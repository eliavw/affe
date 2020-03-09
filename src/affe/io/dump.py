import os
import json
import dill as pkl
import pandas as pd
import joblib


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


def dump_object(o, fn):
    actions = dict(pkl=_dump_pkl, json=_dump_json, csv=_dump_csv, lz4=_dump_lz4)

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
