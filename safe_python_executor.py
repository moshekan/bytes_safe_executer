from venv import EnvBuilder
from executer import SafeExecutor
import os
from utils import get_temp_dir


class SafePythonEnvironment:
    def __init__(self, read_only_access: list = None, write_exec_access: list = None):
        self._env_path = get_temp_dir()
        super(SafePythonEnvironment, self).__init__()

    def create(self):
        # AppArmor dose not support symlinks well.
        env = EnvBuilder(symlinks=False)
        env.create(self._env_path)

    @property
    def executable_path(self):
        return os.path.join(self._env_path, "bin", "python")
