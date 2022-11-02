import argparse
import asyncio
import time
from utils import Log
from config import get_cfg

def pro():
    for i in range(9):
        yield i


def test():
    k = yield from pro()
    print(k)


loop = asyncio.get_event_loop()
if __name__ == "__main__":
    # paser = argparse.ArgumentParser()
    # paser.add_argument("--cfg_file_path", type=str, default="resource/config.yaml")

    # args = paser.parse_args()
    # # 注册
    # Log.init_log(args.cfg_file_path)

    # cfg = get_cfg(log=Log, path_to_config=args.cfg_file_path)
    # one = test(1, "wen")
    # two = test(2, "wen")
    # asyncio.run([one, two])
    # loop.run_until_complete(test())
    test()
    print("wen")