import inspect


def _find_offset_and_line_of_definition(lines):
    for l_idx, l in enumerate(lines):
        function_definition_offset = l.find("def ")
        if function_definition_offset > 0:
            break
    return function_definition_offset, l_idx


def extract_source_of_function(f, tabsize=4):
    indent = " " * tabsize
    full_source = inspect.getsource(f)
    lines = full_source.splitlines()

    function_definition_offset, l_idx = _find_offset_and_line_of_definition(lines)

    inner_lines = lines[l_idx + 1 : -1]  # Drop first and last

    for l_idx in range(len(inner_lines)):
        l = inner_lines[l_idx]
        offset = indent + " " * function_definition_offset
        if l.startswith(offset):
            inner_lines[l_idx] = l[len(offset) :]

    inner_source = "\n".join(inner_lines)
    return inner_source
