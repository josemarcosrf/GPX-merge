import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dir", help="Input directory with GPX files to merge")
    parser.add_argument("--debug", action="store_true", help="Log level to DEBUG")
    return parser.parse_args()
