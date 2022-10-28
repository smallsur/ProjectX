import os


def is_exist(dir_: str) -> bool:
    if os.path.exists(dir_):
        return True

    return False


def is_exist_file(file_: str) -> bool:
    if os.path.isfile(file_):
        return True

    return False
