import argparse
from utils import Log
from config import get_cfg

if __name__ == "__main__":
    paser = argparse.ArgumentParser()
    paser.add_argument("--cfg_file_path", type=str, default="resource/config.yaml")

    args = paser.parse_args()
    # 注册
    Log.init_log(args.cfg_file_path)

    cfg = get_cfg(log=Log, path_to_config=args.cfg_file_path)
