import pandas as pd
import cv2 as cv
import numpy as np
import os
import logging
from tqdm import tqdm
import xml.etree.cElementTree as ET
from aisscv.__RepoPath__ import __RepoPath__
from aisscv.utils import label_reader

logger = logging.getLogger('utils')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s : %(name)s : %(levelname)s : %(message)s')
console.setFormatter(formatter)

logger.addHandler(console)

FOLDER = 'Images'
# Defaults to ../../data/images at the Repository.
IMG_DIR_DEFAULT = os.path.join(__RepoPath__, 'data/images')


def write_to_pascal_voc(df: pd.DataFrame, directory: str, only_box_label: bool = False) -> None:
    """ Reading a DataFrame as returned by via_[coco|json]_to_df. Writing it to single xml files for each image,
    as specified by the Pascal VOC format.
    Attention, Pascal-Voc only supports bounding boxes, so please use poly_to_box=True when creating the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame that contains all Information and labels
    directory : str
        Directories where the xml files are written to.
    only_box_labels: bool
        only write box labels, skip all other

    Returns
    -------
    None

    Raises
    -------
    Exception, if  dataframe woth polygon was passed. Please convert polygons to boundingboxes before.

    """
    assert 'objects' in df.columns, 'Check DataFrame'
    assert os.path.exists(directory), 'Check if path exists and is correct'
    logger.info(f'Writing {df.shape[0]} labels to {directory}')
    for idx, row in df.iterrows():
        root = ET.Element("annotation")

        ET.SubElement(root, "folder").text = row['folder']
        ET.SubElement(root, "filename").text = row['filename']
        ET.SubElement(root, "path").text = row['path']
        source = ET.SubElement(root, "source")
        ET.SubElement(source, "database").text = 'Unknown'

        size = ET.SubElement(root, "size")
        ET.SubElement(size, 'width').text = str(row['size'][0])
        ET.SubElement(size, 'height').text = str(row['size'][1])
        ET.SubElement(size, 'depth').text = str(3)
        ET.SubElement(root, "segmented").text = str(0)
        for object in row.objects:
            if(object['name'] != 'box' and only_box_label):
                continue
            ob = ET.SubElement(root, 'object')
            if 'points' in object.keys():
                raise Warning('Our pascal-voc implementation currently only supports Boundingboxes,'
                              ' no polygons. Please specify poly_to_box=True'
                              'when creating the DataFrame with one of our functions')
            ET.SubElement(ob, 'name').text = object['name']
            ET.SubElement(ob, 'pose').text = str(object['pose'])
            ET.SubElement(ob, 'truncated').text = str(object['truncated'])
            ET.SubElement(ob, 'difficult').text = str(object['difficult'])
            bbox = ET.SubElement(ob, 'bndbox')
            ET.SubElement(bbox, 'xmin').text = str(
                int(object['bndbox']['xmin']))
            ET.SubElement(bbox, 'ymin').text = str(
                int(object['bndbox']['ymin']))
            ET.SubElement(bbox, 'xmax').text = str(
                int(object['bndbox']['xmax']))
            ET.SubElement(bbox, 'ymax').text = str(
                int(object['bndbox']['ymax']))

        tree = ET.ElementTree(root)
        xml_name = row["filename"].split('.')[0] + '.xml'
        tree.write(os.path.join(directory, xml_name))
        logger.debug(f'Wrote xml to {os.path.join(directory, xml_name)}')


def add_bbox_to_image(image: np.ndarray, object: dict) -> np.ndarray:
    """ Add the boundingbox of the given object to the image.
    Since using CV, order is (B,G,R)

    Parameters
    ----------
    img : np.ndarray
        Opencv image
    object : dict
        Dictionary of the boundingbox with meta infos.


    Returns
    -------
    np.ndarray
        image with the bbndbox in (B,G,R)

    """
    color = (0, 0, 0)
    if object['name'] == 'box':
        color = (0, 255, 255)  # Mark Package yellow. (B,G,R) for cv...

    else:
        color = (0, 0, 255)  # Mark damages red. (B,G,R) for cv....
    cv.rectangle(image, (object['bndbox']['xmin'],
                 object['bndbox']['ymin']), (object['bndbox']['xmax'], object['bndbox']['ymax']), color, 3)

    return image


def add_polygon_to_image(image: np.ndarray, object: dict) -> np.ndarray:
    """ Add the polynom of the given object to the image.
    Since using CV, order is (B,G,R)

    Parameters
    ----------
    img : np.ndarray
        Opencv image
    object : dict
        Dictionary of the polynom with meta infos.


    Returns
    -------
    np.ndarray
        image with the polynom in (B,G,R)

    """
    x_points = object['points']['x_points']
    y_points = object['points']['y_points']
    pts = np.array([a for a in zip(x_points, y_points)])
    pts = pts[:, None, :]
    logging.debug(f'Polylines with shape {pts.shape} : {pts}')
    cv.polylines(image, [pts], True, (0, 0, 255), 5)
    return image


def visualize_labels(df: pd.DataFrame, n: int, headless: bool = False) -> None:
    """ Visualize the images of the given DataFrame.
    Since using CV, order is (B,G,R).
    n Images are shown, get to next image by pressing enter. Every other key will exit the loop.
    Loop will exit if no enter pressed for  10 secods.

    Parameters
    ----------
    img : pd.DataFrame
        dataframe with file_name, objects and all the label infos
    n : int
        How many images are visualized (sampled from dataframe)
    headless: bool
        Prevent cv from showing (for automated tests)

    Returns
    -------
    None

    """

    for idx, row in df.sample(min(n, len(df))).iterrows():
        img = cv.imread(row['path'])  # Image.load(image_path)
        for obj in row.objects:
            if 'bndbox' in obj.keys():
                img = add_bbox_to_image(img, obj)
            elif 'points' in obj.keys():
                img = add_polygon_to_image(img, obj)
        if not headless:
            cv.imshow(row['filename'], img)
            key = cv.waitKey(10000)
            logger.debug('Key: {}'.format(key))
            if key != 13:
                logger.info('Leaving preview because enter was not hit')
                break
        cv.destroyAllWindows()


def demo(path: str = os.path.join(
        __RepoPath__, 'data/annotations/labels_joel_json.json'), n: int = 15, headless: bool = False) -> None:
    """
    Simple demo that shows some labels

    Parameters
    ----------
    path: str
        Directory where via-exported json is located
    headless: bool
        Prevent cv from showing (for automated tests)

    Return
    --------
    True, for testing

    """
    print('Running DEMO')
    assert os.path.exists(path), 'Could not find {}'.format(path)
    df = label_reader.via_json_to_df(path, os.path.join(
        IMG_DIR_DEFAULT, 'joel'), poly_to_box=False)
    visualize_labels(df, 15, headless)
    # df = label_reader.via_coco_to_df('/Users/joel/UNI_Offline/Group-Git/data/annotations/Tito_packaging_project_coco.json',
    #                     '/FAKE/IMAGE/DIR', True, False)
    # print(df.columns)
    # write_to_pascal_voc(df, 'data/annotations/pascal')
    return True


def resize_images_df(df: pd.DataFrame, resize_width: int, resize_height: int, directory: str = False, img_to_df: bool = False) -> pd.DataFrame:
    """
    Reading a DataFrame as returned by via_[coco|json]_to_df. Resizing the image itself and the objects. Resized objects get
    resized in place, resized images can be saved in extra Column in the Dataframe or in a directory.
    Attention, currently only support resizing of bounding boxes, so please use poly_to_box=True when creating the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame that contains all Information and labels
    resize_width: int
        Number of width-pixels after rescaling
    resize_height: int
        Number of height-pixels after rescaling
    directory: str, optional
        Wheter rescaled images should be written to directories
    img_to_df: bool, optional
        Wheter rescaled images should be added to returned df

    Return
    -------
    pd.DataFrame
        Dataframe containing all the information

    """

    assert 'objects' in df.columns, 'Check DataFrame'
    img = []
    for idx, row in df.iterrows():
        width_scale = resize_width/df['size'][idx][0]
        height_scale = resize_height/df['size'][idx][1]
        # print(width_scale, height_scale)
        img_resized = cv.resize(
            cv.imread(df['path'][idx]), (resize_width, resize_height))

        if directory != False:
            assert os.path.exists(directory), 'Check if path correct/exists'
            name = row['filename']
            cv.imwrite(os.path.join(directory, name), img_resized)

        for object in row.objects:
            # print(object['bndbox']['xmin'])
            object['bndbox']['xmin'] = int(
                object['bndbox']['xmin']*width_scale)
            object['bndbox']['xmax'] = int(
                object['bndbox']['xmax']*width_scale)
            object['bndbox']['ymin'] = int(
                object['bndbox']['ymin']*height_scale)
            object['bndbox']['ymax'] = int(
                object['bndbox']['ymax']*height_scale)
            # print(object['bndbox']['xmin'])

        if img_to_df:
            img.append(img_resized)

    if img_to_df:
        df.loc[:, 'img_rescaled'] = img

    return df


if __name__ == '__main__':
    demo(headless=False)
