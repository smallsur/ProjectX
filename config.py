from yacs.config import CfgNode

from utils import is_exist

_ROOT = CfgNode()


def get_cfg(log=None, path_to_config: str = None, check_functions: dict = {}) -> CfgNode:
    cfg = _ROOT.clone()
    cfg.set_new_allowed(True)
    if path_to_config is not None and is_exist(path_to_config):
        cfg.merge_from_file(path_to_config)

    if not cfg.useLogging:
        print("log shutdown")
        log.shutdown()

    for name, func in check_functions.items():
        log.logInfo(0, "running checking: %s" % name)
        func(cfg)

    return cfg.clone()
