from typing import TypedDict
from base.rpc_server import do_command, do_connect, do_init_handlers, sessions

do_connect()
if True:
    do_init_handlers()
from base.rpc_server import client, console

# new thread for print console output
import threading
import time

current_prompt = ""


class ConsoleOutput(TypedDict):
    data: str
    prompt: str
    busy: bool


def single_print_console() -> ConsoleOutput:
    global current_prompt
    r: ConsoleOutput = console.read()
    current_prompt = r["prompt"]
    print(r["data"], end="")
    return r


def print_console():
    while True:
        r = single_print_console()
        if not r["busy"]:
            pass
        time.sleep(0.1)


def async_do_command(command: str):
    thread = threading.Thread(
        target=do_command, args=(command,), kwargs=dict(wait_idle=False), daemon=True
    )
    thread.start()


threading.Thread(target=print_console, daemon=True).start()

while True:
    try:
        user_command = input(current_prompt)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        exit(1)
    if user_command in ["quit", "exit"]:
        exit(0)
    if user_command:
        async_do_command(user_command)
    time.sleep(0.05)
