from typing import List
from xml.dom import minidom

import numpy as np
import pandas as pd


def read_xml(gptcx_file: str) -> minidom.Document:
    try:
        doc = minidom.parse(gptcx_file)
        return doc
    except Exception as e:
        raise e


def interpolate_zeros(values: List[int], missing_value: int = 0) -> List[int]:
    _values = [v if v != missing_value else np.nan for v in values]
    s = pd.Series(_values)
    interpolated = list(map(int, s.interpolate().to_list()))

    return interpolated
