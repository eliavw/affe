import argparse
import os


def get_flow_cli(abs=True):
    if abs:
        return __file__
    else:
        return os.path.relpath(__file__, start=os.getcwd())


# Main
def main(flow_filepath, verbosity=1):

    # Imports need to happen like this, otherwise we turn circles.
    import affe
    from affe.flow import load_flow
    from affe.utils import debug_print

    flow = load_flow(flow_filepath)
    flow.run_with_imports()

    msg = """
    I am running the general-purpose flow script.
    """
    debug_print(msg, level=1, v=verbosity)
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
