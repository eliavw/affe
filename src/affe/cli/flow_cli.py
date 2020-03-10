import argparse
import os

SCRIPT_FILENAME = os.path.basename(__file__)


def get_flow_cli(abs=True):
    if abs:
        return __file__
    else:
        return os.path.relpath(__file__, start=os.getcwd())


# Main
def main(flow_filepath, verbosity=1):
    msg = """
    Start {}.
    """.format(
        SCRIPT_FILENAME
    )
    print(msg)

    # Standard imports
    import affe
    from affe.flow import Flow

    # Get flow
    flow = Flow.load(flow_filepath)

    # Flow prerequisites (typically custom imports)
    if flow.imports_source_code is not None:
        exec(flow.imports_source_code)

    # Run Flow
    flow.run()

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
    parser = argparse.ArgumentParser(description="Get the flow filepath")

    parser.add_argument(
        "-f",
        "--flow_filepath",
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

    flow_filepath_outer_scope = args.flow_filepath
    main(flow_filepath_outer_scope)
