import copy
import glob
import logging
import os
from typing import List, Text

from gpx_merge import configure_colored_logging
from gpx_merge import console
from gpx_merge.cli import get_args
from gpx_merge.gpx import compose_output_gpx
from gpx_merge.gpx import get_gpx_attributes
from gpx_merge.gpx import get_gpx_creator
from gpx_merge.gpx import get_track
from gpx_merge.gpx import get_track_extensions
from gpx_merge.gpx import get_track_name
from gpx_merge.gpx import get_track_point_field
from gpx_merge.gpx import get_track_points
from gpx_merge.gpx import interpolate_zero_hr
from gpx_merge.gpx import read_gpx
from gpx_merge.gpx import write_gpx


logger = logging.getLogger(__name__)


def find_files(gpx_dir: Text, extensions: List[str]):
    found = []
    for ext in extensions:
        found.extend(glob.glob(os.path.join(gpx_dir, f"*.{ext}")))

    return found


if __name__ == "__main__":

    args = get_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    configure_colored_logging(level=log_level)

    track_name = ""
    all_extensions = []
    all_track_points = []
    gpx_attributes = {}
    for gpx_file in find_files(args.input_dir, extensions=["gpx", "tcx"]):
        console.print(f"Reading file: [magenta]{gpx_file}[/magenta]")

        is_tcx = gpx_file.endswith(".tcx")
        time_field = "Time" if is_tcx else "time"

        console.print(f"Is TCX: [magenta]{is_tcx}[/magenta]")

        # GPX
        doc = read_gpx(gpx_file)
        creator = get_gpx_creator(doc)
        gpx_attributes.update(get_gpx_attributes(doc))
        console.print(f"Creator: [magenta]{creator}[/magenta]")
        logger.debug(f"GPX Attributes: {gpx_attributes}")

        # Track
        track = get_track(doc, is_tcx=is_tcx)
        track_name = track_name or get_track_name(track)
        track_extensions = get_track_extensions(track)

        all_extensions.append(track_extensions)

        console.print(f"Track Name: [magenta]{track_name}[/magenta]")
        logger.debug(f"Track Extensions: {track_extensions.toprettyxml()}")

        # Track Points
        track_points = get_track_points(track, is_tcx=is_tcx)
        console.print(f"Found {len(track_points)} track points")

        # Times
        times = [
            get_track_point_field(trkpt, field=time_field)
            for trkpt in track_points
        ]
        logger.debug(f"From: {times[0]} to {times[-1]}")

        # Store all the track points and their times
        all_track_points.extend(zip(track_points, times))

    # Posprocessing

    # 1. sort all points based on its time
    sorted_track_points = [
        tp[0] for tp in sorted(all_track_points, key=lambda x: x[1])
    ]

    # 2. Interpolate zero heart rate measurements
    if args.filter_zeros:
        sorted_track_points = interpolate_zero_hr(sorted_track_points)

    # 3. compose the document
    gpx_attributes["creator"] = "JMRF"
    doc = compose_output_gpx(
        gpx_attributes, track_name, all_extensions, sorted_track_points
    )

    # 4. Write file
    write_gpx(args.output_file, doc)
