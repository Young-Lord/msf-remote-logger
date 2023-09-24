"""
{'1': {'arch': 'x64',
       'desc': 'Meterpreter',
       'exploit_uuid': 'tr0kzei9',
       'info': 'LAPTOP-PA3TN26V\\86135 @ LAPTOP-PA3TN26V',
       'platform': 'windows',
       'routes': '',
       'session_host': '172.16.102.248',
       'session_port': 56205,
       'target_host': '',
       'tunnel_local': '192.168.1.8:51092',
       'tunnel_peer': '172.16.102.248:56205',
       'type': 'meterpreter',
       'username': 'Administrator',
       'uuid': 'sqsggmig',
       'via_exploit': 'exploit/multi/handler',
       'via_payload': 'payload/windows/x64/meterpreter/reverse_tcp',
       'workspace': ''}}
"""
from typing import Dict, TypeAlias, TypedDict


class SessionDict(TypedDict):
    arch: str
    desc: str
    exploit_uuid: str
    info: str
    platform: str
    routes: str
    session_host: str
    session_port: int
    target_host: str
    tunnel_local: str
    tunnel_peer: str
    type: str
    username: str
    uuid: str
    via_exploit: str
    via_payload: str
    workspace: str


SessionsType: TypeAlias = Dict[str, SessionDict]
