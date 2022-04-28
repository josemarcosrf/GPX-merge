import logging

from gptcx import console
from gptcx.gpx import compose_output_gpx
from gptcx.gpx import get_gpx_attributes
from gptcx.gpx import get_gpx_creator
from gptcx.gpx import get_track
from gptcx.gpx import get_track_extensions
from gptcx.gpx import get_track_name
from gptcx.gpx import get_track_point_field
from gptcx.gpx import get_track_points
from gptcx.gpx import interpolate_zero_hr
from gptcx.gpx import read_gpx
from gptcx.gpx import write_gpx

from typing import List


logger = logging.getLogger(__name__)


def old_merge(gptcx_files: List[str], output_file: str, filter_zeros: bool = False):
    track_name = ""
    all_extensions = []
    all_track_points = []
    gpx_attributes = {}
    for gptcx_file in gptcx_files:
        console.print(f"Reading file: [magenta]{gptcx_file}[/magenta]")

        # GPX
        doc = read_gpx(gptcx_file)
        creator = get_gpx_creator(doc)
        gpx_attributes.update(get_gpx_attributes(doc))
        console.print(f"Creator: [magenta]{creator}[/magenta]")
        logger.debug(f"GPX Attributes: {gpx_attributes}")

        # Track
        track = get_track(doc)
        track_name = track_name or get_track_name(track)
        track_extensions = get_track_extensions(track)

        all_extensions.append(track_extensions)

        console.print(f"Track Name: [magenta]{track_name}[/magenta]")
        logger.debug(f"Track Extensions: {track_extensions.toprettyxml()}")

        # Track Points
        track_points = get_track_points(track)
        console.print(f"Found {len(track_points)} track points")

        # Times
        times = [get_track_point_field(trkpt, field="time") for trkpt in track_points]
        logger.debug(f"From: {times[0]} to {times[-1]}")

        # Store all the track points and their times
        all_track_points.extend(zip(track_points, times))

    # Posprocessing

    # 1. sort all points based on its time
    sorted_track_points = [tp[0] for tp in sorted(all_track_points, key=lambda x: x[1])]

    # 2. Interpolate zero heart rate measurements
    if filter_zeros:
        sorted_track_points = interpolate_zero_hr(sorted_track_points)

    # 3. compose the document
    gpx_attributes["creator"] = "JMRF"
    doc = compose_output_gpx(
        gpx_attributes, track_name, all_extensions, sorted_track_points
    )

    # 4. Write file
    write_gpx(output_file, doc)
