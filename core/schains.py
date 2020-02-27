import logging
from itertools import chain

from collections import namedtuple
from skale.dataclasses.skaled_ports import SkaledPorts


import iptc

logger = logging.getLogger(__name__)

TABLE = 'filter'
CHAIN = 'INPUT'
BASE_RULE_D = {
    'protocol': 'tcp',
    'target': 'ACCEPT'
}


NodeEndpoint = namedtuple('NodeEndpoint', ['ip', 'port'])


def get_skaled_rpc_endpoints_from_config(config):
    node_info = config["skaleConfig"]["nodeInfo"]
    return [
        NodeEndpoint(ip=None, port=node_info['httpRpcPort']),
        NodeEndpoint(ip=None, port=node_info['wsRpcPort']),
        NodeEndpoint(ip=None, port=node_info['httpsRpcPort']),
        NodeEndpoint(ip=None, port=node_info['wssRpcPort'])
    ]


def get_snapshots_endpoints_from_config(config):
    # TODO: Add this endpoints
    return []


def get_consensus_endpoints_from_config(config):
    node_id = config['skaleConfig']['nodeInfo']['nodeID']
    base_port = config['skaleConfig']['nodeInfo']['basePort']
    schain_nodes_config = config['skaleConfig']['sChain']['nodes']

    node_endpoints = list(chain.from_iterable(
        (
            NodeEndpoint(node_data['ip'], base_port + SkaledPorts.PROPOSAL.value),
            NodeEndpoint(node_data['ip'], base_port + SkaledPorts.CATCHUP.value),
            NodeEndpoint(
                node_data['ip'], base_port + SkaledPorts.BINARY_CONSENSUS.value
            ),
            NodeEndpoint(
                node_data['ip'], base_port + SkaledPorts.ZMQ_BROADCAST.value
            )
        )
        for node_data in schain_nodes_config
        if node_data['nodeID'] != node_id
    ))
    return node_endpoints


def get_allowed_endpoints(config):
    return [
        *get_consensus_endpoints_from_config(config),
        *get_skaled_rpc_endpoints_from_config(config),
        *get_snapshots_endpoints_from_config(config)
    ]


def rule_d_from_endpoint(endpoint):
    rule_d = BASE_RULE_D.copy()
    if endpoint.ip is not None:
        rule_d['src'] = str(endpoint.ip)
    if endpoint.port is not None:
        rule_d['tcp'] = {'dport': str(endpoint.port)}
    return rule_d


def get_added_allowed_endpoints(endpoints):
    rules = []
    for endpoint in endpoints:
        rule_d = rule_d_from_endpoint(endpoint)
        if iptc.easy.has_rule(TABLE, CHAIN, rule_d):
            rules.append((endpoint.ip, endpoint.port))
    return rules


def add_rules(endpoints):
    logger.info('Adding iptables rules')
    for endpoint in endpoints:
        rule_d = rule_d_from_endpoint(endpoint)
        if not iptc.easy.has_rule(TABLE, CHAIN, rule_d):
            iptc.easy.insert_rule(TABLE, CHAIN, rule_d)


def remove_rules(endpoints):
    logger.info('Removing iptables rules')
    for endpoint in endpoints:
        rule_d = rule_d_from_endpoint(endpoint)
        if iptc.easy.has_rule(TABLE, CHAIN, rule_d):
            iptc.easy.delete_rule(TABLE, CHAIN, rule_d)


def add_rules_from_schain_config(config):
    endpoints = get_allowed_endpoints(config)
    add_rules(endpoints)


def remove_schain_config_rules(config):
    endpoints = get_allowed_endpoints(config)
    remove_rules(endpoints)


def get_added_endpoints_from_schain_config(config):
    endpoints = get_allowed_endpoints(config)
    return get_added_allowed_endpoints(endpoints)
