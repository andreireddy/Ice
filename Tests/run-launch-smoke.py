#!/usr/bin/env python3
"""Catch dyld, code-signing and immediate startup failures in packaged apps."""
import pathlib
import subprocess
import sys
import tempfile

app = pathlib.Path(sys.argv[1]).resolve()
with tempfile.TemporaryFile() as log:
    process = subprocess.Popen([str(app / 'Contents/MacOS/Ice')], stdout=log, stderr=log)
    try:
        code = process.wait(timeout=8)
        log.seek(0)
        raise SystemExit(f'App exited during startup ({code}):\n{log.read().decode(errors="replace")}')
    except subprocess.TimeoutExpired:
        print('PASS: packaged app remained alive through startup')
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
