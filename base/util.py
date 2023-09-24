from pathlib import Path
from typing import Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure the directory exists
    :param path: The directory path
    :return: The directory Path path
    """
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_file(path: Union[str, Path]) -> Path:
    """
    Ensure the file exists
    :param path: The file path
    :return: The file Path object
    """
    if isinstance(path, str):
        path = Path(path)
    ensure_dir(path.parent)
    path.touch(exist_ok=True)
    return path


def ensure_no_file(path: Union[str, Path]) -> Path:
    """
    Ensure the file does not exist
    :param path: The file path
    :return: The file Path object
    """
    if isinstance(path, str):
        path = Path(path)
    if path.is_file():
        path.unlink()
    return path
