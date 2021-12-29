"""
usage: pascal_voc_to_yolo.py [-h] [-x XML_DIR] [-o OUTPUT_PATH] [--relative_img_path RELATIVE_IMG_PATH] [--train_txt_path TRAIN_TXT_PATH]
                             [--negative_image_dir NEGATIVE_IMAGE_DIR]

Sample Pascal VOC XML-to-YOLO converter

optional arguments:
  -h, --help            show this help message and exit
  -x XML_DIR, --xml_dir XML_DIR
                        Path to the folder where the input .xml files are stored.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path of output (all yolo-training-related data).  
  --relative_img_path RELATIVE_IMG_PATH
                        Path to prepend to the train.txt files. This path must determines where the training images will reside. Set train_txt_path to path/to/train.txt you want to
                        change.
  --train_txt_path TRAIN_TXT_PATH
                        Path to the train.txt file that you want to change. Only necessary if you want to modify this file with --relative_img_path.
  --negative_image_dir NEGATIVE_IMAGE_DIR
                        If non-empty, adds empty .txt files for the images in the given path.
"""
import argparse
import glob
import os
import xml.etree.ElementTree as ET

from os.path import join
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sample Pascal VOC XML-to-YOLO converter")
    parser.add_argument("-x",
                        "--xml_dir",
                        help="Path to the folder where the input .xml files are stored.",
                        type=str, default=None)
    parser.add_argument("-o",
                        "--output_path",
                        help="Path of output (all yolo-training-related data).", type=str)
    parser.add_argument("--relative_img_path",
                        help="Path to prepend to the train.txt files. This path must determines where "
                        "the training images will reside. Set train_txt_path to path/to/train.txt "
                        "you want to change.",
                        type=str, default="data/aisscv")
    parser.add_argument("--train_txt_path",
                        help="Path to the train.txt file that you want to change. Only necessary if you want to modify this file with --relative_img_path.",
                        type=str, default=None)
    parser.add_argument("--negative_image_dir",
                        help="If non-empty, adds empty .txt files for the images in the given path.",
                        type=str, default=None)

    args = parser.parse_args()
    return args


def change_train_txt_paths(train_txt_path: str, path_to_add: str) -> None:
    """Changes the path that is prepended to the image files in the train.txt file.
    This path must be the path where the files for YOLO training will reside."""
    dir = os.path.split(train_txt_path)[0]
    tmp_file = os.path.join(dir, 'train_tmp.txt')
    with open(train_txt_path) as f_in, open(tmp_file, 'a') as f_out:
        for line in f_in:
            line = os.path.split(line)[-1]
            out_line = os.path.join(path_to_add, line)
            f_out.write(out_line)
    os.remove(train_txt_path)
    os.rename(tmp_file, train_txt_path)


def create_obj_names(classes: list, out_dir: str) -> None:
    """Creates the obj.names file required for training."""
    file = join(out_dir, 'aisscv.names')
    if os.path.exists(file):
        os.remove(file)
    with open(file, 'a') as obj_names:
        for name in classes:
            obj_names.write(name + '\n')


def convert(size: tuple, box: tuple) -> tuple:
    """From https://github.com/AlexeyAB/darknet"""
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x, y, w, h)


def convert_annotations(in_dir: str, classes: list, out_dir: str, relative_img_path: str) -> None:
    """Converts Pascal VOC annotations to YOLO annotations and creates a train.txt required
    for training.
    Adapted from https://github.com/AlexeyAB/darknet"""
    filenames = []
    annotation_dir = join(out_dir, "labels")
    count = 0
    if not os.path.exists(annotation_dir):
        os.makedirs(annotation_dir)
    for voc_file in tqdm(glob.glob(in_dir + '/*.xml'), desc="Processing XMLs..."):
        tree = ET.parse(voc_file)
        root = tree.getroot()

        file = root.find('filename').text
        filenames.append(file)
        filename = file.split('.')[0]
        out = join(annotation_dir, filename + ".txt")
        out_file = open(out, 'w')

        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            cls_id = classes.index(cls)
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(
                xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
            bb = convert((w, h), b)
            out_file.write(str(cls_id) + " " +
                           " ".join([str(a) for a in bb]) + '\n')
        count += 1
    # Write train_txt
    train_file = join(out_dir, 'aisscv-train.txt')
    if os.path.exists(train_file):
        os.remove(train_file)
    with open(train_file, 'a') as train_txt:
        for file in filenames:
            out_str = join(relative_img_path, file) + "\n"
            train_txt.write(out_str)
    print("Converted {} files.".format(count))


def main(args):
    classes = ['box', 'open', 'dent', 'hole']
    if args.train_txt_path is not None:
        # Only executed if you want to change the paths
        print("Changing img paths in train.txt to \"" +
              args.relative_img_path + "\"")
        change_train_txt_paths(os.path.join(args.train_txt_path),
                               args.relative_img_path)
        return
    if args.output_path is not None:
        # Primary execution path for transforming labels
        out_dir = os.path.expanduser(args.output_path)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if args.xml_dir is not None:
            convert_annotations(args.xml_dir, classes,
                                out_dir, args.relative_img_path)
            create_obj_names(classes, out_dir)


if __name__ == '__main__':
    args = parse_args()
    print('=========CALLED MAIN OF PASCAL2YOLO==========')
    main(args)
