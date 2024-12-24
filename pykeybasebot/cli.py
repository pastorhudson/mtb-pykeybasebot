import asyncio
import json
import logging
import shlex

from .kbevent import KbEvent

DEFAULT_TIMEOUT_MS = 10000


class KeybaseNotConnectedError(Exception):
    pass


async def kblisten(keybase_cli: str, options,
                   loop=None):  # loop parameter kept for backwards compatibility but not used
    command = shlex.split(keybase_cli) + ["chat", "api-listen"]
    if options.get("local"):
        command.append("--local")
    if options.get("hide-exploding"):
        command.append("--hide-exploding")
    if options.get("convs"):
        command.append("--convs")
    if options.get("dev"):
        command.append("--dev")
    if options.get("wallet"):
        command.append("--wallet")
    if options.get("filter-channel"):
        command.append("--filter-channel")
        command.append(json.dumps(options["filter-channel"]))
    if options.get("filter-channels"):
        command.append("--filter-channels")
        command.append(json.dumps(options["filter-channels"]))

    logging.debug(f"executing command: {command}")
    process = None
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        while True:
            if not process.stdout:
                raise Exception("Process not initialized correctly")
            line = await process.stdout.readline()
            if not line:
                raise KeybaseNotConnectedError(
                    "the keybase service is probably not running"
                )
            decoded_line = line.decode().strip()
            try:
                yield KbEvent.from_json(decoded_line)
            except json.decoder.JSONDecodeError:
                logging.error(f"Unable to decode JSON output: {line}")
                pass
    finally:
        if process:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()  # Force kill if terminate doesn't work
            except Exception as e:
                logging.error(f"Error during process cleanup: {e}")
            await asyncio.sleep(0)  # Allow event loop to clean up


async def kbsubmit(
        keybase_cli: str, command: str, input_data=None, timeout_ms=None, **kwargs
):
    # Remove loop parameter if present in kwargs
    kwargs = {k: v for k, v in kwargs.items() if k != 'loop'}

    cmd_list = shlex.split(keybase_cli) + shlex.split(command)
    process = None
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd_list,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs
        )

        effective_timeout = timeout_ms / 1000.0 if timeout_ms else DEFAULT_TIMEOUT_MS / 1000.0
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input_data),
            effective_timeout
        )

        if process.returncode != 0:
            logging.error(f"[{command!r} exited with {process.returncode}]")
            logging.error(stderr.decode())

        response = stdout.decode("utf-8")
        try:
            parsed_response = json.loads(response)
            if "error" in parsed_response:
                raise Exception(parsed_response["error"])
            return parsed_response
        except json.decoder.JSONDecodeError:
            return response
    finally:
        if process and process.returncode is None:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()
            except Exception as e:
                logging.error(f"Error during process cleanup: {e}")
        await asyncio.sleep(0)  # Allow event loop to clean up