from .CTE import DEFAULT_CHILDREN, KEYCHAIN_SEPARATOR, LABELS, SEPARATOR


def get_code_string(idx=0, kind=None, n_zeroes=4, separator=SEPARATOR, labels=LABELS):

    index_string = "{}".format(idx).zfill(n_zeroes)
    label_string = labels.get(kind, None)

    if label_string is None:
        return index_string
    else:
        return "{}{}{}".format(label_string, separator, index_string)
