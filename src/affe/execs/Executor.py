import os
import subprocess
import sys

from ..cli import get_flow_cli


class Executor(object):
    def __init__(self, workflow):

        self.flow = workflow.flow
        self.config = workflow.config
        return

    def execute(self, **kwargs):
        raise NotImplementedError("Not implemented in abstract base class.")

    def run(self, **kwargs):
        # Synonym of execute.
        return self.execute(**kwargs)


class NativeExecutor(Executor):
    """
    Native executor: execute a Flow by calling its own flow() method.
    """

    def execute(self):
        return self.flow(self.config)


class ShellExecutor(Executor):
    """
    Shell executor: execute a Flow by generating a command and running it a subprocess.
    """

    def __init__(
        self,
        workflow,
        cwd=None,
        absolute=True,
        executable=None,
        cli=None,
        flow_filepath=None,
        command=None,
    ):
        super().__init__(workflow)

        self.cwd = self.set_cwd(cwd=cwd)
        self.executable = self.set_executable(executable=executable)
        self.cli = self.set_cli(cli=cli, absolute=absolute)
        self.flow_filepath = self.set_flow_filepath(
            workflow, flow_filepath=flow_filepath
        )
        self.command = self.set_command(
            command=command
        )  # N.b.: Comes after flow_filepath definition!

        workflow.dump(flow_filepath=self.flow_filepath)
        return

    def execute(self, shell=True, **kwargs):
        return subprocess.call(self.command, shell=shell, **kwargs)

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

    @staticmethod
    def set_cli(cli=None, absolute=True):
        if cli is not None:
            return cli
        else:
            return get_flow_cli(abs=absolute)

    @staticmethod
    def set_flow_filepath(workflow, flow_filepath=None):
        if flow_filepath is None:
            r = workflow.flow_filepath
        else:
            r = flow_filepath

        assert isinstance(r, str)
        return r

    def set_command(self, command=None):
        if command is not None:
            return command
        else:
            return """{0} {1} -f {2}""".format(
                self.executable, self.cli, self.flow_filepath
            )

    def get_command(self):
        return self.command


class ShellCommandExecutor(object):
    """Very simple class that does not need a flow and just executes a command.
    """

    def __init__(self, command):
        self.command = command
        return

    def execute(self, shell=True, **kwargs):
        return subprocess.call(self.command, shell=shell, **kwargs)

    def run(self, **kwargs):
        return self.execute(**kwargs)
