from fvcore.common.config import CfgNode

from utils import is_exist

_ROOT = CfgNode()


def get_cfg(path_to_config: str = None, check_functions: dict = {}) -> CfgNode:
    cfg = _ROOT.clone()

    if path_to_config is not None and is_exist(path_to_config):
        cfg.merge_from_file(path_to_config)

    for name, func in check_functions.items():
        func(cfg)

    return _ROOT.clone()
