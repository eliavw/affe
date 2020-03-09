import inspect
import os
import sys
import time
from functools import partial
import dill

import dill as pkl

from .dtaiexperimenter import Function, Process
from .executors import get_monitors
from .io import dump_object


def load_flow(fn):
    with open(fn, "rb") as f:
        flow = pkl.load(f)
    return flow


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


class Flow:

    @classmethod
    def load(cls,fn):
        with open(fn, "rb") as f:
            flow = pkl.load(f)
        return flow

    def __init__(
        self,
        config=None,
        flow=None,
        imports=None,
        log_filepath="logfile",
        flow_filepath=None,
        timeout_s=60,
    ):
        self.log_filepath = log_filepath
        self.flow_filepath = flow_filepath
        self.timeout_s = timeout_s
        self.dumped = False

        self.config = config

        # Manage imports
        if imports is not None:
            self.imports = imports
        if self.imports is not None:
            self.imports_source_code = extract_source_of_function(self.imports)
        else:
            self.imports_source_code = None

        # Manage flows
        if flow is not None:
            self.flow = flow
        if self.flow is not None:
            self.flow_source_code = extract_source_of_function(self.flow)
        else:
            self.flow_source_code = None

        return

    def run(self):
        # r = self.flow_initialized()
        return self.flow(self.config)

    def run_with_imports(self):
        if self.imports_source_code is not None:
            exec(self.imports_source_code)

        config = self.config
        r = exec(self.flow_source_code)
        return r

    def run_with_log(self, return_log_filepath=True):
        flow_initialized = partial(self.flow, self.config)
        monitors = get_monitors(self.log_filepath, self.timeout_s)
        executor = Function(flow_initialized, monitors=monitors)

        r = executor.run()
        time.sleep(1)
        if return_log_filepath:
            return self.log_filepath
        else:
            return r

    def run_via_shell_with_log(self, executable=None, cwd=None, ensure_dump=False):
        if not self.dumped or ensure_dump:
            # If you have not dumped yourself, you cannot run yourself as a script.
            self.dump()
        assert (
            self.dumped
        ), "If you have not dumped yourself, you cannot go through a shell."

        if cwd is None:
            cwd = os.getcwd()

        if executable is None:
            executable = sys.executable

        cmd = self.get_cli_command(executable=executable)
        monitors = get_monitors(self.log_filepath, self.timeout_s)

        p = Process(cmd, monitors=monitors, cwd=cwd)  # Init Process
        return p.run()

    def run_imports(self):
        exec(self.imports_source_code)
        return

    def dump(self, flow_filepath=None):
        if flow_filepath is not None:
            self.flow_filepath = flow_filepath

        dump_object(self, self.flow_filepath)
        self.dumped = True
        return

    def get_default_cli(self, abs=True):
        from affe.cli import get_flow_cli

        return get_flow_cli(abs=abs)

    def get_logged_cli(self, abs=True):
        from affe.cli import get_flow_cli_with_monitors

        return get_flow_cli_with_monitors(abs=abs)

    def get_cli_command(self, executable=None, cli=None, return_list=True):
        if executable is None:
            executable = sys.executable

        if cli is None:
            cli = self.get_default_cli()

        cmd = []
        cmd.append(executable)
        cmd.append(cli)
        cmd.append("-f")
        cmd.append(self.flow_filepath)
        if return_list:
            return cmd
        else:
            return " ".join(cmd)

    def get_cli_command_with_logs(self, executable=None, return_list=True):

        cli = self.get_logged_cli()

        cmd = self.get_cli_command(executable=executable, cli=cli)
        cmd.append("-l")
        cmd.append(self.log_filepath)
        cmd.append("-t")
        cmd.append(str(self.timeout_s))
        if return_list:
            return cmd
        else:
            return " ".join(cmd)
