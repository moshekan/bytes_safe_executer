from venv import EnvBuilder
import os


class SafePythonEnvironment:
    def __init__(self, env_path: str):
        self._env_path = env_path

    def create(self):
        # AppArmor dose not support symlinks well.
        env = EnvBuilder(symlinks=False)
        env.create(self._env_path)

    @property
    def executable_path(self):
        return os.path.join(self._env_path, "bin", "python")
