import argparse
import multiprocessing
import os
import tifffile
import shutil
import sys
import tqdm
from tsv.raw import raw_imread
import traceback

def parse_args(args=sys.argv[1:]):
    """Parse the program arguments

    :param args: program arguments, e.g. sys.argv[1:]
    :return: argument dictionary
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--src",
                        help="Source directory",
                        required=True)
    parser.add_argument("--dest",
                        help="Destination directory",
                        required=True)
    parser.add_argument("--n-cpus",
                        type=int,
                        default=os.cpu_count(),
                        help="Number of CPUs to use when reading/writing")
    parser.add_argument("--compress",
                        type=int,
                        default=3,
                        help="TIFF compression level: 0-9, default=3")
    parser.add_argument("--silent",
                        action="store_true",
                        help="Don't display progress to STDOUT")
    parser.add_argument("--src-ext",
                        default=".raw",
                        help="Extension to search for in source folder. "
                        "Default is \".raw\"")
    parser.add_argument("--dest-ext",
                        default=".tiff",
                        help="Extension to add to files in destination folder. "
                        "Default is \".tiff\"")
    parser.add_argument("--copy-all",
                        action="store_true",
                        help="Copy all files in the directory tree, "
                             "compressing .raw files as we go.")
    return parser.parse_args(args)

def copy_one(src, dest, compress):
    """Copy one file from .raw to .tiff

    :param src: the path to a .raw file
    :param dest: the path to the .tiff file to be written
    :param compress: compression level: 0-9
    """
    if os.path.exists(dest):
        src_ts = os.stat(src).st_mtime
        dest_ts = os.stat(dest).st_mtime
        if dest_ts >= src_ts:
            return
    img = raw_imread(src)
    if os.path.exists(dest):
        os.unlink(dest)
    tifffile.imsave(dest, img, compress=compress)


has_printed_exception = False


def copy_tiff(src, dest, compress):
    """Copy a TIFF file, possibly compressing it

    :param src: the path to a .tiff file
    :param dest: the destination
    :param compress: compression level
    """
    global has_printed_exception
    if os.path.exists(dest):
        src_ts = os.stat(src).st_mtime
        dest_ts = os.stat(dest).st_mtime
        if dest_ts >= src_ts:
            return
    try:
        tf = tifffile.TiffFile(src)
        if tf.series[0].pages[0].compression == \
                tifffile.tifffile.TIFF.COMPRESSION.NONE:
            img = tf.asarray()
            if os.path.exists(dest):
                os.unlink(dest)
            tifffile.imsave(dest, img, compress=compress)
        else:
            copy_file(src, dest, compress)
    except:
        if not has_printed_exception:
            print("Possibly corrupted TIF: %s" % src)
            traceback.print_exc()
            has_printed_exception = True
        copy_file(src, dest, compress)


def copy_file(src, dest, compress):
    """Copy any file"""
    if os.path.exists(dest):
        src_ts = os.stat(src).st_mtime
        dest_ts = os.stat(dest).st_mtime
        if dest_ts >= src_ts:
            return
    if os.path.exists(dest):
        os.unlink(dest)
    shutil.copyfile(src, dest)


def main(args=sys.argv[1:]):
    args = parse_args(args)
    to_do = []
    for root, folders, files in tqdm.tqdm(
            os.walk(args.src),
            desc="Scanning directory",
            disable=args.silent):
        rel_root = os.path.relpath(root, args.src)
        dest_root = os.path.join(args.dest, rel_root)
        checked_dest_root = False
        for file in files:
            src = os.path.join(root, file)
            if file.lower().endswith(args.src_ext):
                if not checked_dest_root and not os.path.exists(dest_root):
                    os.makedirs(dest_root)
                    checked_dest_root = True
                dest = os.path.join(dest_root,
                                    file[:-len(args.src_ext)] + args.dest_ext)
                to_do.append((copy_one, src, dest))
            elif args.copy_all:
                if not checked_dest_root and not os.path.exists(dest_root):
                    os.makedirs(dest_root)
                    checked_dest_root = True
                dest = os.path.join(dest_root, file)
                if src.endswith(".tif") or src.endswith(".tiff"):
                    to_do.append((copy_tiff, src, dest))
                else:
                    to_do.append((copy_file, src, dest))

    futures = []
    with multiprocessing.Pool(args.n_cpus) as pool:
        for fn, src, dest in tqdm.tqdm(to_do,
                                   desc="Enqueueing work",
                                   disable=args.silent):
            if fn == shutil.copy:
                fn_args = (src, dest)
            else:
                fn_args = (src, dest, args.compress)
            futures.append(pool.apply_async(
                fn, fn_args))
        for future in tqdm.tqdm(futures,
                                desc="Working",
                                disable=args.silent):
            future.get()


if __name__ == "__main__":
    main()