from unittest import TestCase

__author__ = 'Andrean'

from defs.search import binary_search as binary_search


class TestBinary_search(TestCase):
    def setUp(self):
        self.array = [0,1,2,3,4,5,6,7,8,9,10]

    def test_SimpleSearch(self):
        x = 3
        self.assertEqual(binary_search(self.array, x), 3)

    def test_SearchOnBounds(self):
        x = 10
        self.assertEqual(binary_search(self.array, x), 10)
        x = 0
        self.assertEqual(binary_search(self.array, x), 0)

    def test_NotFound(self):
        x = 11
        self.assertEqual(binary_search(self.array, x), -1)
        x = -1
        self.assertEqual(binary_search(self.array, x), -1)
        x = 2.3
        self.assertEqual(binary_search(self.array, x), -1)

    def test_NotStrictSearch(self):
        x = 1.34
        self.assertEqual(binary_search(self.array, x, strict=False), 1)
        x = 9.89
        self.assertEqual(binary_search(self.array, x, strict=False), 9)
        x = 10.07
        self.assertEqual(binary_search(self.array, x, strict=False), 0.5)
        x = -1.01
        self.assertEqual(binary_search(self.array, x, strict=False), -0.5)
        x = -0.1
        self.assertEqual(binary_search(self.array, x, strict=False), -0.5)

    def test_SimpleSearchWithComparator(self):
        def comparator(el, x):
            y = x / 100
            if el > y:
                return 1
            if el < y:
                return -1
            return 0

        x = 200
        self.assertEqual(binary_search(self.array, x, comparator=comparator), 2)
        x = 300
        self.assertEqual(binary_search(self.array, x, comparator=comparator), 3)
        x = 1000
        self.assertEqual(binary_search(self.array, x, comparator=comparator), 10)
        x = 0
        self.assertEqual(binary_search(self.array, x, comparator=comparator), 0)
        x = 101
        self.assertEqual(binary_search(self.array, x, comparator=comparator), -1)
        x = -1
        self.assertEqual(binary_search(self.array, x, comparator=comparator), -1)
        x = 10
        self.assertEqual(binary_search(self.array, x, comparator=comparator), -1)
        x = 11111
        self.assertEqual(binary_search(self.array, x, comparator=comparator), -1)

    def test_NotStrictSearchWithComparator(self):
        def comparator(el, x):
            y = x / 100
            if el > y:
                return 1
            if el < y:
                return -1
            return 0

        x = 101
        self.assertEqual(binary_search(self.array, x, comparator=comparator, strict=False), 1)
        x = 999
        self.assertEqual(binary_search(self.array, x, comparator=comparator, strict=False), 9)
        x = -1
        self.assertEqual(binary_search(self.array, x, comparator=comparator, strict=False), -0.5)
        x = 11111
        self.assertEqual(binary_search(self.array, x, comparator=comparator, strict=False), 0.5)








