import os
import sys
import unittest

sys.path.append("../main")
import dendro_pictures

class TestDendro(unittest.TestCase):
    def test_picture(self):
        dendro_pictures.take_picture()


if __name__ == '__main__':
    unittest.main()
