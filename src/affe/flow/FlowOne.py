from pathlib import Path

from .Flow import Flow


class FlowOne(Flow):
    def __init__(self, identifier=None, root_levels_up=2, out_dp=None, **kwargs):
        self.identifier = identifier

        # Filesystem parameters. You can explicitly specify an out directory, but you do not have to.
        self.root_levels_up = root_levels_up
        self.out_dp = out_dp

        # Ensure existence of your directories
        self._log_dp.mkdir(parents=True, exist_ok=True)
        self._flow_dp.mkdir(parents=True, exist_ok=True)

        super().__init__(
            log_filepath=str(self.log_fp), flow_filepath=str(self.flow_fp), **kwargs
        )
        return

    # Bookkeeping
    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        if isinstance(value, str):
            self._identifier = value
        elif value is None:
            self._identifier = self._default_identifier
        else:
            raise ValueError("Identifier needs to be string.")

    @property
    def _default_identifier(self):
        return self.__class__.__name__

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
        return self.root_dp / "out" / self.identifier

    @property
    def _flow_dp(self):
        """Flow dirpath"""
        return self.out_dp / "flow"

    @property
    def _log_dp(self):
        """Log dirpath"""
        return self.out_dp / "log"

    @property
    def flow_fp(self):
        """Flow filepath"""
        return self._flow_dp / (self.identifier + ".pkl")

    @property
    def log_fp(self):
        """Log filepath"""
        return self._log_dp / self.identifier
