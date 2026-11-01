#!/usr/bin/env python3
"""Exercise the complete production deletion header with non-raising elements."""
import os
import pathlib
import subprocess
import tempfile
root=pathlib.Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as directory:
    binary=pathlib.Path(directory)/'delete2d'
    command=['g++','-std=c++03','-fno-exceptions','-pedantic','-Wall','-Wextra','-Werror',
             '-I',str(root/'CvGameCoreDLL'),str(pathlib.Path(__file__).with_suffix('.cpp')),'-o',str(binary)]
    if os.environ.get('DELETE2D_SANITIZE'):
        command[1:1]=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    subprocess.run(command,check=True)
    subprocess.run([str(binary)],check=True)
