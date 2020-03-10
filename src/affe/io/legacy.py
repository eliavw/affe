from affe import __version__

__author__ = "Elia vw"
__copyright__ = "Elia vw"
__license__ = "mit"

import os
from os.path import dirname


SEPARATOR = "-"
LABELS = dict(query="q", exp="e", fold="f", experiment="e")

# Generate a standard filesystem. Only in exceptional cases you deviate.
def build_filesystem(root=None, levels_up=2):
    """
    root
    |---config
    |   |---query
    |   |---model
    |
    |---out
        |---$SCRIPT
        |---run_mercs
        |---run_pxs
            |---exp-0001
                |---logs
                |---timings
                |---results
                |---config   
    |
    |---data
        |---raw
            |---datasets-UCI
            |---datasets-starai
                |---datasets
        |---step-01
        |---step-02
    |---cli
        |---main
        |---predict
        |---fit
        |---cli-config
    _
    """

    fs = {}

    if root is None:
        root = os.getcwd()
        for _ in range(levels_up):
            root = dirname(root)
        fs["root"] = root
    else:
        fs["root"] = root

    # Level 01
    level_01 = _default_subdirectories_root_directory()
    for l in level_01:
        fs[l] = [l]

    # Abs
    def abspath(v):
        if v == "root":
            return fs.get("root")
        elif isinstance(v, list):
            return os.path.join(fs.get("root"), *v)
        elif v in fs.keys():
            return os.path.join(fs.get("root"), *fs.get(v))

    fs["abspath"] = abspath

    return fs


def _default_subdirectories_root_directory():
    return ["config", "data", "out", "cli", "models", "scripts"]


def _default_subdirectories_exp_directory():
    return ["results", "timings", "logs", "config", "tmp"]


FILESYSTEM = build_filesystem()


# -------- -------- -------- --------
# LEGACY
# -------- -------- -------- --------
def exp_directory(exp_dname="default", script="manual", fs=None):
    """
    Standard output directory for an experiment.
    """
    directory = {}

    # Root-level
    out_dir = FILESYSTEM["out"] if fs is None else fs["out"]

    directory["script"] = os.path.join(out_dir, script)
    directory["current_exp"] = os.path.join(directory["script"], exp_dname)

    # Subdirectories
    directory["results"] = os.path.join(directory["current_exp"], "results")
    directory["timings"] = os.path.join(directory["current_exp"], "timings")
    directory["logs"] = os.path.join(directory["current_exp"], "logs")
    directory["config"] = os.path.join(directory["current_exp"], "config")
    directory["tmp"] = os.path.join(directory["current_exp"], "tmp")
    return directory


# Filename functions
def original_filename(
    basename, extension="arff", category="UCI", train_or_test="train", fs=None
):

    raw_dir = FILESYSTEM["raw"] if fs is None else fs["raw"]

    if category in {"UCI", "uci"}:
        dn = FILESYSTEM["datasets-UCI"] if fs is None else fs["datasets-UCI"]

        true_path = os.path.join(dn, "{}.{}".format(basename, extension))
    elif category in {"starai"}:
        dn = FILESYSTEM["datasets-starai"] if fs is None else fs["datasets-starai"]
        true_path = os.path.join(
            dn,
            "{}".format(basename),
            "{}.{}.{}".format(basename, train_or_test, extension),
        )
    else:
        raise ValueError("Did not recognize category: {}".format(category))

    return true_path


def filename_dataset(
    basename,
    step=1,
    prefix="",
    suffix="",
    separator="-",
    extension="arff",
    check=True,
    fs=None,
):
    """
    Filename generator for the datafiles of this experiment
    """

    # Directory name
    data_dir = FILESYSTEM["data"] if fs is None else fs["datal"]
    step_dir = build_directory_name(
        parent=data_dir, basename="step", idx=step, zeroes=2
    )

    # File name
    filename = build_filename(
        basename, prefix=prefix, suffix=suffix, separator=separator, extension=extension
    )

    return _check_and_join(filename, step_dir, check=check)


def filename_model(
    basename,
    prefix="",
    suffix="default",
    separator="-",
    extension="pkl",
    check=True,
    fs=None,
):
    """
    Filename generator of the models of this experiment
    """
    # Directory name
    mod_dir = FILESYSTEM["model"] if fs is None else fs["model"]

    # File name
    filename = build_filename(
        basename, prefix=prefix, suffix=suffix, separator=separator, extension=extension
    )

    return _check_and_join(filename, mod_dir, check=check)


def filename_query(
    basename,
    prefix="",
    suffix="default",
    separator="-",
    extension="npy",
    check=True,
    fs=None,
):
    """
    Filename generator of the query files of this experiment
    """
    # Directory name
    qry_dir = FILESYSTEM["query"] if fs is None else fs["query"]

    # File name
    filename = build_filename(
        basename, prefix=prefix, suffix=suffix, separator=separator, extension=extension
    )

    return _check_and_join(filename, qry_dir, check=check)


def filename_cli_commands(
    exp_keyword,
    prefix="",
    suffix="",
    separator="-",
    extension="csv",
    check=True,
    fs=None,
):
    # Directory name
    cli_config_dir = FILESYSTEM["cli-config"] if fs is None else fs["cli-config"]

    # File name
    filename = build_filename(
        basename=exp_keyword,
        prefix=prefix,
        suffix=suffix,
        separator=separator,
        extension=extension,
    )

    return _check_and_join(filename, cli_config_dir, check=check)


def filename_nodefile(
    basename="nodefile", check=True, fs=None,
):
    # Directory name
    cli_dir = FILESYSTEM["cli"] if fs is None else fs["cli"]

    # File name
    filename = build_filename(
        basename=basename, prefix="", suffix="", separator="", extension="",
    )

    return _check_and_join(filename, cli_dir, check=check)


def filename_script(script, fs=None, extension="py", kind="fit", check=True):
    # Directory name
    dirname = FILESYSTEM[kind] if fs is None else fs[kind]
    filename = build_filename(script, extension=extension)
    return _check_and_join(filename, dirname, check=check, check_file=True)


def filename_results(**kwargs):
    return _filename_generic_output(kind="results", **kwargs)


def filename_logs(**kwargs):
    return _filename_generic_output(kind="logs", **kwargs)


def filename_timings(**kwargs):
    return _filename_generic_output(kind="timings", **kwargs)


def filename_config(**kwargs):
    return _filename_generic_output(kind="config", **kwargs)


def _filename_generic_output(
    kind="results",
    exp_fname=None,
    exp_dname=None,
    prefix="",
    suffix="",
    script=None,
    separator=SEPARATOR,
    extension="csv",
    check=True,
    fs=None,
):
    # Directory name
    directory_name = exp_directory(exp_dname=exp_dname, script=script, fs=fs).get(
        kind, False
    )
    assert directory_name

    # File name
    filename = build_filename(
        basename=exp_fname,
        prefix=prefix,
        suffix=suffix,
        separator=separator,
        extension=extension,
    )

    return _check_and_join(filename, directory_name, check=check)


# General functions
def build_filename(
    basename="",
    prefix="",
    suffix="",
    separator=SEPARATOR,
    extension="csv",
    **code_string_kwargs
):

    if isinstance(basename, list):
        basename = separator.join(basename)

    if isinstance(prefix, list):
        prefix = separator.join(prefix)

    if isinstance(suffix, list):
        suffix = separator.join(suffix)

    if code_string_kwargs:
        code_string = build_code_string(**code_string_kwargs)
    else:
        code_string = ""

    base = separator.join(
        [x for x in (prefix, basename, code_string, suffix) if len(x) > 0]
    )

    if len(extension) > 0:
        return base + ".{}".format(extension)
    else:
        return base


def build_code_string(idx=0, kind=None, zeroes=4):

    index_string = "{}".format(idx).zfill(zeroes)
    label_string = LABELS.get(kind, None)

    if label_string is None:
        return index_string
    else:
        return "{}{}{}".format(label_string, SEPARATOR, index_string)


def build_directory_name(
    parent=None, basename=None, separator=SEPARATOR, **code_string_kwargs
):

    code_string = build_code_string(**code_string_kwargs)

    if basename is not None:
        dirname = "{}{}{}".format(basename, separator, code_string)
    else:
        dirname = code_string

    if parent is None:
        return dirname
    else:
        return os.path.join(parent, dirname)


def _check_and_join(filename, directory, check=True, check_file=False):
    # If dir does not exist, make it
    if check:
        if not os.path.exists(directory):
            os.makedirs(directory)

    fname = os.path.join(directory, filename)
    if check_file:
        assert os.path.isfile(fname)
    return fname


# Etc
def default_prefix_exp_fn_suffix(
    config,
    predict_config=None,
    fit_config=None,
    exp_idx=None,
    qry_idx=None,
    exp_fn_fields=None,
):

    if exp_idx is None:
        exp_idx = config.get("exp_idx", 0)
    else:
        assert exp_idx == config.get("exp_idx")

    p = experiment_prefix(exp_idx)
    s = experiment_suffix(qry_idx)

    if predict_config is not None:
        f = experiment_filename(
            config, predict_config, kind="predict", fields=exp_fn_fields
        )
    elif fit_config is not None:
        f = experiment_filename(config, fit_config, kind="fit", fields=exp_fn_fields)
    else:
        raise NotImplementedError("No idea what to do.")

    return p, f, s


def experiment_filename(
    config, predict_config=None, fit_config=None, kind="fit", fields=None
):

    exp_fn = [config.get("dataset")]

    if kind in {"fit"}:
        if fields is not None:
            exp_fn = exp_fn + [fit_config.get(f) for f in fields]
        return exp_fn
    elif kind in {"predict"}:
        if fields is not None:
            exp_fn = exp_fn + [predict_config.get(f) for f in fields]
        return exp_fn
    else:
        raise NotImplementedError("No idea what convention to follow.")


def experiment_prefix(exp_idx):
    return build_code_string(idx=exp_idx, kind=None)


def experiment_suffix(qry_idx):

    if qry_idx is None:
        return ""
    elif isinstance(qry_idx, int):
        return build_code_string(idx=qry_idx, kind="query")
    elif isinstance(qry_idx, list):
        if len(qry_idx) > 1:
            suffix_one = build_code_string(idx=qry_idx[0], kind="query")
            suffix_two = build_code_string(idx=qry_idx[-1], kind="query")
            suffix = [suffix_one, suffix_two]
        else:
            suffix = build_code_string(idx=qry_idx[0], kind="query")
        return suffix

