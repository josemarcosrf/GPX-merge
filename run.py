import glob
import logging
import os
from typing import List
from typing import Text

from gptcx import configure_colored_logging
from gptcx.cli import get_args
from gptcx.merge import xml_merge as merge


logger = logging.getLogger(__name__)


def find_files(gpx_dir: Text, extensions: List[str]):
    found = []
    for ext in extensions:
        found.extend(glob.glob(os.path.join(gpx_dir, f"*.{ext}")))

    return found


def main():
    args = get_args()
    # logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    configure_colored_logging(level=log_level)
    # gather
    gptcx_files = find_files(args.input_dir, extensions=["gpx", "tcx"])
    # merge
    merge(gptcx_files, args.output_file, args.filter_zeros)


if __name__ == "__main__":
    main()
