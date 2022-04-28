import logging
from typing import List

from gptcx import console
from gptcx.gpx import compose_output_gpx
from gptcx.gpx import get_gpx_attributes
from gptcx.gpx import get_gpx_creator
from gptcx.gpx import get_track
from gptcx.gpx import get_track_extensions
from gptcx.gpx import get_track_name
from gptcx.gpx import get_track_point_field
from gptcx.gpx import get_track_points
from gptcx.gpx import GPX
from gptcx.gpx import interpolate_zero_hr
from gptcx.gpx import read_gpx
from gptcx.gpx import write_gpx
from gptcx.tcx import TCX
from gptcx.utils import read_xml


logger = logging.getLogger(__name__)


def merge(gptcx_files: List[str], output_file: str, filter_zeros: bool = False):
    """Merges GPX and TCX files

    Args:
        gptcx_files (List[str]): _description_
        output_file (str): _description_
        filter_zeros (bool, optional): _description_. Defaults to False.
    """
    # # TODO
    # gpx_attributes = {}
    # all_extensions = []
    all_track_points = []

    for gptcx_file in gptcx_files:
        console.print(f"Reading file: [magenta]{gptcx_file}[/magenta]")

        if gptcx_file.endswith(".gpx"):
            gpx = GPX.from_file(gptcx_file)
        elif gptcx_file.endswith(".tcx"):
            gpx = GPX(TCX.from_file(gptcx_file).to_gpx())

        # GPX
        console.print(f"Creator: [magenta]{gpx.creator}[/magenta]")

        # # TODO
        # gpx_attributes.update(get_gpx_attributes(doc))
        # logger.debug(f"GPX Attributes: {gpx_attributes}")

        # Tracks
        track_points = []
        for track in gpx.tracks:
            console.print(f"Track Name: [magenta]{track.name}[/magenta]")

            # # TODO
            # track_extensions = get_track_extensions(track)
            # all_extensions.append(track_extensions)
            # logger.debug(f"Track Extensions: {track_extensions.toprettyxml()}")

        # Track Points
        track_points = gpx.track_points
        logger.debug(f"Found {len(track_points)} track points")
        logger.debug(f"From: {track_points[0].time} to {track_points[-1].time}")

        # Store all the track points and their times
        all_track_points.extend(track_points)

    # Posprocessing
    # 1. sort all points based on its time
    sorted_track_points = sorted(all_track_points, key=lambda x: x.time)

    # TODO
    # # 2. Interpolate zero heart rate measurements
    # if filter_zeros:
    #     sorted_track_points = interpolate_zero_hr(sorted_track_points)

    # 3. compose the document

    # # TODO:
    # gpx_attributes["creator"] = "JMRF"
    # doc = compose_output_gpx(
    #     gpx_attributes, track_name, all_extensions, sorted_track_points
    # )

    merged = GPX.from_track_points(sorted_track_points)
    console.print(f"[AFTER] Total {len(merged.track_points)} track points")

    # 4. Write file
    merged.to_file(output_file)


def xml_merge(gptcx_files: List[str], output_file: str, filter_zeros: bool = False):
    """Merges GPX and TCX files by manipulating its XML structure directly

    Args:
        gptcx_files (List[str]): _description_
        output_file (str): _description_
        filter_zeros (bool, optional): _description_. Defaults to False.
    """
    track_name = ""
    all_extensions = []
    all_track_points = []
    gpx_attributes = {}
    for gptcx_file in gptcx_files:
        console.print(f"Reading file: [magenta]{gptcx_file}[/magenta]")

        if gptcx_file.endswith(".gpx"):
            doc = read_gpx(gptcx_file)
        elif gptcx_file.endswith(".tcx"):
            doc = read_xml(gptcx_file)

        # GPX
        creator = get_gpx_creator(doc)
        gpx_attributes.update(get_gpx_attributes(doc))
        console.print(f"Creator: [magenta]{creator}[/magenta]")
        logger.debug(f"GPX Attributes: {gpx_attributes}")

        # Track
        track = get_track(doc)
        track_name = track_name or get_track_name(track)
        console.print(f"Track Name: [magenta]{track_name}[/magenta]")

        # Track extensions
        try:
            track_extensions = get_track_extensions(track)
            logger.debug(f"Track Extensions: {track_extensions.toprettyxml()}")
            all_extensions.append(track_extensions)
        except AttributeError:
            pass

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
