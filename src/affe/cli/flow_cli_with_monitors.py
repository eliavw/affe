import argparse
import os
from functools import partial


def get_flow_cli_with_monitors(abs=True):
    if abs:
        return __file__
    else:
        return os.path.relpath(__file__, start=os.getcwd())


# MAIN
def main(flow_filepath, log_filepath, timeout_s=60, verbosity=1):

    # Imports need to happen like this, otherwise we turn circles.
    import affe
    from affe.flow import load_flow
    from affe.utils import debug_print
    from affe.executors import get_monitors
    from affe.dtaiexperimenter import Process, Function

    f = load_flow(flow_filepath)
    cmd = f.get_cli_command(
        executable=None
    )  # You are not going to let this script CHANGE the executable!
    monitors = get_monitors(log_filepath, timeout_s)

    cwd = os.getcwd()
    executor = Process(cmd, monitors=monitors, cwd=cwd)  # Init Process

    # flow_initialized = partial(f.flow, f.config)
    # executor = Function(flow_initialized, monitors=monitors)

    msg = """
    Done running the general-purpose monitored flow script.
    """
    debug_print(msg, level=1, v=verbosity)
    return executor.run()


# CLI
def create_parser():
    # Create the parser
    parser = argparse.ArgumentParser(description="Get the flow filepath")

    parser.add_argument(
        "-f",
        "--flow_filepath",
        action="store",
        type=str,
        required=True,
        help="Filename of dumped flow (by definition, this contains literally everything).",
    )

    parser.add_argument(
        "-l",
        "--log_filepath",
        action="store",
        type=str,
        required=True,
        help="Filename of logfile.",
    )

    parser.add_argument(
        "-t",
        "--timeout_s",
        action="store",
        type=int,
        required=True,
        help="Timeout in seconds.",
    )

    return parser


# For executable script
if __name__ == "__main__":

    parser = create_parser()
    args = parser.parse_args()

    flow_filepath_outer_scope = args.flow_filepath
    log_filepath_outer_scope = args.log_filepath
    timeout_s_outer_scope = args.timeout_s

    main(
        flow_filepath_outer_scope,
        log_filepath_outer_scope,
        timeout_s=timeout_s_outer_scope,
    )
