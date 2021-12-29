"""Generates empty label files and appends the filenames to the train.txt for yolo.
usage: negative_examples.py [-h] [--train_txt_path TRAIN_TXT_PATH] [--negative_image_dir NEGATIVE_IMAGE_DIR]

Generates empty label files and appends the filenames to the train.txt for yolo.

optional arguments:
  -h, --help            show this help message and exit
  --train_txt_path TRAIN_TXT_PATH
                        Path to the train.txt file that you want to append the files to.
  --negative_image_dir NEGATIVE_IMAGE_DIR
                        If non-empty, adds empty .txt files for the images in the given path.
"""

import argparse
import glob
import os

from pathlib import Path
from tqdm import tqdm

def create_empty_labels(dir:str, train_txt_path:str)->None:
    """Writes empty label files for the images in out_dir and appends the train.txt.
    If the empty label files exists, does not overwrite it."""
    with open(Path(train_txt_path), 'a+') as train_txt:           
        train_txt.seek(0)
        # print(train_txt.tell())
        prepend_path = os.path.split(train_txt.readline())[0]
        print("Prepend path for train.txt: " + prepend_path)
        count = 0
        train_txt.seek(0,2)
        # print(train_txt.tell())
        for file in tqdm (glob.glob(dir + '/*.jpg'), desc="Adding empty label files..."):
            txt_file = os.path.split(file)[-1].split('.')[0] + ".txt"            
            empty_label = Path(dir) / txt_file
            empty_label.touch()            
            write_path = Path(prepend_path) / os.path.split(file)[1]
            if count == 0:                
                print("Write path: " + str(write_path))
            train_txt.write(str(write_path) + '\n')
            count += 1        
    print("{} files written".format(count))

def main():    
    if args.negative_image_dir is not None:
        create_empty_labels(args.negative_image_dir, args.train_txt_path)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generates empty label files and appends the filenames to the train.txt for yolo.")
    parser.add_argument("--train_txt_path",
                    help="Path to the train.txt file that you want to append the files to.",                         
                    type=str, default=None)
    parser.add_argument("--negative_image_dir",
                    help="If non-empty, adds empty .txt files for the images in the given path.",                       
                    type=str, default=None)

    args = parser.parse_args()

    main()
