import os

from .CTE import DEFAULT_CHILDREN, KEYCHAIN_SEPARATOR, LABELS, SEPARATOR


# Tree navigation
def tree_path(tree, node, separator=None):
    tree_path = []
    while tree.get(node, False):
        tree_path.insert(0, node)
        node = tree.get(node)  # Go to parent node

    if separator is not None:
        first_one = tree_path[0]  # Root stays root.
        tree_path = [n.split(separator).pop() for n in tree_path]
        tree_path[0] = first_one
    return tree_path


def get_children(tree, node):
    return {k: v for k, v in tree.items() if v == node}


def get_subtree(tree, node):
    subtree = get_children(tree, node)
    for child in subtree:
        subtree = {**subtree, **get_subtree(tree, child)}
    return subtree


# Tree navigation wrt filesystem
def tree_path_abs(tree, node, filename=None, separator=KEYCHAIN_SEPARATOR):
    tp = tree_path(tree, node, separator=separator)
    if filename is not None:
        tp.append(filename)

    root_node = tp.pop(0)
    root_dir = tree.get(root_node)
    if len(tp) > 0:
        return os.path.join(root_dir, *tp)
    else:
        return root_dir




# Helpers
def _alter_root_value(tree, value):
    tree = tree.copy()
    root = _get_root_node(tree)
    tree[root] = value
    return tree


def _get_root_node(tree):
    start_node = next(iter(tree.keys()))  # random start
    tp = tree_path(tree, start_node)
    return tp.pop()
