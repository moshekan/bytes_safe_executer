import subprocess
from apparmor import AppArmorSecProfile, FileSystemRestriction
from utils import copy_files, get_temp_dir
import os
import time


class SafeExecute:
    def __init__(self, executable_path: str, read_only_access: list = None, write_exec_access: list = None):
        self._executable = executable_path
        self._read_only_access = read_only_access or []
        self._write_exec_access = write_exec_access or []
        self._temp_dir = get_temp_dir()
        self._apparmor_profile = AppArmorSecProfile(self._executable)

    def configure(self):
        for path in self._read_only_access:
            self._apparmor_profile.add_fs_restriction(FileSystemRestriction(path, "r", True))
        for path in self._write_exec_access:
            # Dir itself should not have write permissions
            self._apparmor_profile.add_fs_restriction(FileSystemRestriction(path, "rix", False))
            self._apparmor_profile.add_fs_restriction(FileSystemRestriction(path, "wrix", False))
        self._apparmor_profile.write_profile_and_update_app_armor()

    def safe_execute(self, files: list = None, new_files: list = None, argv: list = None, stdin: str = None,
                     timeout: int = 60):
        """
        :param runnable: The main run file. ie, "/sbin/python".
        :param files: List of files to be copied to working directory.
        :param new_files: List of touples (name, bytes) of files to be created.
        :param argv: List of rgs to be passed to the runnable. Usually a name of a file from 'files' or 'new_files'.
        :param stdin: Input (str) to be passed to the created process
        :param timeout: Timeout which the proccess will get terminated after in SECONDS.
        :return: (return_code, stdout, stderr)
        """
        files = files or []
        new_files = new_files or []
        argv = argv or []

        copy_files(files, self._temp_dir)
        for file_name, content in new_files:
            with open(os.path.join(self._temp_dir, file_name), "wb") as f:
                f.write(content)

        command_line = [self._executable]
        command_line.extend(argv)
        if stdin:
            stdin = stdin.encode('utf-8')

        process = subprocess.Popen(
            command_line, cwd=self._temp_dir,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        HungProcessKiller(process, timeout).start()

        stdout, stderr = process.communicate(stdin)
        return process.returncode, stdout, stderr


class HungProcessKiller:
    def __init__(self, process: subprocess.Popen, timeout: int):
        self._process = process
        self._timeout = timeout

    def start(self):
        timeout_start = time.time()
        while time.time() < timeout_start + self._timeout:
            if self._process.poll() is not None:
                # Process Has finished execution
                return
            time.sleep(0.5)

        if self._process.poll() is None:
            self._process.kill()