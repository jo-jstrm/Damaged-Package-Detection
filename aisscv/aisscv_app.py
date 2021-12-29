import argparse
import sys

__version__ = "0.0.1"


def get_args():
    """Parses the CLI arguments

    Returns
    -------
    Namespace
        Contains all arguments
    """
    parser = argparse.ArgumentParser(
        description='''This is our AISS-CV project.''',
        epilog="""This is a work in progress.""")
    parser.add_argument('--question', type=str, default="",
                        help='Type your question.')
    # parser.add_argument('bar', nargs='*', default=[1, 2, 3], help='BAR!')

    return parser.parse_args()


def main():
    """Entry point of the program."""
    try:
        args = get_args()
        question = args.question

        print("Executing AISS-CV project version %s" % __version__)

        if(question == ""):
            print("Please type a question")
        else:
            print("Your question was: %s" % question)
    except:
        print('Could not parse args')
