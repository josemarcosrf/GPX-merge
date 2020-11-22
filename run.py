import os
import glob

from typing import Text

from gpx_merge import console
from gpx_merge.cli import get_args
from gpx_merge.gpx_utils import read_gpx
from gpx_merge.gpx_utils import get_trk_points
from gpx_merge.gpx_utils import get_trk_point_field


TEST_DIR = "./data/La-Tuca"



def find_files(gpx_dir: Text, ext: Text):
    return glob.glob(os.path.join(gpx_dir, f"*.{ext}"))


if __name__ == "__main__":

    args = get_args()

    times = []
    ind_ind_list = []

    for gpx_file in find_files(args.in_dir, ext="gpx"):

        console.log(f"Reading file: {gpx_file}")
        doc = read_gpx(gpx_file)

        # Read all points in the track
        track_points = get_trk_points(doc)
        console.log(f"Found {len(track_points)} track points")

        # index list
        ind_ind_list.append(list(range(len(track_points))))
        times.extend(
            [get_trk_point_field(trkpt, field="time") for trkpt in track_points]
        )
        console.log(f"From: {times[0]} to {times[-1]}")

        # times = [tp["time"] for tp in trkpts]
        # console.log(f"From {tims[0]} to {times[-1]}")

    # merge track point elements
