import os
import json
import dill as pkl
import pandas as pd
import joblib
import toml

# Interface Methods
def save_object(o, fn):
    """Alias for dump object method.
    """
    return dump_object(o, fn)


def dump_object(o, fn):
    actions = dict(
        pkl=_dump_pkl,
        json=_dump_json,
        csv=_dump_csv,
        lz4=_dump_lz4,
        txt=_dump_txt,
        toml=_dump_toml,
    )

    ext = os.path.splitext(fn)[-1].split(".")[-1]
    try:
        return actions.get(ext)(o, fn)
    except Exception as e:
        msg = """
        Possibly; there is no dumping policy regarding extension: {}
        """.format(
            ext
        )
        raise Exception(e, msg)


def load_object(fn):
    actions = dict(pkl=_load_pkl, toml=_load_toml)

    ext = os.path.splitext(fn)[-1].split(".")[-1]
    try:
        return actions.get(ext)(fn)
    except Exception as e:
        msg = """
        Possibly; there is no loading policy regarding extension: {}
        """.format(
            ext
        )
        raise Exception(e, msg)


# Actual loaders/dumpers
def _dump_pkl(o, fn):
    with open(fn, "wb") as f:
        pkl.dump(o, f)
    return True


def _dump_json(o, fn):
    with open(fn, "w") as f:
        json.dump(o, f, indent=4, sort_keys=True)
    return True


def _dump_csv(o, fn):
    if not isinstance(o, pd.core.frame.DataFrame):
        o = pd.DataFrame(o)

    o.to_csv(fn)
    return True


def _dump_lz4(o, fn):
    joblib.dump(o, fn, compress="lz4")
    return True


def _dump_txt(o, fn):
    # Fix object to be a list of strings.
    if isinstance(o, (list, tuple, set)):
        assert isinstance(o[0], str)
    else:
        assert isinstance(o, str)
        o = [o]

    with open(fn, "w") as f:
        f.write("\n".join(o))
    return True


def _dump_toml(o, fn):
    with open(fn, "w") as f:
        toml.dump(o, f)
    return True


def _load_pkl(fn):
    with open(fn, "rb") as f:
        o = pkl.load(f)
    return o


def _load_toml(fn):
    with open(fn, "r") as f:
        o = toml.load(f)
    return o
