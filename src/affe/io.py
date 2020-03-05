import os
from os.path import dirname
from functools import partial
from .utils import flatten_dict

# Suggested Defaults
SEPARATOR = "-"
LABELS = dict(query="q", exp="e", fold="f", experiment="e")
DEFAULT_CHILDREN = dict(
    root=["cli", "data", "out", "scripts"],
    out=["manual", "preprocessing", "fit", "predict"],
    model=["models", "logs", "timings"],
    exp=["config", "logs", "results", "timings", "tmp"],
)


def _default_root(levels_up=2):
    root = os.getcwd()
    for _ in range(levels_up):
        root = dirname(root)
    return root


def _directory(root=None, children=None, root_levels_up=0):
    if root is None:
        root = _default_root(levels_up=root_levels_up)

    directory = dict(root=root)
    if children is not None:
        parent = "root"

        s = {child: parent for child in children}
        directory = {**directory, **s}
    return directory


def tree_path(tree, node, separator=None):
    tree_path = []
    while tree.get(node, False):
        tree_path.insert(0, node)
        node = tree.get(node)  # Go to parent node

    if separator is not None:
        first_one = tree_path[0] # Root stays root.
        tree_path = [n.split(separator).pop() for n in tree_path]
        tree_path[0] = first_one
    return tree_path


def _rename_directory(directory, source="root", target="rootroot"):

    directory = directory.copy()

    # 1. Replace the entry of source
    src_tmp = directory.pop(source)
    directory[target] = src_tmp

    # 2. Replace everything that has source as parent
    directory = {k: v if v != source else target for k, v in directory.items()}

    return directory


def _alter_root_value(tree, value):
    tree = tree.copy()
    root = _get_root_node(tree)
    tree[root] = value
    return tree


def _get_root_node(tree):
    return [node for node in tree if tree.get(node) not in tree].pop()


def abspath(tree, node, filename=None, separator="."):
    tp = tree_path(tree, node, separator=separator)
    if filename is not None:
        tp.append(filename)

    root_node = tp.pop(0)
    root_dir = tree.get(root_node)
    if len(tp) > 0:
        return os.path.join(root_dir, *tp)
    else:
        return root_dir


def _insert_child_directory_in_parent_directory(
    child_dir, parent_dir, anchor="root",
):
    if anchor is not None:
        # check nameclashes
        assert len(set(child_dir.keys()) & set(parent_dir.keys())) == 0
        child_dir = _alter_root_value(child_dir, anchor)
        return {**child_dir, **parent_dir}
    else:
        # Assumption: child dir has as its root a directory that is represented in the parent dir
        child_root = _get_root_node(child_dir)
        assert child_root in parent_dir
        child_dir.pop(child_root)

        # check nameclashes
        assert len(set(child_dir.keys()) & set(parent_dir.keys())) == 0
        return {
            **parent_dir,
            **child_dir,
        }


def get_code_string(idx=0, kind=None, n_zeroes=4, separator=SEPARATOR, labels=LABELS):

    index_string = "{}".format(idx).zfill(n_zeroes)
    label_string = labels.get(kind, None)

    if label_string is None:
        return index_string
    else:
        return "{}{}{}".format(label_string, separator, index_string)


def get_filepath(
    basename="",
    prefix="",
    suffix="",
    extension="csv",
    separator=SEPARATOR,
    tree=None,
    node=None,
    check_directory=True,
    check_file=False,
    **code_string_kwargs,
):
    filename = get_filename(
        basename=basename,
        prefix=prefix,
        suffix=suffix,
        extension=extension,
        separator=separator,
        **code_string_kwargs,
    )

    filepath = abspath(tree, node, filename=filename)

    # Ensure existence of the directory, we do not care about overwriting a file.
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


def _check(filename, check_directory=True, check_file=False):
    # If directory does not exist: make it
    directory = os.path.dirname(filename)
    if check_directory:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # If file already exists: complain
    if check_file:
        assert os.path.isfile(filename)
    return True


def mimic_fs(
    root=None, root_levels_up=2, exclude=None, depth=1, flatten=True, rename_root=None
):
    if root is None:
        root = _default_root(levels_up=root_levels_up)

    if exclude is None:
        exclude = {"note", "src", "docs", "tests", "visualisation"}

    tree = mimic_directory(root, exclude_children=exclude)

    if rename_root is not None:
        tree = _rename_directory(tree, source="root", target=rename_root)

    if depth > 0:
        do_not_expand = {"root", rename_root}

        for node, value in tree.items():
            if node not in do_not_expand:

                if rename_root is not None:
                    next_root = "{}.{}".format(rename_root, node)
                else:
                    next_root = node

                subdir = abspath(tree, node)
                subtree = mimic_fs(
                    root=subdir,
                    exclude=exclude,
                    depth=depth - 1,
                    flatten=False,
                    rename_root=next_root,
                )
                subtree.pop(next_root)
                if len(subtree) > 0:
                    tree[node] = subtree
                    tree = flatten_dict(tree)
                    tree[node] = value
                do_not_expand.add(node)

    return tree


def mimic_directory(directory_path, exclude_children=None):
    if exclude_children is None:
        exclude_children = {"note", "src", "docs", "tests"}

    children = [
        d
        for d in os.listdir(directory_path)
        if os.path.isdir(os.path.join(directory_path, d))  # Has to be a directory
        if not d.startswith(".")  # Exclude hidden dirs
        if not d.startswith("_")  # Exclude hidden dirs
        if d not in exclude_children
    ]

    tree = _directory(root=directory_path, children=children)

    return tree


# Interesting Suggested Defaults
DEFAULT_NAMING_CONVENTION = dict(
    model=partial(get_filepath, suffix="default", extension="pkl", node="model"),
    query=partial(get_filepath, suffix="default", extension="npy", node="query"),
    timings=partial(get_filepath, basename="timings", extension="csv", node="timings"),
    results=partial(get_filepath, basename="results", extension="csv", node="results"),
    logs=partial(get_filepath, basename="logs", extension="", node="logs"),
)


def get_root_directory(root=None, children=None, root_levels_up=2):
    if children is None:
        children = DEFAULT_CHILDREN["root"]
    return _directory(root=root, children=children, root_levels_up=root_levels_up)


def get_exp_directory(root=None, children=None, root_levels_up=2):
    if children is None:
        children = DEFAULT_CHILDREN["exp"]
    return _directory(root=root, children=children, root_levels_up=root_levels_up)

