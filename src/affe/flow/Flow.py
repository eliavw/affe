import inspect
import os
import sys
import time
from functools import partial

import dill as pkl

from ..dtaiexperimenter import Function, Process
from ..io import dump_object
from .utils import extract_source_of_function
from ..execs import (
    DTAIExperimenterFunctionExecutor,
    DTAIExperimenterProcessExecutor,
    NativeExecutor,
    ShellExecutor,
    DTAIExperimenterShellExecutor,
)


class Flow:
    """A workflow object.

    A flow is an abstraction of 'something' that needs to be executed

    A good workflow abstracts away a lot of boilerplate regarding
        - config
        - io
        - execution

    For the executors, we introduce the following terminology;
        `local`:    Execute flow in python process
        `shell`:    Execute flow in a shell

        `now`:   Stderr and stdout go as default
        `log`:   Stderr and stdout are collected in a logfile.

        `command`:

    Returns:
        [type] -- [description]
    """

    executors = dict(
        local_now=NativeExecutor,
        shell_now=ShellExecutor,
        local_log=DTAIExperimenterFunctionExecutor,
        shell_log=DTAIExperimenterProcessExecutor,
        shell_log_autonomous=DTAIExperimenterShellExecutor,
    )

    def __init__(
        self,
        config=None,
        flow=None,
        imports=None,
        log_filepath="logfile",
        flow_filepath="flowfile.pkl",
        timeout_s=60,
    ):
        # Basics
        self.log_filepath = log_filepath
        self.flow_filepath = flow_filepath
        self.timeout_s = timeout_s
        self.dumped = False

        self.config = config

        # Flows and Imports are python-functions
        self.imports = imports
        self.flow = flow
        return

    def execute(self):
        e = self.executors.get("local_now")(self)
        return e.execute()

    def run(self):
        return self.execute()

    def run_via_shell(self, **kwargs):
        e = self.executors.get("shell_now")(self, **kwargs)
        return e.execute()

    def run_with_log(self, **kwargs):
        e = self.executors.get("local_log")(self, **kwargs)
        return e.execute()

    def run_with_log_via_shell(self, return_log_filepath=True, **kwargs):
        e = self.executors.get("shell_log")(self, **kwargs)
        return e.execute(return_log_filepath=return_log_filepath)

    def run_via_shell_with_log(self, return_log_filepath=True, **kwargs):
        """Synonym to method above."""
        return self.run_with_log_via_shell(
            return_log_filepath=return_log_filepath, **kwargs
        )

    def get_shell_command(self, **kwargs):
        e = self.executors.get("shell_now")(self, **kwargs)
        return e.command

    def get_shell_with_log_command(self, **kwargs):
        # The other shell_log command goes via Process of DTAIExperimenter, this one generates a standalone bash command.
        e = self.executors.get("shell_log_autonomous")(self, **kwargs)
        return e.command

    @classmethod
    def load(cls, fn):
        with open(fn, "rb") as f:
            flow = pkl.load(f)
        return flow

    def dump(self, flow_filepath=None):
        if flow_filepath is not None:
            self.flow_filepath = flow_filepath

        dump_object(self, self.flow_filepath)
        self.dumped = True
        return

    @property
    def imports_source_code(self):
        if self._imports_source_code is None:
            if self.imports is not None:
                self._imports_source_code = extract_source_of_function(self.imports)
            else:
                self._imports_source_code = None
        return self._imports_source_code

    @property
    def flow_source_code(self):
        if self._flow_source_code is None:
            if self.flow is not None:
                self._flow_source_code = extract_source_of_function(self.flow)
            else:
                self._flow_source_code = None
        return self._flow_source_code
