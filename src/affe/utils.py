import pandas as pd

from .io.CTE import KEYCHAIN_SEPARATOR

VERBOSITY = 1


def flatten_dict(d, separator=KEYCHAIN_SEPARATOR):
    return pd.json_normalize(d, sep=separator).to_dict(orient="records").pop()


def keychain(*args, separator=KEYCHAIN_SEPARATOR):
    return separator.join(args)


def debug_print(msg, level=1, V=VERBOSITY, **kwargs):
    if V >= level:
        print(msg + "\n")
    return
