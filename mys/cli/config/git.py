from contextlib import suppress
import subprocess


class GitConfig(dict):
    def get(self, key, default=None):
        rv = super().get(key, default)
        with suppress(Exception):
            rv = subprocess.check_output(['git', 'config', '--get', key])
        self[key] = rv
        return rv
