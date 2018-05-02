import os
import collections
import subprocess


class DirDict(collections.MutableMapping):
    def __init__(self, dir_path):
        self._dir_path = dir_path

    def __len__(self):
        return len(os.listdir(path=self._dir_path))

    def __setitem__(self, key, value):
        with open(os.path.join(self._dir_path, str(key)), 'w') as f:
            f.write(str(value))

    def __getitem__(self, key):
        if str(key) not in os.listdir(path=self._dir_path):
            raise KeyError(str(key))
        with open(os.path.join(self._dir_path, str(key)), 'r') as f:
            return f.read()

    def __delitem__(self, key):
        if str(key) not in os.listdir(path=self._dir_path):
            raise KeyError(str(key))
        subprocess.call(['rm', os.path.join(self._dir_path, str(key))])

    def __iter__(self):
        return iter(os.listdir(path=self._dir_path))

    def __bool__(self):
        return self.__len__() > 0
