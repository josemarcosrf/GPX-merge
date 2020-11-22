import logging

from typing import Any
from typing import Text

from tempfile import NamedTemporaryFile

from xml.dom import minidom
from xml.parsers.expat import ExpatError


logger = logging.getLogger(__name__)


TRACKPOINT_TAG = "trkpt"


def read_gpx(gpx_file: Text) -> Any:

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


def get_trk_points(xml_doc):
    return xml_doc.getElementsByTagName(TRACKPOINT_TAG)


def get_trk_point_field(trk_point, field):
    return trk_point.getElementsByTagName(field)[0].childNodes[0].nodeValue
