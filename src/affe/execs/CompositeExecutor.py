import traceback
import warnings

from joblib import Parallel, delayed

from ..io import dump_object
from .DTAIExperimenterExecutor import DTAIExperimenterShellExecutor
from .Executor import Executor, ShellCommandExecutor, ShellExecutor
from .pinac import generate_nodefile

try:
    from tqdm import tqdm
    from dask import distributed
    from distributed import Client, Future
except ImportError:
    Client = None
    Future = None
    msg = """
    Dask (or tqdm) is not installed, therefore using the Dask Executor will not be an option.
    """
    warnings.warn(msg)


def get_default_nodefile(
    nodefile_filepath="nodefile.txt",
    desired_memory_per_thread=8,
    desired_nb_threads=None,
    max_percentage_thread_claim=50,
    machine_kinds={"pinac", "himec", "cudos"},
    claim_policy="greedy",
):
    nodefile = generate_nodefile(
        df=None,
        desired_memory_per_thread=desired_memory_per_thread,
        desired_nb_threads=desired_nb_threads,
        max_percentage_thread_claim=max_percentage_thread_claim,
        kinds=machine_kinds,
        claim_policy=claim_policy,
    )

    dump_object(nodefile, nodefile_filepath)

    return nodefile_filepath


class CompositeExecutor(Executor):
    def __init__(self, workflows, executor=None):
        self.child_workflows = workflows
        self.n_child_workflows = len(self.child_workflows)
        self.child_executor = executor
        return

    def execute(self, **kwargs):
        return [
            self.execute_child(child_index=i, **kwargs)
            for i in range(self.n_child_workflows)
        ]

    def execute_child(self, child_index=0, **kwargs):
        if self.child_executor in {None}:
            return self.child_workflows[child_index].run(**kwargs)
        else:
            return self.child_executor(
                self.child_workflows[child_index], **kwargs
            ).execute()

    def get_command_child(self, child_index=0, **kwargs):
        """Child executor should obviously be compatible with the get_command method."""
        return self.child_executor(
            self.child_workflows[child_index], **kwargs
        ).get_command()

    def get_command(self, **kwargs):
        return [
            self.get_command_child(child_index=i, **kwargs)
            for i in range(self.n_child_workflows)
        ]


class DaskExecutor(Executor):
    # I don't need the functionality from CompositeExecutor
    # I'm simply going to implement the execute method
    def __init__(self, flows, executor, scheduler, show_progress=False):
        self.flows = flows
        self.executor = executor
        self.scheduler = scheduler
        self.show_progress = show_progress

    def execute(self, **executor_options):
        with Client(self.scheduler) as client:
            futures = []
            for flow in self.flows:
                executor = self.executor(flow, **executor_options)
                future = client.submit(executor.execute, executor, pure=False)
                futures.append(future)
            with tqdm(total=len(futures)) as pbar:
                for future, _ in distributed.as_completed(
                    futures, with_results=True, raise_errors=False
                ):
                    pbar.update(1)
                    f: Future = future
                    if f.exception() is not None:
                        traceback.print_tb(f.traceback())
                        print(f.exception())


class JoblibExecutor(CompositeExecutor):
    def __init__(self, workflows, executor, n_jobs=1, verbose=0):
        self.n_jobs = n_jobs
        self.verbose = verbose
        super().__init__(workflows, executor)
        return

    def execute(self, n_jobs=None, **kwargs):
        if n_jobs is None:
            n_jobs = self.n_jobs

        return Parallel(n_jobs=n_jobs, verbose=self.verbose)(
            delayed(self.execute_child)(child_index=i, **kwargs)
            for i in range(self.n_child_workflows)
        )


class GNUParallelExecutor:
    executors = dict(shell_command=ShellCommandExecutor)

    # You need shell commands from your children flows, so there's two ways of extracting them.
    extractors = dict(
        shell_now=ShellExecutor,
        shell_log_autonomous=DTAIExperimenterShellExecutor,
    )

    def __init__(
        self,
        workflows,
        n_jobs=1,
        child_logs=True,
        logs=False,
        flow_commands_filepath="commands.txt",
        nodefile_filepath="nodefile.txt",
        executor=None,
        use_nodes=False,
        progress=False,
        desired_memory_per_thread=8,
        desired_nb_threads=None,
        max_percentage_thread_claim=50,
        machine_kinds={"pinac", "himec", "cudos"},
        claim_policy="greedy",
        username="user",
        **flow_commands_extractor_kwargs,
    ):
        self.n_jobs = n_jobs
        self.use_nodes = use_nodes
        self.progress = progress
        self.logs = logs
        self.child_logs = child_logs
        self.flow_commands_extractor = self.set_flow_commands_extractor(self.child_logs)
        self.flow_commands = self.set_flow_commands(
            workflows, self.flow_commands_extractor, **flow_commands_extractor_kwargs
        )
        self.flow_commands_filepath = self.set_flow_commands_filepath(
            flow_commands_filepath
        )
        self.flow_commands_dumped = dump_object(
            self.flow_commands, self.flow_commands_filepath
        )

        if self.use_nodes:
            self.nodefile = self.set_nodefile(
                self.use_nodes,
                desired_memory_per_thread=desired_memory_per_thread,
                desired_nb_threads=desired_nb_threads,
                max_percentage_thread_claim=max_percentage_thread_claim,
                machine_kinds=machine_kinds,
                claim_policy=claim_policy,
                username=username,
            )
            self.nodefile_filepath = self.set_nodefile_filepath(
                self.use_nodes, nodefile_filepath
            )
            self.nodefile_dumped = dump_object(self.nodefile, self.nodefile_filepath)

        # GNU-parallel command generation and execution
        self.command = self.set_command()
        self.executor = self.set_executor(executor, self.logs)

        return

    def set_flow_commands_extractor(self, child_logs=True):
        if child_logs:
            return self.extractors.get("shell_log_autonomous")
        else:
            return self.extractors.get("shell_now")

    def set_executor(self, executor, logs):
        if executor is not None:
            r = executor
        elif isinstance(executor, str):
            r = self.executors.get(executor)
        else:
            if logs:
                raise NotImplementedError(
                    "Getting a command as input and logging immediately is sth I have yet to manage."
                )
            else:
                r = self.executors.get("shell_command")
        return r

    @staticmethod
    def set_flow_commands(workflows, flow_commands_extractor, **kwargs):
        extractor = CompositeExecutor(workflows, flow_commands_extractor)
        return extractor.get_command(**kwargs)

    @staticmethod
    def set_flow_commands_filepath(flow_commands_filepath):
        assert isinstance(flow_commands_filepath, str)
        r = flow_commands_filepath
        return r

    @staticmethod
    def set_nodefile(
        use_nodes,
        desired_memory_per_thread=8,
        desired_nb_threads=None,
        max_percentage_thread_claim=50,
        machine_kinds={"pinac", "himec", "cudos"},
        claim_policy="greedy",
        username="user",
    ):
        assert (
            use_nodes
        ), "Somehow you are asking for a nodefile, whilst you do not want to use nodes. Something is wrong."
        return generate_nodefile(
            df=None,
            desired_memory_per_thread=desired_memory_per_thread,
            desired_nb_threads=desired_nb_threads,
            max_percentage_thread_claim=max_percentage_thread_claim,
            kinds=machine_kinds,
            claim_policy=claim_policy,
            username=username,
        )

    @staticmethod
    def set_nodefile_filepath(use_nodes, nodefile_filepath):
        if use_nodes:
            assert isinstance(nodefile_filepath, str)
            r = nodefile_filepath
        else:
            # Do not use nodes => no need for nodefile_filepath
            r = None
        return r

    def set_command(self):
        progress_clause = "--progress" if self.progress else ""

        if self.use_nodes:
            r = "parallel --gnu --sshloginfile {0} -a {1} {2}".format(
                self.nodefile_filepath, self.flow_commands_filepath, progress_clause
            )
        else:
            r = "parallel --gnu --jobs {0} -a {1} {2}".format(
                self.n_jobs, self.flow_commands_filepath, progress_clause
            )

        return r

    def execute(self, **kwargs):
        # N.b. this may seem like overkill, but then again, I already have implemented a shellcommand executor, so this does make sense.
        return self.executor(self.command, **kwargs).execute()
