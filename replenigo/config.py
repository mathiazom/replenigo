from typing import Optional

import typing
import yaml

from replenigo.definitions import APP_ROOT

DEFAULT_CONFIG_PATH = APP_ROOT / "replenigo.defaults.yaml"


def config_from_stream(s: typing.Any) -> Optional[dict]:
    """Create config dict from YAML config file"""
    with open(DEFAULT_CONFIG_PATH) as file:
        try:
            default_config = yaml.safe_load(file)
            return default_config | yaml.safe_load(s)
        except yaml.YAMLError as exc:
            print(f"[FAIL] Error while loading YAML config: {exc}")
