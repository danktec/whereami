import argparse
import whereami

def main(assigned_args: list = None):
    """
    Parse and execute the call from command-line.

    Args:
        assigned_args: List of strings to parse. The default is taken from sys.argv.

    Returns:
        Closest node tests.
    """
    parser = argparse.ArgumentParser(prog="whereami", description="test", epilog="Test")
    parser.add_argument("--version", action="version", version=whereami.__version__)
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="Verbose output mode.")

    args = parser.parse_args(assigned_args)
    whereami.QUIET = args.quiet

    whereami.main()

if __name__ == "__main__":
    main()