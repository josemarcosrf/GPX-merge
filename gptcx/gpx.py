import logging
import re
import gpxpy

from tempfile import NamedTemporaryFile
from typing import Any
from typing import Dict
from typing import List
from typing import Text
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from gptcx.utils import interpolate_zeros


logger = logging.getLogger(__name__)


class GPX:
    def __init__(self, gpx: gpxpy.gpx.GPX) -> None:
        self.gpx = gpx

    @classmethod
    def from_file(cls, gpx_path: str):
        try:
            with open(gpx_path, "r") as f:
                return cls(gpxpy.parse(gpx_path))
        except Exception as e:
            logger.error(f"Error reading gpx file: {e}")
            raise e

    def _extract_track_points(self):
        points = []
        for track in self.gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(
                        ({point.latitude}, {point.longitude}),
                        point.elevation,
                        point.time,
                        None,  # TODO: Heart Rate data
                    )

    def to_file(self, output_path: str):
        """Write GPX object to file (XML format)."""
        logger.info(f"Writting GPX to: {output_path}")
        with open(output_path, "w", encoding="utf8") as f:
            f.write(self.gpx.to_xml())


GPX_TAG = "gpx"
CREATOR_TAG = "creator"
GPX_TRACK_TAG = "trk"
TRACK_NAME_TAG = "name"
TRACK_SEGMENT_TAG = "trkseg"
TRACK_EXTENSIONS_TAG = "extensions"
GPX_TRACKPOINT_TAG = "trkpt"
TRACKPOINT_HEART_RATE_TAG = "gpxtpx:hr"
METADATA_TAG = "metadata"

TCX_TRACK_TAG = "Track"
TCX_TRACKPOINT_TAG = "Trackpoint"
TCX_TRACKPOINT_TIME = "Time"
TCX_TRACKPOINT_ALT = "AltitudeMeters"
TCX_TRACKPOINT_DIST = "DistanceMeters"
TCX_TRACKPOINT_HR = "HeartRateBpm"

UNKNOWN_TAG = "UNK"


def read_gpx(gpx_file: Text) -> minidom.Document:
    try:
        doc = minidom.parse(gpx_file)
        return doc
    except ExpatError:
        try:
            # Heart Rate data from MATRIX Powerwatch 2 misses
            # the namespace definition for 'gpxtpx' so we add manually
            with open(gpx_file, "r") as f:
                content = f.read()
                content = content.replace(
                    "<trk>", '<trk xmlns:gpxtpx="http://www.example.org/trackpoint/">'
                )

            with NamedTemporaryFile("w", delete=True) as tfile:
                tfile.write(content)
                doc = minidom.parse(tfile.name)
                return doc
        except Exception as e:
            raise e


def _get_elem_field(elem: minidom.Element, field: Text) -> Any:
    return elem.getElementsByTagName(field)[0].childNodes[0].nodeValue


def _get_attribute_dict(xml_node) -> Dict[Text, Any]:
    return {k: v for k, v in xml_node.attributes.items()}


def _xml_to_str(doc):
    xml_str = doc.toprettyxml(indent="  ", newl="\n", encoding=None)
    xml_str = re.sub("[ ]+\n", "", xml_str)
    xml_str = re.sub("[\t]+\n", "", xml_str)

    return xml_str


def get_gpx_attributes(xml_doc: minidom.Document) -> Dict[Text, Any]:
    try:
        gpx = xml_doc.getElementsByTagName(GPX_TAG)[0]
        return _get_attribute_dict(gpx)
    except IndexError:
        return {}


def get_gpx_creator(xml_doc: minidom.Document) -> Text:
    return get_gpx_attributes(xml_doc).get(CREATOR_TAG, UNKNOWN_TAG)


def get_track(xml_doc: minidom.Document, is_tcx: bool = False) -> minidom.Element:
    try:
        if is_tcx:
            return xml_doc.getElementsByTagName(TCX_TRACK_TAG)[0]

        return xml_doc.getElementsByTagName(GPX_TRACK_TAG)[0]
    except IndexError:
        minidom.Element(GPX_TRACK_TAG)


def get_track_name(xml_track: minidom.Element) -> Text:
    try:
        if xml_track.nodeName != GPX_TRACK_TAG:
            raise ValueError(
                f"Received element of type: {xml_track.nodeName}. "
                f"Expected a {GPX_TRACK_TAG}"
            )
        return _get_elem_field(xml_track, TRACK_NAME_TAG)
    except (ValueError, IndexError) as e:
        logger.error(f"Error getting track name: {e}")
        return ""


def get_track_extensions(xml_track: minidom.Element) -> minidom.Element:
    try:
        if xml_track.nodeName != GPX_TRACK_TAG:
            raise ValueError(
                f"Received element of type: {xml_track.nodeName}. "
                f"Expected a {GPX_TRACK_TAG}"
            )
        return xml_track.getElementsByTagName(TRACK_EXTENSIONS_TAG)[0]
    except (ValueError, IndexError) as e:
        logger.error(f"Error getting track extensions: {e}")
        return minidom.Element(TRACK_EXTENSIONS_TAG)


def get_track_points(
    xml_track: minidom.Document, is_tcx: bool = False
) -> minidom.NodeList:
    try:
        if is_tcx:
            if xml_track.nodeName != TCX_TRACK_TAG:
                raise ValueError(
                    f"Received element of type: '{xml_track.nodeName}'. "
                    f"Expected a '{TCX_TRACK_TAG}'"
                )
            return xml_track.getElementsByTagName(TCX_TRACKPOINT_TAG)

        if xml_track.nodeName != GPX_TRACK_TAG:
            raise ValueError(
                f"Received element of type: '{xml_track.nodeName}'. "
                f"Expected a '{GPX_TRACK_TAG}'"
            )
        return xml_track.getElementsByTagName(GPX_TRACKPOINT_TAG)
    except ValueError as e:
        logger.error(f"Error getting track points: {e}")
        return minidom.NodeList()


def get_track_point_field(trk_point: minidom.Element, field: Text) -> Any:
    try:
        valid_nodes = [GPX_TRACKPOINT_TAG, TCX_TRACKPOINT_TAG]
        if trk_point.nodeName not in valid_nodes:
            raise ValueError(
                f"Received element of type: {trk_point.nodeName}. "
                f"Expected one of {valid_nodes}"
            )
        return trk_point.getElementsByTagName(field)[0].childNodes[0].nodeValue
    except (ValueError, IndexError) as e:
        logger.error(f"Error getting track point field '{field}': {e}")
        return minidom.NodeList()


def interpolate_zero_hr(track_points: List[minidom.Element]) -> List[minidom.Element]:
    try:
        types = {trk_point.nodeName for trk_point in track_points}
        if any([t != GPX_TRACKPOINT_TAG for t in types]):

            raise ValueError(
                f"Received a list with invalid elements ({types}). "
                f"Expected all to be of type: {GPX_TRACKPOINT_TAG}"
            )

        heart_rates = []
        hr_indices = []
        for i, trk_point in enumerate(track_points):
            hr = trk_point.getElementsByTagName(TRACKPOINT_HEART_RATE_TAG)
            if hr:
                hr_indices.append(i)
                heart_rates.append(int(hr[0].childNodes[0].nodeValue))

        interpolated = interpolate_zeros(heart_rates, missing_value=0)

        assert all([x != 0 for x in interpolated])

        for index, new_hr in zip(hr_indices, interpolated):
            hr = track_points[index].getElementsByTagName(TRACKPOINT_HEART_RATE_TAG)
            hr[0].childNodes[0].nodeValue = str(new_hr)

            assert new_hr != 0

            assert (
                int(
                    get_track_point_field(
                        track_points[index], field=TRACKPOINT_HEART_RATE_TAG
                    )
                )
                != 0
            )

        return track_points

    except (ValueError, IndexError) as e:
        logger.error(f"Error interpolating heart rates: {e}. Returning untouched list")

    return track_points


def compose_output_gpx(
    gpx_attributes: Dict[Text, Text],
    track_name: Text,
    track_extensions_list: List[minidom.Element],
    track_points: List[minidom.Element],
):
    doc = minidom.Document()

    # Create and set GPX attributes
    gpx = doc.createElement(GPX_TAG)
    for k, v in gpx_attributes.items():
        gpx.setAttribute(k, v)

    # TODO: Add metadata to the GPX object

    # Create a Track
    track = doc.createElement(GPX_TRACK_TAG)
    track.setAttribute(TRACK_NAME_TAG, track_name)

    # Create track extensions and add to the Track
    extensions = doc.createElement(TRACK_EXTENSIONS_TAG)
    track.appendChild(extensions)
    for track_extensions in track_extensions_list:
        for extension in track_extensions.childNodes:
            if extension.nodeType != 3:  # skip text nodes
                extensions.appendChild(extension)

    # Create a Track Segment and add Track Points
    track_segment = doc.createElement(TRACK_SEGMENT_TAG)
    for track_point in track_points:
        track_segment.appendChild(track_point)

    # Add the GPX to the document
    track.appendChild(track_segment)
    gpx.appendChild(track)
    doc.appendChild(gpx)

    return doc


def write_gpx(file_path: Text, doc: minidom.Document):
    with open(file_path, "w") as f:
        f.write(_xml_to_str(doc))
