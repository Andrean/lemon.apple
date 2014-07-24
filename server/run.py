__author__ = 'Andrean'

import core
import modules.storage

if __name__ == "__main__":
    c = core.Core()
    storage = modules.storage.Storage(c)
    print("Starting server")
    print(core.Instance)