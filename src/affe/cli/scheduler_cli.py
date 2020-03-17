import argparse
import os

SCRIPT_FILENAME = os.path.basename(__file__)


def get_scheduler_cli(abs=True):
    if abs:
        return __file__
    else:
        return os.path.relpath(__file__, start=os.getcwd())


# Main
def main(flow_index, scheduler_filepath, verbosity=1):
    msg = """
    Start {}.
    """.format(
        SCRIPT_FILENAME
    )
    print(msg)

    # Standard imports
    import affe
    from affe.flow import Flow
    from affe.execs import ShellCommandExecutor

    # Get flow
    scheduler = Flow.load(scheduler_filepath)
    flow_command = scheduler.commands[flow_index]

    # Flow prerequisites (typically custom imports)
    if scheduler.imports_source_code is not None:
        exec(scheduler.imports_source_code)

    # Run Flow
    executor = ShellCommandExecutor(flow_command)
    executor.execute()

    msg = """
    Done {}.
    """.format(
        SCRIPT_FILENAME
    )
    print(msg)
    return


# CLI
def create_parser():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Get the flow index and scheduler filepath."
    )

    parser.add_argument(
        "-i",
        "--flow index",
        action="store",
        type=int,
        required=True,
        default=0,
        help="The scheduler encompasses multiple flows. This index indicates which one to run.",
    )

    parser.add_argument(
        "-f",
        "--scheduler_filepath",
        action="store",
        type=str,
        required=True,
        help="Filename of dumped flow (by definition, this contains literally everything).",
    )

    return parser


# For executable script
if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    flow_index_outer_scope = args.flow_index
    scheduler_filepath_outer_scope = args.scheduler_filepath
    main(flow_index_outer_scope, scheduler_filepath_outer_scope)
