import os
import subprocess
from typing import Annotated
from base.logger import log, log_shell
import typer
from trogon import Trogon
from rich import traceback
from base.config import config
from base.payload import payloads
from base.rpc_server import do_init_handlers, do_run_server, do_connect, loop_block
from base.util import ensure_dir, ensure_no_file

app = typer.Typer(no_args_is_help=True)  # type: ignore


@app.command()
def gen(
    path: str = "payloads",
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Only output commands, don't invoke msfvenom."),
    ] = False,
):
    """
    Generate payloads.
    """
    ensure_dir(path)
    for payload in payloads:
        payload_path = path + "/" + payload.filename_first_stage
        log("Generating payload: " + payload.name + " to " + payload_path)
        command = [config.bin.msfvenom] + payload.command_args
        log_shell(" ".join(command))
        if not dry_run:
            subprocess.run(command, check=True)
            ensure_no_file(payload_path)
            os.rename(payload.filename_first_stage, payload_path)
        log()


@app.command()
def serve(
    run_server: Annotated[
        bool,
        typer.Option("--run-server/--no-run-server", help="Run msfrpcd on startup."),
    ] = config.msf.run_server_on_startup,
):
    if run_server:
        do_run_server()
    do_connect()
    do_init_handlers()
    loop_block()


@app.command()
def tui(ctx: typer.Context):
    Trogon(typer.main.get_group(app), click_context=ctx).run()


if __name__ == "__main__":
    traceback.install()
    app()
