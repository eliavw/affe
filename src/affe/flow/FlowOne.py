from pathlib import Path

from .Flow import Flow
import uuid

class FlowOne(Flow):
    def __init__(self, experiment_identifier=None,flow_identifier = None, root_levels_up=2, out_dp=None, **kwargs):
        self.flow_identifier = flow_identifier
        self.experiment_identifier = experiment_identifier
        # Filesystem parameters. You can explicitly specify an out directory, but you do not have to.
        self.root_levels_up = root_levels_up
        self.out_dp = out_dp

        # Ensure existence of your directories
        self.check_filesystem()

        super().__init__(
            log_filepath=str(self.log_fp), flow_filepath=str(self.flow_fp), **kwargs
        )
        return

    def check_filesystem(self):
        """
        Verify the existence of the directories in your filesystem.
        """
        self._log_dp.mkdir(parents=True, exist_ok=True)
        self._flow_dp.mkdir(parents=True, exist_ok=True)
        return

    # Bookkeeping
    @property
    def experiment_identifier(self):
        return self._experiment_identifier

    @experiment_identifier.setter
    def experiment_identifier(self, value):
        if isinstance(value, str):
            self._experiment_identifier = value
        elif value is None:
            self._experiment_identifier = self._default_experiment_identifier
        else:
            raise ValueError("Identifier needs to be string.")

    @property
    def _default_experiment_identifier(self):
        return self.__class__.__name__

    @property
    def flow_identifier(self):
        return self._flow_identifier

    @flow_identifier.setter
    def flow_identifier(self, value):
        if isinstance(value, str):
            self._flow_identifier = value
        elif value is None:
            self._flow_identifier = self._default_flow_identifier
        else:
            raise ValueError("Identifier needs to be string.")

    @property
    def _default_flow_identifier(self):
        return f"flow_{uuid.uuid4().hex}"

    # Filesystem-MGMT
    @property
    def root_dp(self):
        """Root directory path"""
        return Path().absolute().parents[self.root_levels_up - 1]

    @property
    def out_dp(self):
        return self._out_dp

    @out_dp.setter
    def out_dp(self, value):
        if isinstance(value, Path):
            self._out_dp = value
        elif isinstance(value, str):
            self._out_dp = Path(value)
        elif value is None:
            self._out_dp = self._default_out_dp
        else:
            raise ValueError("out_dp needs to be string.")

    @property
    def _default_out_dp(self):
        return self.root_dp / "out"

    @property
    def out_exp_dp(self):
        return self.out_dp/self.experiment_identifier

    @property
    def _flow_dp(self):
        """Flow dirpath"""
        return self.out_exp_dp / "flow"

    @property
    def _log_dp(self):
        """Log dirpath"""
        return self.out_exp_dp / "log"

    @property
    def flow_fp(self):
        """Flow filepath"""
        return self._flow_dp / (self.flow_identifier + ".pkl")

    @property
    def log_fp(self):
        """Log filepath"""
        return self._log_dp / self.flow_identifier
