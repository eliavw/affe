import inspect
import os
import sys
import time
from functools import partial

import dill as pkl

from .dtaiexperimenter import Function, Process
from .executors import get_monitors
from .io import dump_object


def load_flow(fn):
    with open(fn, "rb") as f:
        flow = pkl.load(f)
    return flow


def extract_source_of_function(f, tabsize=4):
    indent = " " * tabsize
    full_source = inspect.getsource(f)
    lines = full_source.splitlines()
    inner_lines = lines[1:-1]  # Drop first and last

    for l_idx in range(len(inner_lines)):
        l = inner_lines[l_idx]
        if l.startswith(indent):
            inner_lines[l_idx] = l[tabsize:]

    inner_source = "\n".join(inner_lines)
    return inner_source


class Flow:
    def __init__(
        self,
        config=None,
        flow=None,
        imports=None,
        log_filepath="logfile",
        flow_filepath="flowfile.pkl",
        timeout_s=60,
    ):
        self.log_filepath = log_filepath
        self.flow_filepath = flow_filepath
        self.timeout_s = timeout_s

        self.config = config

        self.flow = flow
        self.dumped = False

        # source magic
        if imports is not None:
            self.imports_source_code = extract_source_of_function(imports)

        if flow is not None:
            self.flow_source_code = extract_source_of_function(flow)

        return

    def run(self):
        # r = self.flow_initialized()
        return self.flow(self.config)

    def run_with_imports(self):
        exec(self.imports_source_code)

        config = self.config
        exec(self.flow_source_code)
        return

    def run_with_log(self):
        flow_initialized = partial(self.flow, self.config)
        monitors = get_monitors(self.log_filepath, self.timeout_s)
        executor = Function(flow_initialized, monitors=monitors)

        r = executor.run()
        time.sleep(1)
        return r

    def run_via_shell(self, executable=None, cwd=None, ensure_dump=False):
        if not self.dumped or ensure_dump:
            # If you have not dumped yourself, you cannot run yourself as a script.
            self.dump()

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

    def get_cli_command(self, executable="python", return_list=True):
        cmd = []
        cmd.append(executable)
        cmd.append(self.get_default_cli())
        cmd.append("-f")
        cmd.append(self.flow_filepath)
        if return_list:
            return cmd
        else:
            return " ".join(cmd)
