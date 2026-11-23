"""Extract attachment text in a process the protocol request can stop."""

import asyncio
import os
import signal
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from anyio import CancelScope, fail_after


ATTACHMENT_TIMEOUT = 15
_EXTRACTOR = Path(__file__).with_name("file_preview.py")


async def _stop_extractor(process):
    with CancelScope(shield=True):
        if sys.platform == "win32":
            if process.returncode is None:
                taskkill = Path(os.environ["SystemRoot"]) / "System32" / "taskkill.exe"
                try:
                    cleanup = await asyncio.create_subprocess_exec(
                        str(taskkill), "/PID", str(process.pid), "/T", "/F",
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                    await cleanup.wait()
                except OSError:
                    pass
                if process.returncode is None:
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        await process.wait()


async def extract_protocol_attachment(path, name, content_type, max_chars):
    with TemporaryDirectory(prefix="protocol-attachment-") as directory:
        output = Path(directory) / "text.txt"
        options = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {"start_new_session": True}
        with CancelScope(shield=True):
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-B", str(_EXTRACTOR),
                path, name, content_type or "", str(output), str(max_chars),
                env={**os.environ, "TEMP": directory, "TMP": directory, "TMPDIR": directory},
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **options,
            )
        try:
            with fail_after(ATTACHMENT_TIMEOUT):
                if await process.wait() != 0:
                    raise OSError("Attachment extraction failed")
            return output.read_text(encoding="utf-8")
        finally:
            if process.returncode is None:
                await _stop_extractor(process)
