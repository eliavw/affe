from ..monitor import ProcessMonitor

from typing import Optional, Tuple, Dict, Any

class PushToRemote(ProcessMonitor):
    def __init__(
        self,
        host: str = None,
        port: int = None,
        keep_alive: int = None,
        msg_queue_size: int = None,
        tunnel: str = None,
    ) -> None:
        self.port = ...  # type: int
        self.host = ...  # type: str
        self.context = ...  # type: Any
        self.socket = ...  # type: Any
        self.node = ...  # type: str
        self.unique_node = ...  # type: str
        self.linger = ...  # type: int
        self.msg_queue_size = ...  # type: int
        self.tunnel = ...  # type: str
        ...
    def _set_up(self, parent: Any, popen_args: dict = None) -> None: ...
    def _tear_down(self, returncode: int) -> None: ...
    def get_log(self, msg: str, identifier: int) -> None: ...
