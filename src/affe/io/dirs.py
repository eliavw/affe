import os
from functools import partial
from os.path import dirname

from ..utils import flatten_dict, keychain
from .CTE import DEFAULT_CHILDREN, LABELS, SEPARATOR
from .tree import tree_path_abs, get_children
from .utils import get_code_string


# Tree creation from filesystem
def mimic_fs(
    root=None, root_levels_up=2, exclude=None, depth=1, flatten=True, rename_root=None
):
    if root is None:
        root = get_default_root(levels_up=root_levels_up)

    if exclude is None:
        exclude = {"note", "src", "docs", "tests", "visualisation"}

    tree = mimic_directory(root, exclude_children=exclude)

    if rename_root is not None:
        tree = rename_directory(tree, source="root", target=rename_root)

    if depth > 0:
        do_not_expand = {"root", rename_root}

        for node, value in tree.items():
            if node not in do_not_expand:

                if rename_root is not None:
                    next_root = "{}.{}".format(rename_root, node)
                else:
                    next_root = node

                subdir = tree_path_abs(tree, node)
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

    tree = get_directory(root=directory_path, children=children)

    return tree


# Tree creation from specification
def get_directory(root=None, children=None, root_levels_up=0):
    if root is None:
        root = get_default_root(levels_up=root_levels_up)

    directory = dict(root=root)
    if children is not None:
        parent = "root"

        s = {child: parent for child in children}
        directory = {**directory, **s}
    return directory


# Tree modification
def insert_new_subdirectory(
    tree,
    parent="root",
    child="",
    code_string=False,
    return_key=False,
    **code_string_kwargs,
):
    """
    Insert a new subdirectory entry in the given directory tree.
    
    This new subdirectory has no children.
    """
    assert isinstance(child, str)

    child = get_directory_name(
        name=child, code_string=code_string, **code_string_kwargs
    )

    # Include in tree
    if parent not in {"root"}:
        key = keychain(parent, child)
    else:
        key = child

    tree[key] = parent

    if return_key:
        return tree, key
    else:
        return tree


def insert_old_subdirectory(
    tree,
    parent="root",
    child=None,
    code_string=False,
    return_key=False,
    **code_string_kwargs,
):
    """
    Insert an existing subdirectory tree in the given directory tree.
    
    This new subdirectory has children as defined by its own tree
    """
    assert isinstance(child, dict)

    # insert child root in parent tree
    child_root = child["root"]
    tree, child_root_key = insert_new_subdirectory(
        tree,
        parent=parent,
        child=child_root,
        code_string=code_string,
        return_key=True,
        **code_string_kwargs,
    )

    # rename child root for consistency with parent tree
    child = rename_directory(child, source="root", target=child_root_key)

    # insert child tree in parent tree (all these steps are necessary!)
    child.pop(child_root_key)  # already in the parent anyway!
    child_root = tree[child_root_key]
    tree[child_root_key] = child
    tree = flatten_dict(tree)
    tree[child_root_key] = child_root  # add again, you replaced it with the child tree

    if return_key:
        return tree, child_root_key
    else:
        return tree


def insert_subdirectory(
    tree,
    parent="root",
    child=None,
    code_string=False,
    return_key=False,
    **code_string_kwargs,
):
    actions = {}
    actions[str] = insert_new_subdirectory
    actions[dict] = insert_old_subdirectory

    return actions.get(type(child), False)(
        tree,
        parent,
        child=child,
        code_string=code_string,
        return_key=return_key,
        **code_string_kwargs,
    )


# Tree inspection
def get_children_paths(tree, node):
    """
    Get the paths of all the children directories of a node.
    """
    children = get_children(tree, node)
    children_paths = [tree_path_abs(tree, c) for c in children]
    return children_paths

def get_subdirectory_paths(tree, node):
    return {os.path.split(v)[-1]: v for v in get_children_paths(tree, node)}

# Tree verification
def check_existence_of_directory(tree, nodes=None):
    """
    Verification of the tree wrt actual filesystem
    """
    if nodes is None:
        nodes = tree.keys()

    if isinstance(nodes, str):
        nodes = [nodes]

    for node in nodes:
        assert (
            node in tree.keys()
        ), "You are asking for the existence of a directory unknown to this tree"

        path = tree_path_abs(tree, node)
        if not os.path.isdir(path):
            os.makedirs(path)

    return


# Directory-naming
def get_directory_name(name=None, code_string=False, **code_string_kwargs):
    if code_string:
        code_string = get_code_string(**code_string_kwargs)
        if name not in {""}:
            name = "{}{}{}".format(name, separator, code_string)
        else:
            name = code_string
    return name


def rename_directory(tree, source="root", target="rootroot"):

    tree = tree.copy()

    # 1. Replace the entry of source
    src_tmp = tree.pop(source)
    tree[target] = src_tmp

    # 2. Replace everything that has source as parent
    tree = {k: v if v != source else target for k, v in tree.items()}

    return tree


# Default suggestions
def get_root_directory(root=None, children=None, root_levels_up=2):
    if children is None:
        children = DEFAULT_CHILDREN["root"]
    return get_directory(root=root, children=children, root_levels_up=root_levels_up)


def get_flow_directory(keyword="manual", children=None, root_levels_up=2):
    if children is None:
        children = DEFAULT_CHILDREN.get("flow")

    flow_directory_tree = get_directory(
        root=keyword, children=children, root_levels_up=root_levels_up
    )
    return flow_directory_tree


def get_default_root(levels_up=2):
    root = os.getcwd()
    for _ in range(levels_up):
        root = dirname(root)
    return root
