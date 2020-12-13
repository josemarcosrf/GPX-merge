from typing import List

import numpy as np
import pandas as pd


def interpolate_zeros(values: List[int], missing_value: int = 0) -> List[int]:
    _values = [v if v != missing_value else np.nan for v in values]
    s = pd.Series(_values)
    interpolated = list(map(int, s.interpolate().to_list()))

    return interpolated
