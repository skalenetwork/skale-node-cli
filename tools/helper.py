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

import os
import re
import sys
import json
import yaml
import shutil
import requests
import subprocess
import urllib.request
from subprocess import PIPE
from functools import wraps

import logging
from logging import Formatter
import logging.handlers as py_handlers

import click

from jinja2 import Environment
from readsettings import ReadSettings

from core.print_formatters import print_err_response
from tools.exit_codes import CLIExitCodes

from configs.env import (absent_params as absent_env_params,
                         get_params as get_env_params)
from configs import CONFIG_FILEPATH, TEXT_FILE, ADMIN_HOST, ADMIN_PORT
from configs.cli_logger import (LOG_FORMAT, LOG_BACKUP_COUNT,
                                LOG_FILE_SIZE_BYTES,
                                LOG_FILEPATH, DEBUG_LOG_FILEPATH)
from configs.routes import get_route


logger = logging.getLogger(__name__)


HOST = f'http://{ADMIN_HOST}:{ADMIN_PORT}'

DEFAULT_ERROR_DATA = {
    'status': 'error',
    'payload': 'Request failed. Check skale_api container logs'
}


def read_json(path):
    with open(path, encoding='utf-8') as data_file:
        return json.loads(data_file.read())


def write_json(path, content):
    with open(path, 'w') as outfile:
        json.dump(content, outfile, indent=4)


def run_cmd(cmd, env={}, shell=False, secure=False):
    if not secure:
        logger.info(f'Running: {cmd}')
    else:
        logger.info('Running some secure command')
    res = subprocess.run(cmd, shell=shell, stdout=PIPE, stderr=PIPE, env={**env, **os.environ})
    if res.returncode:
        logger.info(res.stdout.decode('UTF-8').rstrip())
        logger.error('Error during shell execution:')
        logger.error(res.stderr.decode('UTF-8').rstrip())
        res.check_returncode()
    else:
        logger.info('Command is executed successfully. Command log:')
        logger.info(res.stdout.decode('UTF-8').rstrip())
    return res


def format_output(res):
    return res.stdout.decode('UTF-8').rstrip(), res.stderr.decode('UTF-8').rstrip()


def download_file(url, filepath):
    return urllib.request.urlretrieve(url, filepath)


def process_template(source, destination, data):
    """
    :param source: j2 template source path
    :param destination: out file path
    :param data: dictionary with fields for template
    :return: Nothing
    """
    template = read_file(source)
    processed_template = Environment().from_string(template).render(data)
    with open(destination, "w") as f:
        f.write(processed_template)


def read_file(path):
    file = open(path, 'r')
    text = file.read()
    file.close()
    return text


def get_username():
    return os.environ.get('USERNAME') or os.environ.get('USER')


def session_config():
    return ReadSettings(CONFIG_FILEPATH)


def extract_env_params(env_filepath):
    env_params = get_env_params(env_filepath)
    if not env_params.get('DB_ROOT_PASSWORD'):
        env_params['DB_ROOT_PASSWORD'] = env_params['DB_PASSWORD']

    absent_params = ', '.join(absent_env_params(env_params))
    if absent_params:
        click.echo(f"Your env file({env_filepath}) have some absent params: "
                   f"{absent_params}.\n"
                   f"You should specify them to make sure that "
                   f"all services are working",
                   err=True)
        return None
    return env_params


def error_exit(error_payload, exit_code=CLIExitCodes.FAILURE):
    print_err_response(error_payload)
    sys.exit(exit_code.value)


def safe_get_config(config, key):
    try:
        return config[key]
    except KeyError as e:
        logger.error(e)
        return None


def no_node(f):
    @wraps(f)
    def inner(*args, **kwargs):
        # todo: check that node is not installed yet!
        return f(*args, **kwargs)

    return inner


def safe_load_texts():
    with open(TEXT_FILE, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def safe_load_yml(filepath):
    with open(filepath, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def construct_url(route):
    return urllib.parse.urljoin(HOST, route)


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def post_request(blueprint, method, json=None, files=None):
    route = get_route(blueprint, method)
    url = construct_url(route)
    try:
        response = requests.post(url, json=json, files=files)
        data = response.json()
    except Exception as err:
        logger.error('Request failed', exc_info=err)
        data = DEFAULT_ERROR_DATA
    status = data['status']
    payload = data['payload']
    return status, payload


def get_request(blueprint, method, params=None):
    route = get_route(blueprint, method)
    url = construct_url(route)
    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as err:
        logger.error('Request failed', exc_info=err)
        data = DEFAULT_ERROR_DATA

    status = data['status']
    payload = data['payload']
    return status, payload


def download_dump(path, container_name=None):
    route = get_route('logs', 'dump')
    url = construct_url(route)
    params = {}
    if container_name:
        params['container_name'] = container_name
    with requests.get(url, params=params, stream=True) as r:
        if r is None:
            return None
        if r.status_code != requests.codes.ok:  # pylint: disable=no-member
            print('Request failed, status code:', r.status_code)
            error_exit(r.json())
            return None
        d = r.headers['Content-Disposition']
        fname_q = re.findall("filename=(.+)", d)[0]
        fname = fname_q.replace('"', '')
        filepath = os.path.join(path, fname)
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return fname


def init_default_logger():
    f_handler = get_file_handler(LOG_FILEPATH, logging.INFO)
    debug_f_handler = get_file_handler(DEBUG_LOG_FILEPATH, logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG, handlers=[
                        f_handler, debug_f_handler])


def get_file_handler(log_filepath, log_level):
    formatter = Formatter(LOG_FORMAT)
    f_handler = py_handlers.RotatingFileHandler(
        log_filepath, maxBytes=LOG_FILE_SIZE_BYTES,
        backupCount=LOG_BACKUP_COUNT)
    f_handler.setFormatter(formatter)
    f_handler.setLevel(log_level)

    return f_handler


def load_ssl_files(key_path, cert_path):
    return {
        'ssl_key': (os.path.basename(key_path),
                    read_file(key_path), 'application/octet-stream'),
        'ssl_cert': (os.path.basename(cert_path),
                     read_file(cert_path), 'application/octet-stream')
    }


def upload_certs(key_path, cert_path, force):
    with open(key_path, 'rb') as key_file, open(cert_path, 'rb') as cert_file:
        files_data = {
            'ssl_key': (os.path.basename(key_path), key_file,
                        'application/octet-stream'),
            'ssl_cert': (os.path.basename(cert_path), cert_file,
                         'application/octet-stream')
        }
        files_data['json'] = (
            None, json.dumps({'force': force}),
            'application/json'
        )
        return post_request(
            blueprint='ssl',
            method='upload',
            files=files_data
        )


def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def validate_abi(abi_filepath: str) -> dict:
    if not os.path.isfile(abi_filepath):
        return {'filepath': abi_filepath,
                'status': 'error',
                'msg': 'No such file'}
    try:
        with open(abi_filepath) as abi_file:
            json.load(abi_file)
    except Exception:
        return {'filepath': abi_filepath, 'status': 'error',
                'msg': 'Failed to load abi file as json'}
    return {'filepath': abi_filepath, 'status': 'ok', 'msg': ''}
