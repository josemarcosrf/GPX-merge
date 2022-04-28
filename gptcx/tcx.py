import logging
from datetime import datetime
from itertools import zip_longest
from typing import List

import coloredlogs
import dateutil.parser
import gpxpy
from tcxparser import TCXParser

from gptcx import Point
from gptcx.gpx import GPX


logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger, level=logging.DEBUG)


class TCX:
    def __init__(self, tcx: TCXParser = None) -> None:
        self.tcx = tcx

    @classmethod
    def from_file(cls, tcx_path):
        """
        Read a TCX file.
        """
        try:
            logger.info(f"Reading tcx: {tcx_path}")
            return cls(TCXParser(tcx_path))

        except Exception as e:
            logger.error(f"Error reading tcx file: {e}")
            raise e

    @property
    def track_points(self):
        return self._extract_track_points()

    def _extract_track_points(self) -> List[Point]:
        """Extract and combine features from tcx"""
        try:
            return [
                Point(pos, alt, t, hr)
                for pos, alt, t, hr in zip_longest(
                    self.tcx.position_values(),
                    self.tcx.altitude_points(),
                    self.tcx.time_values(),
                    self.tcx.hr_values(),
                )
            ]
        except Exception as e:
            logger.error(f"Error extracting TCX track points: {e}")

    def to_gpx(self, gpx_name: str = "", description: str = "") -> GPX:
        """
        Create GPX object.
        """
        logger.info(f"Creating GPX from TCX")
        _gpx = gpxpy.gpx.GPX()
        _gpx.name = gpx_name
        _gpx.description = description

        # start_time = dateutil.parser.parse(self.tcx.started_at).strftime(
        #     "%Y-%m-%d %H:%M:%S"
        # )
        gpx_track = gpxpy.gpx.GPXTrack(name=gpx_name, description=description)
        gpx_track.type = self.tcx.activity_type

        # gpx_track.extensions = '<topografix:color>c0c0c0</topografix:color>'
        _gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        for pos, alt, t, hr in self._extract_track_points():
            tp_time = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.000Z")
            lat = pos[0] if pos else None
            lon = pos[1] if pos else None
            gpx_trackpoint = gpxpy.gpx.GPXTrackPoint(
                latitude=lat,
                longitude=lon,
                elevation=alt,
                time=tp_time,
            )
            gpx_segment.points.append(gpx_trackpoint)

        return _gpx

    def to_file(self, output_path: str):
        raise NotImplementedError("TCX.to_file not implemented yet!")


if __name__ == "__main__":
    import sys

    tcx = TCX.from_file(sys.argv[1])
    GPX(tcx.to_gpx()).to_file(sys.argv[2])
