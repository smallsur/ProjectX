from yacs.config import CfgNode

from utils import is_exist, Log

_ROOT = CfgNode()

def get_cfg(log=None, path_to_config: str = None) -> CfgNode:
    cfg = _ROOT.clone()
    cfg.set_new_allowed(True)
    if path_to_config is not None and is_exist(path_to_config):
        cfg.merge_from_file(path_to_config)

    if not cfg.useLogging:
        print("log shutdown")
        log.shutdown()

    return cfg.clone()

cfg = get_cfg(Log, 'resource/config.yaml')

__all__ = ['cfg', ]
