from ..flow import Flow
from ..execs import ShellCommandExecutor
from ..cli import get_scheduler_cli


class Scheduler(Flow):
    def __init__(self, workflows):
        flow_commands = get_flow_commands()
        exec_config = get_executor_config()

        return

    @staticmethod
    def get_flows(flows):
        if not isinstance(flows, (list, dict, tuple)):
            flows = [flows]

        for f in flows:
            assert isinstance(f, Flow)

        return flows

    @staticmethod
    def get_flow_commands(flows, log=True, **kwargs):
        if log:
            commands = [f.get_shell_with_log_command(**kwargs) for f in flows]
        else:
            commands = [f.get_shell_command(**kwargs) for f in flows]
        return commands

    def get_executor_config(self,):
        command = get_command(
            executable="python",
            n_flows=1,
            n_jobs=2,
            omp_num_threads=1,
            cli=None,
            flow_filepath=None,
        )

        executor_config = dict(command=command)
        return

    def get_command(
        executable="python",
        n_flows=1,
        n_jobs=2,
        omp_num_threads=1,
        cli=None,
        flow_filepath=None,
    ):
        if cli is None:
            cli = get_scheduler_cli()

        return """seq 0 {0} | parallel --jobs {1} --bar "OMP_NUM_THREADS={2} {3} {4} -f {5} -i $1"
        """.format(
            n_flows, n_jobs, omp_num_threads, executable, cli, flow_filepath
        )

