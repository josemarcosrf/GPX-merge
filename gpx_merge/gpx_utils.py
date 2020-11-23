import logging
import re
from tempfile import NamedTemporaryFile
from typing import Any
from typing import Dict
from typing import List
from typing import Text
from xml.dom import minidom
from xml.parsers.expat import ExpatError


logger = logging.getLogger(__name__)


GPX_TAG = "gpx"
CREATOR_TAG = "creator"
TRACK_TAG = "trk"
TRACK_NAME_TAG = "name"
TRACK_SEGMENT_TAG = "trkseg"
TRACK_EXTENSIONS_TAG = "extensions"
TRACKPOINT_TAG = "trkpt"
METADATA_TAG = "metadata"

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


def get_track(xml_doc: minidom.Document) -> minidom.Element:
    try:
        return xml_doc.getElementsByTagName(TRACK_TAG)[0]
    except IndexError:
        minidom.Element(TRACK_TAG)


def get_track_name(xml_track: minidom.Element) -> Text:
    try:
        if xml_track.nodeName != TRACK_TAG:
            raise ValueError(
                f"Received element of type: {xml_track.nodeName}. "
                f"Expected a {TRACK_TAG}"
            )
        return _get_elem_field(xml_track, TRACK_NAME_TAG)
    except (ValueError, IndexError) as e:
        logger.error(f"Error getting track name: {e}")
        return ""


def get_track_extensions(xml_track: minidom.Element) -> minidom.Element:
    try:
        if xml_track.nodeName != TRACK_TAG:
            raise ValueError(
                f"Received element of type: {xml_track.nodeName}. "
                f"Expected a {TRACK_TAG}"
            )
        return xml_track.getElementsByTagName(TRACK_EXTENSIONS_TAG)[0]
    except (ValueError, IndexError) as e:
        logger.error(f"Error getting track extensions: {e}")
        return minidom.Element(TRACK_EXTENSIONS_TAG)


def get_trk_points(xml_track: minidom.Document) -> minidom.NodeList:
    try:
        if xml_track.nodeName != TRACK_TAG:
            raise ValueError(
                f"Received element of type: {xml_track.nodeName}. "
                f"Expected a {TRACK_TAG}"
            )
        return xml_track.getElementsByTagName(TRACKPOINT_TAG)
    except ValueError as e:
        logger.error(f"Error getting track points: {e}")
        return minidom.NodeList()


def get_trk_point_field(trk_point: minidom.Element, field: Text) -> Any:
    try:
        if trk_point.nodeName != TRACKPOINT_TAG:
            raise ValueError(
                f"Received element of type: {trk_point.nodeName}. "
                f"Expected a {TRACKPOINT_TAG}"
            )
        return trk_point.getElementsByTagName(field)[0].childNodes[0].nodeValue
    except (ValueError, IndexError) as e:
        logger.error(f"Error getting track point field '{field}': {e}")
        return minidom.NodeList()


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
    track = doc.createElement(TRACK_TAG)
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
