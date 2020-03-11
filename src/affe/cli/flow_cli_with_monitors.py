import argparse
import os
from functools import partial

SCRIPT_FILENAME = os.path.basename(__file__)


def get_flow_cli_with_monitors(abs=True):
    if abs:
        return __file__
    else:
        return os.path.relpath(__file__, start=os.getcwd())


# MAIN
def main(flow_filepath, log_filepath, timeout_s=60, verbosity=1):
    msg = """
    Start {}.
    """.format(
        SCRIPT_FILENAME
    )
    print(msg)

    # Standard imports
    import affe
    from affe.flow import Flow
    from affe.execs import DTAIExperimenterProcessExecutor

    # Get flow
    flow = Flow.load(flow_filepath)
    executor = DTAIExperimenterProcessExecutor(
        flow, log_filepath=log_filepath, timeout_s=timeout_s
    )
    result = executor.run()

    msg = """
    Done {}.
    """.format(
        SCRIPT_FILENAME
    )
    print(msg)
    return result


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
