from pathlib import Path
from dataclasses import dataclass
import tomllib
from typing import Union, Optional, List
import dacite
from mergedeep import merge


@dataclass
class ServerConfig:
    host: str


@dataclass
class MsfConfig:
    host: str
    port: int
    username: str
    password: str
    force_ssl: bool = True
    run_server_on_startup: bool = True
    run_server_on_startup_wait_time: int = 20


@dataclass
class LogConfig:
    path: Optional[str] = None
    stdout: bool = True


@dataclass
class AppConfig:
    check_interval: int = 10


@dataclass
class ExecutableConfig:
    msfvenom: str = "msfvenom"
    msfrpcd: str = "msfrpcd"


@dataclass
class Config:
    server: ServerConfig
    msf: MsfConfig
    log: LogConfig
    app: AppConfig
    bin: ExecutableConfig


config_path = Path("./config.toml")
override_path = Path("./config.override.toml")
with open(config_path, "rb") as f:
    config_data = tomllib.load(f)
if override_path.is_file():
    with open(override_path, "rb") as f:
        config_override_data = tomllib.load(f)
    merge(config_data, config_override_data)

config: Config = dacite.from_dict(data_class=Config, data=config_data)
