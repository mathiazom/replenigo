# replenigo

[![PyPI](https://img.shields.io/pypi/v/replenigo)](https://pypi.org/project/replenigo/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/replenigo)
[![PyPI - License](https://img.shields.io/pypi/l/replenigo)](https://github.com/mathiazom/replenigo/blob/main/LICENSE)

Script that utilizes Sbanken's Open Banking API to refill accounts to specified balances

## Usage

> I recommend you to check out Sbanken's [developer portal](https://sbanken.no/bruke/utviklerportalen/) and read the [documentation](https://github.com/Sbanken/api-examples#swagger) for the Sbanken API before using this app

1. Retrieve credentials required to use the API at https://sbanken.no/bruke/utviklerportalen/

2. Install `replenigo`
```shell
pip install replenigo
```

3. Use [`replenigo.template.yaml`](replenigo.template.yaml) to create your own `replenigo.yaml` config file with required credentials, source account and refill parameters. Some defaults are provide (see [`replenigo.defaults.yml`](replenigo/replenigo.defaults.yaml)), if not specified in `replenigo.yaml`.
4. See below for use of the `replenigo` CLI

# `replenigo`

Script that utilizes Sbanken's Open Banking API to refill accounts to specified balances

**Usage**:

```console
$ replenigo [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `refill`: Refill accounts to specified balances

## `replenigo refill`

Refill accounts to specified balances

**Usage**:

```console
$ replenigo refill [OPTIONS]
```

**Options**:

* `-c, --config-file FILENAME`: Configurations file  [default: replenigo.yaml]
* `-r, --reverse-if-above-goal / -R, --no-reverse-if-above-goal`: If refill goal has been exceeded, decide if the surplus should be transferred back to the source account
* `-m, --transfer-message TEXT`: Message to be displayed in the bank transfer (max 30 chars)
* `-p, --write-checkpoints / -P, --no-checkpoints`: Enable or disable "checkpointing", which creates an empty checkpoint file on each successful refill
* `-d, --checkpoints-dir DIRECTORY`: Directory to store checkpoint files
* `--help`: Show this message and exit.
