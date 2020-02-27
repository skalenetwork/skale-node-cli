#   -*- coding: utf-8 -*-
#
#   This file is part of skale-node-cli
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json

import click
import pprint
from core.helper import get
from core.schains import (add_rules_from_schain_config, remove_schain_config_rules,
                          get_added_endpoints_from_schain_config)

from core.print_formatters import print_schains, print_dkg_statuses


@click.group()
def schains_cli():
    pass


@schains_cli.group('schains', help="Node sChains commands")
def schains():
    pass


@schains.command(help="List of sChains served by connected node")
def ls():
    schains_list = get('node_schains')
    if not schains_list:
        print('No sChains found')
        return
    print_schains(schains_list)


@schains.command(help="DKG statuses for each sChain on the node")
def dkg():
    dkg_statuses = get('dkg_statuses')
    if not dkg_statuses:
        return
    print_dkg_statuses(dkg_statuses)


@schains.command('config', help="sChain config")
@click.argument('schain_name')
def get_schain_config(schain_name):
    schain_config = get('schain_config', {'schain-name': schain_name})
    if not schain_config:
        return
    pprint.pprint(schain_config)


@schains.command('add-rules', help="Add iptables rules related to specified schain")
@click.option('--schain-name', default=None)
@click.option('--config-path', default=None)
def add_iptables_rules(schain_name, config_path):
    if schain_name is not None:
        schain_config = get('schain_config', {'schain-name': schain_name})
    elif config_path is not None:
        with open(config_path) as schain_config_file:
            schain_config = json.load(schain_config_file)
    else:
        print('You should provide schain name or path to schain config file')
        return

    print(schain_config)
    add_rules_from_schain_config(schain_config)
    print(f'Rules for schain {schain_name} was successfully added')


@schains.command('remove-rules', help="Remove iptables rules related to specified schain")
@click.option('--schain-name', default=None)
@click.option('--config-path', default=None)
def remove_iptables_rules(schain_name, config_path):
    if schain_name is not None:
        schain_config = get('schain_config', {'schain-name': schain_name})
    elif config_path is not None:
        with open(config_path) as schain_config_file:
            schain_config = json.load(schain_config_file)
    else:
        print('You should provide schain name or path to schain config file')
        return

    remove_schain_config_rules(schain_config)
    print(f'Rules for schain {schain_name} was successfully removed')


@schains.command('show-rules', help="Remove iptables rules related to the specified schain")
@click.option('--schain-name', default=None)
@click.option('--config-path', default=None)
def show_iptables_rules(schain_name, config_path):
    if schain_name is not None:
        schain_config = get('schain_config', {'schain-name': schain_name})
    elif config_path is not None:
        with open(config_path) as schain_config_file:
            schain_config = json.load(schain_config_file)
    else:
        print('You should provide schain name or path to schain config file')
        return

    print(get_added_endpoints_from_schain_config(schain_config))
