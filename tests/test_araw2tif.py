import contextlib
import numpy as np
import os
import unittest
import shutil
import tempfile
import tifffile
import time
from tsv.raw import raw_imsave
from araw2tif.main import main, copy_one

@contextlib.contextmanager
def test_case(file_hierarchy, dest=None):
    """create a test case

    Usage:

    with test_case(dict(foo={ "bar.raw": np.random.randint... })) as (src, dst):
         main(["--src", src, "--dest", dst])

         ... test things

    :param file_hierarchy: A dictionary of dictionaries and numpy arrays. The
         dictionary keys are filenames and the values are either a dictionary
         representing a folder or a numpy array representing the contents
         of a .raw file with the given name.
    :param dest: an optional destination for the tiff files
    :return: a 2-tuple of the root of the hierarchy and destination (yielded)
    """
    src = tempfile.mkdtemp()
    if dest is None:
        dest = tempfile.mkdtemp()
    stack = [(src, file_hierarchy)]
    while len(stack) > 0:
        root, fh = stack.pop(0)
        for key, value in fh.items():
            path = os.path.join(root, key)
            if isinstance(value, dict):
                os.mkdir(path)
                stack.append((path, value))
            else:
                raw_imsave(path, value)
    yield (src, dest)
    shutil.rmtree(src, ignore_errors=True)
    shutil.rmtree(dest, ignore_errors=True)


def mkimg(r:np.random.RandomState):
    """Make a typical random image

    :param r: A random state for generating images
    :returns: a 10x10x10 uint8 array
    """
    return r.randint(0, 256, size=(10, 10), dtype=np.uint8)


class TestARaw2Tif(unittest.TestCase):
    def test_copy_one(self):
        r = np.random.RandomState(1)
        my_case = { "foo.raw": mkimg(r)}
        with test_case(my_case) as (src, dest):
            copy_one(os.path.join(src, "foo.raw"),
                     os.path.join(dest, "foo.tiff"),
                     compress=3)
            np.testing.assert_array_equal(
                my_case["foo.raw"],
                tifffile.imread(os.path.join(dest, "foo.tiff")))

    def test_copy_one_after(self):
        r = np.random.RandomState(1)
        my_case = { "foo.raw": mkimg(r)}
        with test_case(my_case) as (src, dest):
            time.sleep(.1)  # sleep a tick.
            with open(os.path.join(dest, "foo.tiff"), "w") as fd:
                fd.write("Huzzah!")
            copy_one(os.path.join(src, "foo.raw"),
                     os.path.join(dest, "foo.tiff"),
                     compress=3)
            with open(os.path.join(dest, "foo.tiff")) as fd:
                self.assertEqual(fd.read(), "Huzzah!")

    def test_copy_one_before(self):
        r = np.random.RandomState(1)
        my_case = { "foo.raw": mkimg(r)}
        dest = tempfile.mkdtemp()
        with open(os.path.join(dest, "foo.tiff"), "w") as fd:
            fd.write("Huzzah!")
        time.sleep(.1) # sleep a tick.
        with test_case(my_case, dest=dest) as (src, dest):
            copy_one(os.path.join(src, "foo.raw"),
                     os.path.join(dest, "foo.tiff"),
                     compress=3)
            np.testing.assert_array_equal(
                my_case["foo.raw"],
                tifffile.imread(os.path.join(dest, "foo.tiff")))

    def test_one(self):
        r = np.random.RandomState(1)
        my_case = { "foo.raw": mkimg(r)}
        with test_case(my_case) as (src, dest):
            main(["--src", src,
                  "--dest", dest])
            dirlist = os.listdir(dest)
            self.assertEqual(len(dirlist), 1)
            self.assertEqual(dirlist[0], "foo.tiff")
            np.testing.assert_array_equal(
                my_case["foo.raw"],
                tifffile.imread(os.path.join(dest, "foo.tiff")))

    def test_subdir(self):
        r = np.random.RandomState(1)
        my_case = { "foo": { "foo.raw": mkimg(r)},
                    "bar": { "bar.raw": mkimg(r),
                             "baz.raw": mkimg(r)}
                    }
        with test_case(my_case) as (src, dest):
            main(["--src", src,
                  "--dest", dest])
            dirlist = sorted(os.listdir(dest))
            self.assertListEqual(dirlist, ["bar", "foo"])
            np.testing.assert_array_equal(
                my_case["foo"]["foo.raw"],
                tifffile.imread(os.path.join(dest, "foo", "foo.tiff")))
            np.testing.assert_array_equal(
                my_case["bar"]["bar.raw"],
                tifffile.imread(os.path.join(dest, "bar", "bar.tiff")))
            np.testing.assert_array_equal(
                my_case["bar"]["baz.raw"],
                tifffile.imread(os.path.join(dest, "bar", "baz.tiff")))

    def test_timestamp_after(self):
        r = np.random.RandomState(1)
        my_case = { "foo.raw": mkimg(r)}
        with test_case(my_case) as (src, dest):
            time.sleep(.1)  # sleep a tick.
            with open(os.path.join(dest, "foo.tiff"), "w") as fd:
                fd.write("Huzzah!")
            main(["--src", src,
                  "--dest", dest])
            with open(os.path.join(dest, "foo.tiff")) as fd:
                self.assertEqual(fd.read(), "Huzzah!")

    def test_timestamp_before(self):
        r = np.random.RandomState(1)
        my_case = { "foo.raw": mkimg(r)}
        dest = tempfile.mkdtemp()
        with open(os.path.join(dest, "foo.tiff"), "w") as fd:
            fd.write("Huzzah!")
        time.sleep(.1) # sleep a tick.
        with test_case(my_case, dest=dest) as (src, dest):
            main(["--src", src,
                  "--dest", dest])
            np.testing.assert_array_equal(
                my_case["foo.raw"],
                tifffile.imread(os.path.join(dest, "foo.tiff")))
