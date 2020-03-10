import inspect
import os
import sys
import time
from functools import partial

import dill as pkl

from ..dtaiexperimenter import Function, Process
from ..io import dump_object
from .utils import extract_source_of_function
from ..execs import DTAIExperimenterFunctionExecutor, DTAIExperimenterProcessExecutor


class Flow:
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

    def execute(self):
        return self.flow(self.config)

    def run(self):
        return self.execute()

    def run_with_log(self, **kwargs):
        e = DTAIExperimenterFunctionExecutor(self, **kwargs)
        return e.execute()

    def run_via_shell_with_log(self, **kwargs):
        e = DTAIExperimenterProcessExecutor(self, **kwargs)
        return e.execute()

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
