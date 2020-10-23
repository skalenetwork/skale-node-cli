#   -*- coding: utf-8 -*-
#
#   This file is part of node-cli
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

import ipaddress
from urllib.parse import urlparse

import click

from core.core import get_node_info, get_node_about
from core.node import (get_node_signature, init, restore,
                       register_node as register, update, backup,
                       set_maintenance_mode_on, set_maintenance_mode_off, turn_off, turn_on)
from core.host import install_host_dependencies
from core.helper import abort_if_false, safe_load_texts
from configs import DEFAULT_NODE_BASE_PORT
from tools.helper import session_config


config = session_config()
TEXTS = safe_load_texts()


class UrlType(click.ParamType):
    name = 'url'

    def convert(self, value, param, ctx):
        try:
            result = urlparse(value)
        except ValueError:
            self.fail(f'Some characters are not allowed in {value}',
                      param, ctx)
        if not all([result.scheme, result.netloc]):
            self.fail(f'Expected valid url. Got {value}', param, ctx)
        return value


class IpType(click.ParamType):
    name = 'ip'

    def convert(self, value, param, ctx):
        try:
            ipaddress.ip_address(value)
        except ValueError:
            self.fail(f'expected valid ipv4/ipv6 address. Got {value}',
                      param, ctx)
        return value


URL_TYPE = UrlType()
IP_TYPE = IpType()


@click.group()
def node_cli():
    pass


@node_cli.group(help="SKALE node commands")
def node():
    pass


@node.command('info', help="Get info about SKALE node")
@click.option('--format', '-f', type=click.Choice(['json', 'text']))
def node_info(format):
    config = session_config()
    get_node_info(config, format)


@node.command('about', help="Get service info about SKALE node")
@click.option('--format', '-f', type=click.Choice(['json', 'text']))
def node_about(format):
    config = session_config()
    get_node_about(config, format)


@node.command('register', help="Register current node in the SKALE Manager")
@click.option(
    '--name', '-n',
    help='SKALE node name'
)
@click.option(
    '--ip',
    prompt="Enter node public IP",
    type=IP_TYPE,
    help='Public IP for RPC connections & consensus (required)'
)
@click.option(
    '--port', '-p',
    default=DEFAULT_NODE_BASE_PORT,
    type=int,
    help='Base port for node sChains'
)
def register_node(name, ip, port):
    config = session_config()
    register(config, name, ip, ip, port)


@node.command('init', help="Initialize SKALE node")
@click.argument('env_file')
@click.option(
    '--install-deps',
    is_flag=True,
    help='Install host dependencies'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help="Dry run node init (don't setup containers)"
)
def init_node(env_file, install_deps, dry_run):
    if install_deps:
        install_host_dependencies()
    init(env_file, dry_run)


@node.command('update', help='Update node from .env file')
@click.option(
    '--sync-schains',
    help='Run all sChains in the snapshot download mode',
    is_flag=True
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to update SKALE node software?')
@click.argument('env_file')
def update_node(sync_schains, env_file):
    update(env_file, sync_schains)


@node.command('signature', help='Get node signature for given validator id')
@click.argument('validator_id')
def signature(validator_id):
    res = get_node_signature(validator_id)
    print(f'Signature: {res}')


@node.command('backup', help="Generate backup file to restore SKALE node on another machine")
@click.argument('backup_folder_path')
@click.argument('env_file')
def backup_node(backup_folder_path, env_file):
    backup(backup_folder_path, env_file)


@node.command('restore', help="Restore SKALE node on another machine")
@click.argument('backup_path')
@click.argument('env_file')
def restore_node(backup_path, env_file):
    restore(backup_path, env_file)


@node.command('maintenance-on', help="Set SKALE node into maintenance mode")
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to set SKALE node into maintenance mode?')
def set_node_in_maintenance():
    set_maintenance_mode_on()


@node.command('maintenance-off', help="Remove SKALE node from maintenance mode")
def remove_node_from_maintenance():
    set_maintenance_mode_off()


@node.command('turn-off', help='Turn off the node')
@click.option(
    '--maintenance-on',
    help='Set SKALE node into maintenance mode before turning off',
    is_flag=True
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to turn off the node?')
def _turn_off(maintenance_on):
    turn_off(maintenance_on)


@node.command('turn-on', help='Turn on the node')
@click.option(
    '--maintenance-off',
    help='Turn off maintenance mode after turning on the node',
    is_flag=True
)
@click.option(
    '--sync-schains',
    help='Run all sChains in the snapshot download mode',
    is_flag=True
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to turn on the node?')
@click.argument('env_file')
def _turn_on(maintenance_off, sync_schains, env_file):
    turn_on(maintenance_off, sync_schains, env_file)
