from queue import Queue
from logging import Logger
from multiprocessing.queues import Queue as MPQueue

from typing import Optional, Tuple, Dict, Any, Union

class Bunch:
    def __init__(self, *args, **kwargs) -> None: ...
    def __getattr__(self, name: str) -> Any: ...

levels = ...  # type: Bunch
level_prefix = ...  # type: Dict[int, str]

class Timeout(Exception):
    def __init__(self, msg: str) -> None: ...

class Timer(object):
    def __init__(
        self,
        description: str,
        logger: Logger,
        time_format: str = "{:.3f} seconds",
        max_time: int = 0,
    ) -> None:
        self._max_time = ...  # type: int
        self._exec_time = None  # type: float
        self._time_format = ...  # type: str
        self._logger = ...  # type: Logger
        self._start_time = ...  # type: float
        self._description = ...  # type: str
        ...
    @property
    def total_time(self) -> float: ...
    def __enter__(self) -> "Timer": ...
    def __exit__(self, *args) -> None: ...
    def on_time_out(self, *args) -> None: ...

def wait_until_queue_empty(
    queue: Union[Queue, MPQueue], timeout: float = 5
) -> None: ...

class MPStream(MPQueue):
    def __init__(self):
        self.line = ...  # type: str
        self.closed = ...  # type: bool
    def write(self, b: str) -> int: ...
    def flush(self) -> None: ...
    def readline(self) -> str: ...
    def wait_until_empty(self, timeout: float) -> None: ...
    def close(self) -> None: ...
