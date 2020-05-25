import os
import subprocess
import sys
from functools import partial

from ..cli import get_flow_cli, get_flow_cli_with_monitors
from ..dtaiexperimenter import Function, Logfile, MemoryLimit, Process, TimeLimit
from .Executor import Executor, ShellExecutor


class DTAIExperimenterExecutor(Executor):
    def __init__(self, workflow, log_filepath=None, timeout_s=None, memory_mb=None):
        self.log_filepath = self.set_log_filepath(
            workflow, log_filepath=log_filepath
        )  # This really has to happen first.
        self.timeout_s = self.set_timeout_s(workflow, timeout_s=timeout_s)
        self.memory_mb = self.set_memory_mb(workflow, memory_mb=memory_mb)
        self.monitors = self.set_monitors()

        super().__init__(workflow)
        self.future = None  # Get fixed in the subclasses
        return

    @staticmethod
    def set_timeout_s(workflow, timeout_s=None):
        if timeout_s is None:
            r = workflow.timeout_s
        else:
            r = timeout_s

        if not isinstance(r, int):
            r = int(r)
        return r

    @staticmethod
    def set_memory_mb(workflow, memory_mb=None):
        # This one is allowed to be None!
        if memory_mb is None and hasattr(workflow, "memory_mb"):
            r = workflow.memory_mb
        else:
            r = memory_mb

        return r

    @staticmethod
    def set_log_filepath(workflow, log_filepath=None):
        if log_filepath is None:
            r = workflow.log_filepath
        else:
            r = log_filepath

        assert isinstance(r, str)
        return r

    def set_monitors(self):
        """
        Create monitors to monitor whatever is being executed. 
        
        Default monitors are a logger and a timeout.
        """
        monitors = []
        if self.log_filepath is not None:
            monitors.append(Logfile(self.log_filepath))

        if self.timeout_s is not None:
            monitors.append(TimeLimit(self.timeout_s))

        if self.memory_mb is not None:
            monitors.append(MemoryLimit(maxmem=self.memory_mb))

        return monitors

    def execute(self, return_log_filepath=True):
        r = self.future.run()
        if return_log_filepath:
            return self.log_filepath
        else:
            return r


class DTAIExperimenterFunctionExecutor(DTAIExperimenterExecutor):
    def __init__(
        self, workflow, log_filepath=None, timeout_s=None,
    ):
        super().__init__(workflow, log_filepath=log_filepath, timeout_s=timeout_s)
        self.flow_initialized = self.set_flow_initialized()
        self.future = self.set_future()
        return

    def set_flow_initialized(self):
        return partial(self.flow, self.config)

    def set_future(self):
        return Function(self.flow_initialized, monitors=self.monitors)


class DTAIExperimenterProcessExecutor(DTAIExperimenterExecutor, ShellExecutor):
    def __init__(
        self,
        workflow,
        executable=None,
        cli=None,
        absolute=True,
        flow_filepath=None,
        cwd=None,
        command=None,
        log_filepath=None,
        timeout_s=None,
    ):
        DTAIExperimenterExecutor.__init__(
            self, workflow, log_filepath=log_filepath, timeout_s=timeout_s
        )

        ShellExecutor.__init__(
            self,
            workflow,
            executable=executable,
            cli=cli,
            absolute=absolute,
            flow_filepath=flow_filepath,
            cwd=cwd,
            command=command,
        )

        self.future = self.set_future()
        workflow.dump(flow_filepath=self.flow_filepath)
        return

    def set_future(self):
        return Process(self.command.split(" "), monitors=self.monitors, cwd=self.cwd)


class DTAIExperimenterShellExecutor(DTAIExperimenterProcessExecutor):
    @staticmethod
    def set_cli(cli=None, absolute=True):
        if cli is not None:
            return cli
        else:
            return get_flow_cli_with_monitors(abs=absolute)

    def set_command(self, command=None):
        if command is not None:
            return command
        else:
            return """{0} {1} -f '{2}' -l '{3}' -t {4}""".format(
                self.executable,
                self.cli,
                self.flow_filepath,
                self.log_filepath,
                self.timeout_s,
            )

    def set_future(self):
        return DelayedShellCommand(self.command)


class FunctionExecutor(DTAIExperimenterExecutor):
    def __init__(self, f, log_filepath=None, timeout_s=None, memory_mb=None, **kwargs):
        self.flow = f
        self.config = kwargs
        self.log_filepath = log_filepath
        self.timeout_s = timeout_s
        self.memory_mb = memory_mb

        self.monitors = self.set_monitors()
        self.flow_initialized = self.set_flow_initialized()
        self.future = self.set_future()
        return

    def set_flow_initialized(self):
        # This is the main difference with the above, this just executes a function straight away.
        return partial(self.flow, **self.config)

    def set_future(self):
        return Function(self.flow_initialized, monitors=self.monitors)


class DelayedShellCommand:
    """Mini-helper class for DTAIExperimenterShellExecutor, I need to pack a generated command in a future for it to be ran correctly by the superclass.
    """

    def __init__(self, command):
        self.command = command

    def run(self, shell=True, **kwargs):
        return subprocess.call(self.command, shell=shell, **kwargs)
