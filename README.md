# Node CLI

![Build and publish](https://github.com/skalenetwork/node-cli/workflows/Build%20and%20publish/badge.svg)
![Test](https://github.com/skalenetwork/node-cli/workflows/Test/badge.svg)
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

SKALE Node CLI, part of the SKALE suite of validator tools, is the command line to setup, register and maintain your SKALE node.

## Table of Contents

1.  [Installation](#installation)
2.  [CLI usage](#cli-usage)
    2.1 [Top level commands](#top-level-commands)
    2.2 [User](#user-commands)
    2.3 [Node](#node-commands)
    2.4 [Wallet](#wallet-commands)
    2.5 [sChains](#schain-commands)
    2.6 [Containers](#containers-commands)
    2.7 [SGX](#sgx-commands)
    2.8 [SSL](#ssl-commands)
    2.9 [Logs](#logs-commands)
3.  [Development](#development)

## Installation

-   Prerequisites

Ensure that the following package is installed: **docker**, **docker-compose** (1.27.4+)

-   Download the executable

```bash
VERSION_NUM={put the version number here} && sudo -E bash -c "curl -L https://github.com/skalenetwork/node-cli/releases/download/$VERSION_NUM/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
```

For versions `<1.1.0`:

```bash
VERSION_NUM=0.0.0 && sudo -E bash -c "curl -L https://skale-cli.sfo2.cdn.digitaloceanspaces.com/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
```

-   Apply executable permissions to the downloaded binary:

```bash
chmod +x /usr/local/bin/skale
```

-   Test the installation

```bash
skale --help
```

## CLI usage

### Top level commands

#### Info

Print build info

```bash
skale info
```

#### Version

Print version number

```bash
skale version
```

Options:

-   `--short` - prints version only, without additional text.

### Node commands

> Prefix: `skale node`

#### Node initialization

Initialize a SKALE node on current machine

```bash
skale node init [ENV_FILE]
```

Arguments:

- `ENV_FILE` - path to .env file (required parameters are listed in the `skale init` command)

Required options:

-   `--dry-run` - create only needed files and directories and don't create containers

You should also specify the following environment variables:

-   `SGX_SERVER_URL` - SGX server URL
-   `DISK_MOUNTPOINT` - disk mount point for storing sChains data
-   `DOCKER_LVMPY_STREAM` - stream of `docker-lvmpy` to use
-   `CONTAINER_CONFIGS_STREAM` - stream of `skale-node` to use
-   `IMA_ENDPOINT` - IMA endpoint to connect
-   `ENDPOINT` - RPC endpoint of the node in the network where SKALE Manager is deployed
-   `MANAGER_CONTRACTS_ABI_URL` - URL to SKALE Manager contracts ABI and addresses
-   `IMA_CONTRACTS_ABI_URL` - URL to IMA contracts ABI and addresses
-   `FILEBEAT_URL` - URL to the Filebeat log server
-   `DB_USER`'  - MySQL user for local node database
-   `DB_PASSWORD` - Password for root user of node internal database
      (equal to user password by default)
-   `DB_PORT` - Port for node internal database (default is `3306`)

Optional variables:

-   `TG_API_KEY` - Telegram API key
-   `TG_CHAT_ID` - Telegram chat ID
-   `MONITORING_CONTAINERS` - will enable monitoring containers (`filebeat`, `cadvisor`, `prometheus`)

#### Node initialization from backup

Restore SKALE node on another machine

```bash
skale node restore [BACKUP_PATH] [ENV_FILE]
```

Arguments:

- `BACKUP_PATH` - path to the archive with backup data generated by `skale node backup` command
- `ENV_FILE` - path to .env file (required parameters are listed in the `skale init` command)

#### Node backup

Generate backup file to restore SKALE node on another machine

```bash
skale node backup [BACKUP_FOLDER_PATH] [ENV_FILE]
```

Arguments:

- `BACKUP_FOLDER_PATH` - path to the folder where the backup file will be saved
- `ENV_FILE` - path to .env file (required parameters are listed in the `skale init` command)
`

Optional arguments:

-   `--no-database` - skip mysql database backup (in case if mysql container is not started)

#### Node Registration

```bash
skale node register
```

Required arguments:

-   `--ip` - public IP for RPC connections and consensus

Optional arguments:

-   `--name` - SKALE node name
-   `--port` - public port - beginning of the port range for node SKALE Chains (default: `10000`)

#### Node information

Get base info about SKALE node

```bash
skale node info
```

Options:

`-f/--format json/text` - optional

#### Node update

Update SKALE node on current machine

```bash
skale node update [ENV_FILEPATH]
```

Options:

-   `--sync-schains` - run sChains in the backup recovery mode after restart
-   `--yes` - remove without additional confirmation

Arguments:

- `ENV_FILEPATH` - path to env file where parameters are defined

You can also specify a file with environment variables
which will update parameters in env file used during skale node init.

#### Node turn-off

Turn-off SKALE node on current machine and optionally set it to the maintenance mode

```bash
skale node turn-off
```

Options:

-   `--maintenance-on` - set SKALE node into maintenance mode before turning off
-   `--yes` - remove without additional confirmation

#### Node turn-on

Turn on SKALE node on current machine and optionally disable maintenance mode

```bash
skale node turn-on [ENV_FILEPATH]
```

Options:

-   `--maintenance-off` - turn off maintenance mode after turning on the node
-   `--sync-schains` - run sChains in the backup recovery mode after restart
-   `--yes` - remove without additional confirmation

Arguments:

- `ENV_FILEPATH` - path to env file where parameters are defined

You can also specify a file with environment variables
which will update parameters in env file used during skale node init.

#### Node maintenance

Set SKALE node into maintenance mode

```bash
skale node maintenance-on
```

Options:

-   `--yes` - set without additional confirmation

Switch off maintenance mode

```bash
skale node maintenance-off
```

### Wallet commands

> Prefix: `skale wallet`

Commands related to Ethereum wallet associated with SKALE node

#### Wallet information

```bash
skale wallet info
```

Options:

`-f/--format json/text` - optional

#### Wallet setting

Set local wallet for the SKALE node

```bash
skale wallet set --private-key $ETH_PRIVATE_KEY
```

#### Send ETH tokens

Send ETH tokens from SKALE node wallet to specific address

```bash
skale wallet send [ADDRESS] [AMOUNT]
```

Arguments:

-   `ADDRESS` - Ethereum receiver address
-   `AMOUNT` - Amount of ETH tokens to send

Optional arguments:

`--yes` - Send without additional confirmation

### SKALE Chain commands

> Prefix: `skale schains`

#### SKALE Chain list

List of SKALE Chains served by connected node

```bash
skale schains ls
```

#### SKALE Chain configuration

```bash
skale schains config SCHAIN_NAME
```

#### SKALE Chain DKG status

List DKG status for each SKALE Chain on the node

```bash
skale schains dkg
```

#### SKALE Chain info

Show information about SKALE Chain on node
```bash
skale schains info SCHAIN_NAME
```

Options:

-   `--json` - Show info in JSON format

#### SKALE Chain repair

Turn on repair mode for SKALE Chain

```bash
skale schains repair SCHAIN_NAME
```

#### SKALE Chain healthcheck

Show healthcheck results for all SKALE Chains on the node

```bash
skale schains checks
```

Options:

-   `--json` - Show data in JSON format

### Container commands

Node container commands

> Prefix: `skale containers`

#### List containers

List all SKALE containers running on the connected node

```bash
skale containers ls
```

Options:

-   `-a/--all` - list all containers (by default - only running)

#### SKALE Chain containers

List of SKALE chain containers running on the connected node

```bash
skale containers schains
```

Options:

-   `-a/--all` - list all SKALE chain containers (by default - only running)

### SGX commands

> Prefix: `skale sgx`

#### Status

Status of the SGX server. Returns the SGX server URL and connection status.

```bash
$ skale sgx status

SGX server status:
┌────────────────┬────────────────────────────┐
│ SGX server URL │ https://0.0.0.0:1026/      │
├────────────────┼────────────────────────────┤
│ Status         │ CONNECTED                  │
└────────────────┴────────────────────────────┘
```

Admin API URL: \[GET] `/api/ssl/sgx`

### SSL commands

> Prefix: `skale ssl`

#### SSL Status

Status of the SSL certificates on the node

```bash
skale ssl status
```

Admin API URL: \[GET] `/api/ssl/status`

#### Upload certificates

Upload new SSL certificates

```bash
skale ssl upload
```

##### Options

-   `-c/--cert-path` - Path to the certificate file
-   `-k/--key-path` - Path to the key file
-   `-f/--force` - Overwrite existing certificates

Admin API URL: \[GET] `/api/ssl/upload`

### Logs commands

> Prefix: `skale logs`

#### CLI Logs

Fetch node CLI logs:

```bash
skale logs cli
```

Options:

-   `--debug` - show debug logs; more detailed output

#### Dump Logs

Dump all logs from the connected node:

```bash
skale logs dump [PATH]
```

Optional arguments:

-   `--container`, `-c` - Dump logs only from specified container


### Resources allocation commands

> Prefix: `skale resources-allocation`

#### Show allocation file

Show resources allocation file:

```bash
skale resources-allocation show
```
#### Generate/update

Generate/update allocation file:

```bash
skale resources-allocation generate
```

Options:

-   `--yes` - generate without additional confirmation

## Development

### Setup repo

#### Install development dependencies

```bash
pip install -e .[dev]
```

##### Add flake8 git hook

In file `.git/hooks/pre-commit` add:

```bash
#!/bin/sh
flake8 .
```

### Debugging

Run commands in dev mode:

```bash
ENV=dev python main.py YOUR_COMMAND
```

### Setting up Travis

Required environment variables:

-   `ACCESS_KEY_ID` - DO Spaces/AWS S3 API Key ID
-   `SECRET_ACCESS_KEY` - DO Spaces/AWS S3 Secret access key
-   `GITHUB_EMAIL` - Email of GitHub user
-   `GITHUB_OAUTH_TOKEN` - GitHub auth token

## Contributing

**If you have any questions please ask our development community on [Discord](https://discord.gg/vvUtWJB).**

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## License

[![License](https://img.shields.io/github/license/skalenetwork/node-cli.svg)](LICENSE)

Copyright (C) 2018-present SKALE Labs
