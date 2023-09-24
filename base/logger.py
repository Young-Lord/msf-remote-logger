from functools import wraps
from io import TextIOWrapper
from typing import Optional
from base.config import config

log_file: Optional[TextIOWrapper] = None

if config.log.path:
    log_file = open(config.log.path, "w")


@wraps(print)
def log(*args, **kwargs):
    if config.log.stdout:
        print(*args, **kwargs)
    if config.log.path:
        kwargs_for_file = kwargs.copy()
        global log_file
        assert log_file is not None
        kwargs_for_file.update(file=log_file, flush=True)
        print(*args, **kwargs_for_file)


@wraps(print)
def log_shell(*args, **kwargs):
    args = ["$"] + list(args)
    log(*args, **kwargs)


@wraps(print)
def log_msf(*args, **kwargs):
    args = ["msf>"] + list(args)
    log(*args, **kwargs)
