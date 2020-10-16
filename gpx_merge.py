import os
import glob

from xml.dom import minidom
from xml.parsers.expat import ExpatError

from rich.console import Console
from rich.traceback import install

from tempfile import NamedTemporaryFile

TEST_DIR = "data/LaTuca"

TRACKPOINT_TAG = "trkpt"


console = Console()
install()


def find_files(gpx_dir):
    return glob.glob(os.path.join(gpx_dir, "*.gpx"))


def read_gpx(gpx_file):

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


if __name__ == "__main__":

    times = []
    ind_ind_list = []
    for gpx_file in find_files(TEST_DIR):
        console.log(f"Reading file: {gpx_file}")
        doc = read_gpx(gpx_file)
        track_points = get_trk_points(doc)
        console.log(f"Found {len(track_points)} track points")

        ind_ind_list.append(list(range(len(track_points))))
        times.extend(
            [get_trk_point_field(trkpt, field="time") for trkpt in track_points]
        )
        console.log(f"From: {times[0]} to {times[-1]}")

        # times = [tp["time"] for tp in trkpts]
        # console.log(f"From {tims[0]} to {times[-1]}")

    # merge track point elements
