# -*- coding: utf-8 -*-
from pkg_resources import DistributionNotFound, get_distribution

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version

    from . import io, utils, execs, cli, demo
    from .flow import Flow
    from .execs import (
        DTAIExperimenterFunctionExecutor,
        DTAIExperimenterProcessExecutor,
        NativeExecutor,
    )


except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound
