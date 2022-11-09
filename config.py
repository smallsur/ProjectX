from yacs.config import CfgNode

from utils import is_exist

_ROOT = CfgNode()


def get_cfg(path_to_config: str = None) -> CfgNode:
    cfg_ = _ROOT.clone()
    cfg_.set_new_allowed(True)
    if path_to_config is not None and is_exist(path_to_config):
        cfg_.merge_from_file(path_to_config)

    return cfg_.clone()


cfg = get_cfg('resource/config.yaml')

__all__ = ['cfg', ]
