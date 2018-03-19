# import numpy as np


def find_opt_threshold(histogram):
    """Find optimal threshold to divide the histogram into two classes."""
    # todo add some safety checks

    px_cnt = sum(histogram)

    # leave if histogram is empty
    if px_cnt == 0:
        return -1



    len(histogram)

