import aisscv
from aisscv import utils, aisscv_app
from aisscv.utils import pascal_voc_to_yolo, negative_examples
#from aisscv.utils import *
from aisscv import augmentation
from aisscv.augmentation import *
import os
import glob
import pandas as pd
from pathlib import Path


def test_function():
    # Check if functions are present, to check if module works as expected
    assert os.system(
        "python -m aisscv --question 'Where is the package?'") == 0

    assert os.system(
        "python -m aisscv") == 0
    assert (aisscv_app.main() is None)
    assert utils.label_helper.demo(headless=True)


def test_pascal_conversion():
    df = utils.label_reader.via_coco_to_df(
        'data/annotations/packaging_project_manuel_coco.json', 'data/images', True, False)
    try:
        os.system('rm -rf ./tmp')
    except:
        pass
    os.mkdir('tmp/')

    utils.label_helper.write_to_pascal_voc(df, 'tmp')
    files = os.listdir('tmp')
    assert len(glob.glob("tmp/*.xml", recursive=False)
               ) == df['filename'].unique().size, 'files: {} and unqie rows {}'.format(len(glob.glob("temp/*.txt", recursive=False)), df['filename'].unique().size)


def test_yolo_conversion():
    try:
        os.system('rm -rf ./tmp')
    except:
        pass
    os.makedirs("./tmp/jpg")
    # requires pascal voc files
    pascal_voc_to_yolo.convert_annotations(in_dir="./tests/xml", classes=['box', 'wet'], out_dir="./tmp",
                                           relative_img_path="/test/path")
    num_txt_files = len(glob.glob("tmp/labels/*.txt", recursive=False))
    num_xml_files = len(glob.glob("./tests/xml/*.xml", recursive=False))
    assert num_txt_files == num_xml_files, "Not all XMLs were converted to YOLO format."
    with open("./tmp/aisscv-train.txt", 'r') as train_txt:
        num_lines = len(train_txt.readlines())
        assert num_txt_files == num_lines, "Number of lines in train.txt does not match the number of files. Number of txt files: {}, number of lines: {}".format(
            str(num_txt_files), str(len(num_lines)))
    utils.pascal_voc_to_yolo.change_train_txt_paths(
        "./tmp/aisscv-train.txt", "/test")
    with open("./tmp/aisscv-train.txt", 'r') as train_txt:
        assert num_txt_files == len(train_txt.readlines(
        )), "Changing image paths in train.txt changed the number of lines"
        for line in train_txt:
            assert os.path.split(
                line)[0] == "/test", "Wrong path added to train.txt"
    try:
        os.system('rm -rf ./tmp')
    except:
        pass


def test_yolo_create_empty_labels():
    os.makedirs("./tmp")
    os.system('cp -r ./tests/jpg ./tmp/jpg')
    with open(Path("./tmp/train.txt"), 'w') as train_txt:
        train_txt.write("/test-path/test.jpg\n")
    negative_examples.create_empty_labels(
        dir="./tmp/jpg/", train_txt_path="./tmp/train.txt")
    num_txt_files = len(glob.glob("./tmp/jpg/*.txt", recursive=False))
    num_jpg_files = len(glob.glob("./tmp/jpg/*.jpg", recursive=False))
    assert num_txt_files == num_jpg_files, "Not all jpg got a label file."
    for txt in glob.glob("./tmp/jpg/*.txt"):
        pass
        assert os.stat(txt).st_size == 0, "Label file not empty."
    try:
        os.system('rm -rf ./tmp')
    except:
        pass


def test_helper():
    df = utils.label_reader.via_json_to_df(
        'data/annotations/labels_luca_json.json', 'data/images', True, False, True)
    assert isinstance(df, pd.core.frame.DataFrame), 'Expexted to get panda DF'


def test_rescale():
    df = utils.label_reader.via_json_to_df(
        'data/annotations/labels_joel_json.json', 'data/images/joel', True, True, True)
    try:
        os.system('rm -rf ./tmp')
    except:
        pass
    os.mkdir('./tmp')
    print('Created Folder for resized images')

    utils.label_helper.resize_images_df(
        df.loc[:10, :], resize_width=300, resize_height=300, directory='./tmp', img_to_df=True)
    df_check = utils.label_reader.via_json_to_df(
        'data/annotations/labels_joel_json.json', './tmp', False, True, True)
    assert (df_check.loc[:10, 'size'] == (300, 300)).all()


def test_augmentation():
    try:
        os.system('rm -rf ./tmp')
    except:
        pass
    os.mkdir('./tmp')
    print('Created Folder for augmented images')
    augmentation.augment_dataset.create_augmented_dataset('data/images/joel',
                                                          "data/annotations/labels_joel_json.json", './tmp', repetitions_per_image=2, stop_after=2)

    assert len(glob.glob("./tmp/annotations/*.xml", recursive=False)
               ) == len(glob.glob("./tmp/*.png", recursive=False)) == 3*3


def test_augmentation_with_damages():
    try:
        os.system('rm -rf ./tmp')
    except:
        pass
    os.mkdir('./tmp')
    print('Created Folder for augmented images')
    augmentation.augment_dataset_with_damages.create_augmented_dataset('data/images/joel',
                                                                       "data/annotations/labels_joel_json.json", './tmp', repetitions_per_image=2, stop_after=2)

    assert len(glob.glob("./tmp/annotations/*.xml", recursive=False)
               ) == len(glob.glob("./tmp/*.png", recursive=False)) == 3*3


if __name__ == '__main__':
    """ 
    This section is only for debugging tests. 
    When the pytest test-suite runs the tests, every function present will be executed
    """
    print(dir(utils))
    # test_function()
    # test_helper()
    # test_pascal_conversion()
    # test_rescale()
    # test_augmentation()
    # test_yolo_conversion()
    # test_yolo_create_empty_labels()
    test_augmentation_with_damages()

    # Clean up after yourself

    # try:
    #    os.system('rm -rf ./tmp')
    # except:
    #    pass
