import argparse
import whereamicloud


def main(assigned_args: list = None):
    """
    Parse and execute the call from command-line

    Args:
        assigned_args: List of strings to parse
        The default is taken from sys.argv

    Returns:
        Closest node tests
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="whereamicloud",
        description="""
        Pings hosts inside locations.json to
        infer its own location based on response time"""
    )
    parser.add_argument(
        "--version",
        action="version",
        version=whereamicloud.__version__
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Make output less verbose."
    )

    args = parser.parse_args(assigned_args)

    whereamicloud.QUIET = args.quiet

    whereamicloud.main()


if __name__ == "__main__":
    main()
