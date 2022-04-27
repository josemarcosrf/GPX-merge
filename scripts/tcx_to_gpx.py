import coloredlogs
import dateutil.parser
import logging

from datetime import datetime
from gpxpy import gpx
from itertools import zip_longest
from tcxparser import TCXParser


logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger, level=logging.DEBUG)


def read_tcx(tcx_path):
    """
    Read a TCX file.
    """
    try:
        logger.info(f"Reading tcx: {tcx_path}")
        tcx = TCXParser(tcx_path)
        return tcx
    except Exception as e:
        logger.error(f"Error reading tcx file: {e}")
        raise e


def extract_track_points(tcx):
    """
    Extract and combine features from tcx
    """
    try:
        return zip_longest(
            tcx.position_values(),
            tcx.altitude_points(),
            tcx.time_values(),
            tcx.hr_values(),
        )
    except Exception as e:
        logger.error(f"Error extracting TCX track points: {e}")


def tcx_to_gpx(tcx, gpx_name: str = "", description: str = ""):
    """
    Create GPX object.
    """
    logger.info(f"Creating GPX from TCX")
    _gpx = gpx.GPX()
    _gpx.name = gpx_name
    _gpx.description = description

    start_time = dateutil.parser.parse(tcx.started_at).strftime("%Y-%m-%d %H:%M:%S")
    gpx_track = gpx.GPXTrack(name=gpx_name, description=description)
    gpx_track.type = tcx.activity_type

    # gpx_track.extensions = '<topografix:color>c0c0c0</topografix:color>'
    _gpx.tracks.append(gpx_track)
    gpx_segment = gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for pos, alt, t, hr in extract_track_points(tcx):
        tp_time = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.000Z")
        lat = pos[0] if pos else None
        lon = pos[1] if pos else None
        gpx_trackpoint = gpx.GPXTrackPoint(
            latitude=lat, longitude=lon, elevation=alt, time=tp_time,
        )
        gpx_segment.points.append(gpx_trackpoint)

    return _gpx


def write_gpx(gpx, output_path: str):
    """
    Write GPX object to file.
    """
    logger.info(f"GPX written to: {output_path}")
    with open(output_path, "w", encoding="utf8") as f:
        f.write(gpx.to_xml())


if __name__ == "__main__":
    import sys

    tcx = read_tcx(sys.argv[1])

    tcx_points = extract_track_points(tcx)
    logger.debug(f"Total TCX points: {len(list(tcx_points))}")

    gpx = tcx_to_gpx(tcx)
    write_gpx(gpx, sys.argv[2])
