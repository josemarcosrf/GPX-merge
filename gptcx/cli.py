import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input-dir", help="Input directory with GPX files to merge")
    parser.add_argument("output-file", help="Output GPX merged file")
    parser.add_argument(
        "--filter-zeros", action="store_true", help="Filter heart rate zero values"
    )
    parser.add_argument("--debug", action="store_true", help="Log level to DEBUG")
    return parser.parse_args()
