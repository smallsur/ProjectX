import os


def is_exist(dir_: str) -> bool:
    if os.path.exists(dir_):
        return True

    return False
