import os
import sys
from functools import partial

from ..cli import get_flow_cli, get_flow_cli_with_monitors
from ..dtaiexperimenter import Function, Logfile, Process, TimeLimit
from .Executor import Executor


class DTAIExperimenterExecutor(Executor):
    def __init__(self, workflow, log_filepath=None, timeout_s=None):
        super().__init__(workflow)

        self.log_filepath = self.set_log_filepath(workflow, log_filepath=log_filepath)
        self.timeout_s = self.set_timeout_s(workflow, timeout_s=timeout_s)
        self.monitors = self.set_monitors()
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

        monitors = [Logfile(self.log_filepath), TimeLimit(self.timeout_s)]
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


class DTAIExperimenterProcessExecutor(DTAIExperimenterExecutor):
    def __init__(
        self,
        workflow,
        executable=None,
        cli=None,
        absolute=True,
        flow_filepath=None,
        log_filepath=None,
        timeout_s=None,
        cwd=None,
        command=None,
        delayed=False,
    ):
        super().__init__(workflow, log_filepath=log_filepath, timeout_s=timeout_s)

        self.cwd = self.set_cwd(cwd=cwd)
        self.executable = self.set_executable(executable=executable)
        self.flow_filepath = self.set_flow_filepath(
            workflow, flow_filepath=flow_filepath
        )
        self.delayed = delayed
        self.cli = self.set_cli(cli=cli, absolute=absolute, delayed=delayed)
        self.command = self.set_command(command=command, delayed=delayed)
        self.future = self.set_future()

        workflow.dump(flow_filepath=self.flow_filepath)
        return

    @staticmethod
    def set_cwd(cwd=None):
        if cwd is None:
            r = os.getcwd()
        else:
            r = cwd
        return r

    @staticmethod
    def set_executable(executable=None):
        if executable is None:
            r = sys.executable
        else:
            r = executable
        return r

    def set_cli(self, cli=None, absolute=True, delayed=False):
        if cli is not None:
            return cli
        elif delayed:
            return self.set_delayed_cli(absolute=absolute)
        else:
            return self.set_immediate_cli(absolute=absolute)

    @staticmethod
    def set_immediate_cli(absolute=True):
        return get_flow_cli(abs=absolute)

    @staticmethod
    def set_delayed_cli(absolute=True):
        return get_flow_cli_with_monitors(abs=absolute)

    @staticmethod
    def set_flow_filepath(workflow, flow_filepath=None):
        if flow_filepath is None:
            r = workflow.flow_filepath
        else:
            r = flow_filepath

        assert isinstance(r, str)
        return r

    def set_command(self, command=None, delayed=False):
        if command is not None:
            return command
        elif delayed:
            return self.set_delayed_command()
        else:
            return self.set_immediate_command()

    def set_immediate_command(self):
        r = """{0} {1} -f {2}""".format(self.executable, self.cli, self.flow_filepath)
        return r

    def set_delayed_command(self):
        r = """{0} -l {1} -t {2}""".format(
            self.set_immediate_command(), self.log_filepath, self.timeout_s
        )
        return r

    def set_future(self):
        if self.delayed:
            return ReturnCommand(self.command)
        else:
            return Process(
                self.command.split(" "), monitors=self.monitors, cwd=self.cwd
            )

    def get_command(self):
        return self.command

class ReturnCommand:
    def __init__(self, command="a string"):
        self.command = command
        return

    def run(self):
        return self.command
