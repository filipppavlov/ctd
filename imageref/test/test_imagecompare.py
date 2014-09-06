import unittest
import os
import imageref.imagecompare as imagecompare
import imageref.imageref as imageref

RES_PATH = os.path.join(os.path.dirname(__file__), 'res')


def _res_path(path):
    return os.path.join(RES_PATH, path)


class TestImageCompare(unittest.TestCase):
    def test_comparing_same_image_succeeds(self):
        self.assertEqual(imagecompare.compare_images(_res_path('1.png'), _res_path('1.png'))['color']['max_abs_error'], 0)

    def test_comparing_different_images_fails(self):
        self.assertGreater(imagecompare.compare_images(_res_path('1.png'), _res_path('2.png'))['color']['max_abs_error'], 0)

    def test_comparing_different_sized_image_raises(self):
        with self.assertRaises(imagecompare.DimensionsDiffer):
            imagecompare.compare_images(_res_path('1.png'), _res_path('3.png'))


class TestImageRes(unittest.TestCase):
    def test_ref_equals_itself(self):
        cmp = imageref.ImageComparison()
        ref = imageref.ImageRef(_res_path('1.png'))
        self.assertTrue(cmp.compare(ref, ref, cmp.get_default_settings()))

    def test_refs_to_equal_images_are_equal(self):
        cmp = imageref.ImageComparison()
        ref1 = imageref.ImageRef(_res_path('1.png'))
        ref2 = imageref.ImageRef(_res_path('4.png'))
        self.assertTrue(cmp.compare(ref1, ref2, cmp.get_default_settings()))

    def test_refs_to_different_images_are_not_equal(self):
        cmp = imageref.ImageComparison()
        ref1 = imageref.ImageRef(_res_path('1.png'))
        ref2 = imageref.ImageRef(_res_path('2.png'))
        self.assertFalse(cmp.compare(ref1, ref2, cmp.get_default_settings()))

    def test_refs_to_different_sized_images_are_not_equal(self):
        cmp = imageref.ImageComparison()
        ref1 = imageref.ImageRef(_res_path('1.png'))
        ref2 = imageref.ImageRef(_res_path('3.png'))
        self.assertFalse(cmp.compare(ref1, ref2, cmp.get_default_settings()))
