import pandas as pd
import json
import cv2 as cv
import os
import logging
from aisscv.__RepoPath__ import __RepoPath__
logger = logging.getLogger('utils')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s : %(name)s : %(levelname)s : %(message)s')
console.setFormatter(formatter)

logger.addHandler(console)

FOLDER = 'images'
# Defaults to ../../data/images at the Repository.
IMG_DIR_DEFAULT = os.path.join(__RepoPath__, 'data/images')

__all__ = ['via_json_to_df', 'via_coco_to_df']


def get_size(path: str) -> tuple:
    """ Get the Size of the Image.

    Parameters
    ----------
    path : str
        Path to the image of interest

    Returns
    -------
    tuple
        (width,height)

    """
    try:
        im = cv.imread(path)
        h, w, _ = im.shape
    except:
        logger.error(f'Could not find Image {path} to get size')
        w, h = 0, 0
    return(w, h)


def via_json_to_df(label_file_path: str, image_dir: str = IMG_DIR_DEFAULT, poly_to_box=False, add_img_size=False, skip_format_problems=False) -> pd.DataFrame:
    """ Function which reads in a json, that was exported by the VGG Image Annotator (via) and transorfms it to a dataframe.
    The dataframe is already equipped with pascal-voc-like keywords.

    Parameters
    ----------
    label_file_path : str
        Path to the json-labelfile
    image_dir : str, optional
        Directories where the images reside. Defaults to the path in git repository /data/images
    poly_to_box : bool, optional
        Wether polynoms should be converted to a bounding_box. Defaults to no
    add_img_size : bool, optional
        Load the image to extract size. Will massively slow down the conversion.
        Should be turned on, when meant to export to a different format
        (i.e. PASCAL VOC) but can be kept of when just visualizing
    skip_format_problems : bool, optional
        If a wrong label-type is detected skip that annotation. Defaults to False,
        which throws an error to fix the label

    Returns
    -------
    pd.DataFrame
        Dataframe with one row per image.

    """
    logger.info('Opening {}'.format(label_file_path))
    logger.info('Looking at image_dir: {}'.format(image_dir))
    with open(label_file_path, 'r') as label_file:
        data = json.load(label_file)
    assert 'regions' in data[list(data.keys(
    ))[0]].keys(), 'Seems not to be VGGs JSON format'

    df = pd.DataFrame(columns=['folder', 'path', 'filename',
                               'size', 'objects'])

    for identifier, infos in data.items():
        image_name = infos['filename']
        logger.info(f'Working on {identifier} with image {image_name}')
        objects = []
        for region in infos['regions']:
            label_type = region['shape_attributes']['name']
            #print('All Region Attributes: ', region['region_attributes'])
            if (not region['region_attributes']):
                #print('No Label Info Found')
                continue
            label_name = region['region_attributes']['label']
            if label_type == 'rect':
                x_min = region['shape_attributes']['x']
                x_max = x_min + region['shape_attributes']['width']
                y_min = region['shape_attributes']['y']
                y_max = y_min + region['shape_attributes']['height']
                objects.append({'name': label_name, 'pose': 0, 'truncated': 0, 'difficult': 0, 'bndbox': {'xmin': x_min,
                                                                                                          'ymin': y_min, 'xmax': x_max, 'ymax': y_max}})

            elif label_type in ['polygon', 'polyline']:  # Label not box:
                x_points = region['shape_attributes']['all_points_x']
                y_points = region['shape_attributes']['all_points_y']
                if poly_to_box:
                    x_min = min(x_points)
                    x_max = max(x_points)
                    y_min = min(y_points)
                    y_max = max(y_points)
                    objects.append({'name': label_name, 'pose': 0, 'truncated': 0, 'difficult': 0, 'bndbox': {'xmin': x_min,
                                                                                                              'ymin': y_min, 'xmax': x_max, 'ymax': y_max}})
                    logger.info('Transformed polynom for {} of image {} to box {}'.format(
                        label_name, image_name, [x_min, x_max, y_min, y_max]))
                else:
                    points = zip(x_points, y_points)
                    objects.append({'name': label_name, 'pose': 0,
                                    'truncated': 0, 'difficult': 0, 'points': {'x_points': x_points, 'y_points': y_points}})
            else:
                logger.error('Unvalid label type for {}: {} not accepted'.format(
                    label_name, label_type))
                if skip_format_problems:
                    continue
                else:
                    raise Exception('See above logs-error')
        image_path = os.path.join(image_dir, image_name)
        size = get_size(image_path) if add_img_size else (0, 0)
        df = df.append({'folder': '.', 'path': image_path, 'filename': image_name,
                        'size': size, 'objects': objects}, ignore_index=True)
    return df


def via_coco_to_df(label_file_path: str, image_dir: str = IMG_DIR_DEFAULT, poly_to_box=False, add_img_size=False) -> pd.DataFrame:
    """ Function which reads in a json in COCO-Format, that was exported by the VGG Image Annotator (via) and transorfms it to a dataframe.
    The dataframe is already equipped with pascal-voc-like keywords.

    Parameters
    ----------
    label_file_path : str
        Path to the COCO-styled json-labelfile
    image_dir : str, optional
        Directories where the images reside. Defaults to the path in git repository /data/images
    poly_to_box : bool, optional
        Wether polynoms should be converted to a bounding_box. Defaults to no
    add_img_size : bool, optional
        Load the image to extract size. Will massively slow down the conversion. 
        Should be turned on, when meant to export to a different format 
        (i.e. PASCAL VOC) but can be kept of when just visualizing
    Returns
    -------
    pd.DataFrame
        Dataframe with one row per image.

    """
    logger.info('Opening {}'.format(label_file_path))
    logger.info('Looking at image_dir: {}'.format(image_dir))
    with open(label_file_path, 'r') as label_file:
        data = json.load(label_file)

    assert 'info' in data.keys(), 'Seems not to be COCO format'
    images = dict()
    for img in data['images']:
        images[img['id']] = img['file_name']
    df = pd.DataFrame(columns=['folder', 'path', 'filename',
                               'size', 'objects'])
    label_map = {1: 'box', 2: 'wet', 3: 'dent', 4: 'hole',  5: 'open'}
    data_dict = {}

    # Two Step approach is necessary, because COCO Stores a bunch of anotations,
    # in whcih the same image occurs multiple times.
    # But we need to have all annotations grouped per Image

    # First, iterate through unique images and add an entry for each label
    for img_name in images.values():
        image_path = os.path.join(image_dir, img_name)
        size = get_size(image_path) if add_img_size else (0, 0)
        data_dict[img_name] = {'folder': '.', 'path': image_path, 'filename': img_name,
                               'size': size, 'objects': []}
    # Now, iterate through all annotations, and add them to the corresponding image
    for annotation in data['annotations']:
        image_name = images[annotation['image_id']]
        anno_id = annotation['id']
        logger.info(f'Working on annotation {anno_id} with image {image_name}')
        label_name = label_map[annotation['category_id']]
        if label_name == 'box' or poly_to_box:
            x_min = annotation['bbox'][0]
            x_max = x_min + annotation['bbox'][2]
            y_min = annotation['bbox'][1]
            y_max = y_min + annotation['bbox'][3]
            data_dict[image_name]['objects'].append({'name': label_name, 'pose': 0, 'truncated': 0, 'difficult': 0, 'bndbox': {'xmin': x_min,
                                                                                                                               'ymin': y_min, 'xmax': x_max, 'ymax': y_max}})
        else:  # Label not box:
            x_points = annotation['segmentation'][0::2]
            y_points = annotation['segmentation'][1::2]
            points = zip(x_points, y_points)
            data_dict[image_name]['objects'].append({'name': label_name, 'pose': 0,
                                                     'truncated': 0, 'difficult': 0, 'points': {'x_points': x_points, 'y_points': y_points}})

        df = pd.DataFrame.from_dict(data_dict, orient='index')
    return df
