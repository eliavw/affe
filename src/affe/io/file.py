import os
from functools import partial

from .CTE import DEFAULT_CHILDREN, KEYCHAIN_SEPARATOR, LABELS, SEPARATOR
from .tree import tree_path, tree_path_abs
from .utils import get_code_string


# Absolute paths
def abspath(tree, node, filename=None, separator=KEYCHAIN_SEPARATOR):
    return tree_path_abs(tree, node, filename=filename, separator=separator)


# Creating filenames
def get_filepath(
    basename=None,
    prefix="",
    suffix="",
    extension="csv",
    separator=SEPARATOR,
    tree=None,
    node=None,
    check_directory=True,
    check_file=False,
    filename=None,
    **code_string_kwargs,
):
    if basename is None and node is not None:
        basename = node

    if filename is None:
        filename = get_filename(
            basename=basename,
            prefix=prefix,
            suffix=suffix,
            extension=extension,
            separator=separator,
            **code_string_kwargs,
        )

    filepath = abspath(tree, node, filename=filename)

    # Ensure existence of the directory, we (by default) do not care about overwriting a file.
    assert _check(filepath, check_directory=check_directory, check_file=check_file)

    return filepath


def get_filename(
    basename="",
    prefix="",
    suffix="",
    extension="csv",
    separator=SEPARATOR,
    **code_string_kwargs,
):
    # Preprocess filename parts
    if isinstance(basename, list):
        basename = separator.join(basename)

    if isinstance(prefix, list):
        prefix = separator.join(prefix)

    if isinstance(suffix, list):
        suffix = separator.join(suffix)

    # Generate code string if necessary (always assumed as last thing)
    if code_string_kwargs:
        code_string = get_code_string(**code_string_kwargs)
    else:
        code_string = ""

    # Join parts for full filename
    base = separator.join(
        [x for x in (prefix, basename, code_string, suffix) if len(x) > 0]
    )

    # Add extension if necessary
    if len(extension) > 0:
        return base + ".{}".format(extension)
    else:
        return base


# Helpers
def _check(filename, check_directory=True, check_file=False):
    # If directory does not exist: make it
    directory = os.path.dirname(filename)
    if check_directory:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # If file already exists: complain
    if check_file:
        assert os.path.isfile(filename), "Filename {} does not exist".format(filename)
    return True


# Templates
FN_TEMPLATE_CLASSIC_FLOW = dict(
    timings=partial(get_filepath, extension="csv", node="timings"),
    results=partial(get_filepath, extension="pkl", node="results"),
    config=partial(get_filepath, extension="json", node="config"),
    logs=partial(get_filepath, extension="", node="logs"),
    flows=partial(get_filepath, extension="pkl", node="flows"),
)


def get_default_model_filename(
    data_identifier="", model_identifier="", extension="pkl", **kwargs
):
    model_filename = get_filename(
        basename=[model_identifier, data_identifier], extension=extension, **kwargs
    )
    return model_filename


def get_template_filenames(tree, template=FN_TEMPLATE_CLASSIC_FLOW, **kwargs):
    template_filenames = {}
    for k in tree:
        if template.get(k, False):
            v = template.get(k)(tree=tree, **kwargs)
            template_filenames[k] = v

    return template_filenames
