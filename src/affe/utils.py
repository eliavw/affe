import pandas as pd

from .io.CTE import KEYCHAIN_SEPARATOR

VERBOSITY = 1


def flatten_dict(d, separator=KEYCHAIN_SEPARATOR):
    return pd.json_normalize(d, sep=separator).to_dict(orient="records").pop()


def keychain(*args, separator=KEYCHAIN_SEPARATOR):
    return separator.join(args)


def debug_print(msg, level=1, V=VERBOSITY, **kwargs):

    """
    def get_var_name(var):
        var_name = [k for k, v in locals().items() if v is var][0]
        return var_name

    if kwargs.keys() > {'msg', 'level', 'V'}:
        print('INSIDE')
        relevant = {k:v for k,v in kwargs.items()
                    if k not in {'msg', 'level', 'V'}}
        for k,v in relevant.items():
            msg+="k: {}".format(v)
    """

    if V >= level:
        print(msg + "\n")
    return
