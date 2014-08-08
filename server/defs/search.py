__author__ = 'Andrean'

from types import *


def binary_search(arr, x, comparator=None, strict=True, low=0, high=None):
    """

    :param arr: sorted list of elements
    :param x: searched element or compare forEach function, which returns 1, 0, -1
    :param strict: if True don't look for strict comparison. Returns position of nearest left element
    :return: position of looking element or position between elements where it could be if "strict" is True
    """
    def cmp(arr_el, el):
        if arr_el > el:
            return 1
        if arr_el < el:
            return -1
        return 0
    if isinstance(comparator, FunctionType):
        cmp = comparator
    if high is None:
        high = len(arr)
    while low < high:
        mid = (low + high)//2
        test = cmp(arr[mid], x)
        if test == -1:
            low = mid+1
        elif test == 1:
            high = mid
        else:
            return mid
    if strict is not True:
        if high == 0:
            return -0.5
        if low >= len(arr):
            return 0.5
        return low-1
    return -1