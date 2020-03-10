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
