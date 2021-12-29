
import logging
import pandas as pd
from tqdm import tqdm
from aisscv.utils import label_reader, label_helper
import os
from hashlib import md5
import imageio
import imgaug as ia
from imgaug import augmenters as iaa
import matplotlib.pyplot as plt
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
import numpy as np

utils_logger = logging.getLogger('utils')
utils_logger.setLevel(logging.DEBUG)
aug_logger = logging.getLogger('augmenter')


def augment_one(image: imageio.core.util.Array, repetitions: int = 3, num_augmenters: int = 2, bboxes: np.array = None, polygons: np.array = None, show: bool = False) -> tuple:
    """
    Augment one image multiple times. Boundingbboxes can be passed to be augmented in the same way the image is augmented.
    The augmentations is seperated into two steps:

        - pixel augmentations that do not affect the bounding box
        - affine augmentations that change the shape of the image, and hence the bounding boxes

    For each iteration, some of the augmentations are chosen of each type. Each augmentation itself is random again in the intensity it is applied.

    Parameters
    ----------
    image: imageio.core.util.Array or np.ndarray
        image to be augmented, numpy-like
    repetitions: int
        How many pictures to create out of the input image.
    num_augmenters: int
        How many augmentations steps of each class (pixel and affine) are applied
    bboxes: np.ndarray or list of list
        List or array containing multiple bounding boxes in format [[xmin,xmax,ymin,ymax],[...],...]
    polygons: np.array or list of lists
        polygons to be augmented. NOT YET IMPLEMENTED
    show: boolean, optional
        wether to open a window wich shows the augmented images

    Returns
    -------
    list: [images_list, bbox_list]

    """
    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=box[0], x2=box[2], y1=box[1], y2=box[3]) for box in bboxes], shape=image.shape)

    aug_logger.debug(
        'BBS infos: type: {} - shape - {}'.format(type(bbs), bbs.shape))
    pixel_aug = iaa.SomeOf(num_augmenters,
                           # Color Operations: distort color channels without impacting bounding boxes
                           [
                               # Darker/Brighter
                               iaa.Multiply((0.6, 1.4), per_channel=False),
                               # Equalize colorintensities
                               iaa.pillike.Equalize((1, 10)),
                               # Enhance Color of grey-like images
                               iaa.pillike.EnhanceColor((0.0, 1.0)),
                               # iaa.pillike.Solarize(0.2, threshold=(32, 128)),
                               # Random grey boxes on the image
                               iaa.Cutout(size=(0.05, 0.2),
                                          nb_iterations=(1, 4)),
                               # Pixel Noise
                               iaa.AdditiveGaussianNoise(
                                   scale=(10, 40))
                           ], random_order=True)

    affine_aug = iaa.SomeOf(num_augmenters,
                            # Geometric Operations: distort image content altering location & size of bounding boxes
                            [
                                # Rotate by one of the given angles
                                iaa.Affine(rotate=[0, 20, -20, 90, -90]),
                                # Stretch in X direction
                                iaa.ShearX((-10, 10)),
                                # Stretch in Y direction
                                iaa.ShearY((-10, 10)),
                                # Randomly crop margin of image
                                iaa.Crop(percent=(0, 0.15))],
                            # iaa.PerspectiveTransform(scale=(0.01, 0.15)), #Not used because corrupts bounding boxes
                            random_order=True)

    images = np.repeat(image[None, :], repetitions, 0)
    bbs_batch = [bbs for i in range(repetitions)]
    aug_logger.debug('Image shape: {}'.format(images.shape))

    images_aug_1 = pixel_aug(images=images)
    images_aug_2, bbs_aug = affine_aug(
        images=images_aug_1, bounding_boxes=bbs_batch)
    aug_logger.debug('Augmented Images shape: {}'.format(images_aug_2.shape))

    if show:
        fig = plt.figure(figsize=(10, 7))
        # fig.set_figheight(25)
        rows = (repetitions+1) % 5
        columns = np.ceil(repetitions/rows)+1
        fig.set_figwidth(3*(repetitions+1))
        thickness = int(image.shape[1]/500)
        fig.add_subplot(rows, columns, 1)
        plt.title('Original')
        plt.imshow(bbs.draw_on_image(image, size=thickness))
        for i in range(0, repetitions):
            img = images_aug_2[i]
            fig.add_subplot(rows, columns, i+2)
            plt.title('Augmentation #{}'.format(i+1))
            plt.imshow(bbs_aug[i].draw_on_image(img, size=thickness))
        plt.show()

    bboxes_list = []

    bboxes_list.append([{'xmin': box[0][0], 'xmax': box[1][1],
                       'ymin': box[0][1], 'ymax': box[1][1]} for box in bbs])
    for box_set in bbs_aug:
        bboxes_list.append([{'xmin': box.coords[0][0], 'xmax': box.coords[1][0],
                           'ymin': box.coords[0][1], 'ymax': box.coords[1][1]} for box in box_set])

    return (np.insert(images_aug_2, 0, image, axis=0), bboxes_list)


def create_augmented_dataset(source_dir: str, label_path: str, target_dir: str, repetitions_per_image: int = 5,  stop_after: int = False) -> None:
    """
    Function which creates an entire augmented Dataset. Reads in JSON/COCO and images.
    Write out the images + xml-labels to the specified directory. This takes only packages into account!

    Parameters
    ----------
    source_dir : str
        Source images that should be augmented
    label_path : str
        Path to the label file in json/coco format.
    target_dir : str
        Directory where the final, augmented dataset is saved, along with the labels.
    repetitions_per_image: int, optional
        How many augmented images to create per real image. Defaults to 5.
    stop_after: int
        Stop the loop after so many steps

    Returns
    -------
    None

    """
    files = os.listdir()
    if not os.path.exists(os.path.join(target_dir, 'annotations')):
        os.mkdir(os.path.join(target_dir, 'annotations'))
    label_df = label_reader.via_coco_to_df(label_path, source_dir, poly_to_box=True) if 'coco' in label_path else label_reader.via_json_to_df(
        label_path, source_dir, poly_to_box=True)
    df_augmented = pd.DataFrame(columns=label_df.columns)
    for index, row in tqdm(label_df.iterrows(), total=label_df.shape[0]):
        if stop_after and (index > stop_after):
            break
        # For Image in Directory
        try:
            path = row['path']

            # Read in Image
            img = imageio.imread(path)

            # Readin label
            objects = [i for i in row['objects'] if i['name'] == 'box']
            bboxes = [[o['bndbox']['xmin'], o['bndbox']['ymin'],
                       o['bndbox']['xmax'], o['bndbox']['ymax']] for o in objects]

            # Augment image with bobxes/polygons
            images, boxes = augment_one(
                image=img, num_augmenters=2, repetitions=repetitions_per_image, bboxes=bboxes, show=False)

            for ind, image in enumerate(images):
                #  Save image to target dir
                name = md5(image).hexdigest() + '.png'

                augmented_objects = [{'name': 'box', 'pose': 0, 'truncated': 0,
                                      'difficult': 0, 'bndbox': img_box} for img_box in boxes[ind]]
                df_augmented = df_augmented.append({'folder': target_dir, 'path': os.path.join(target_dir, name), 'filename': name, 'size': (
                    image.shape[1], image.shape[0]), 'objects': augmented_objects}, ignore_index=True)

                # Save label to target dir
                imageio.imsave(os.path.join(target_dir, name), image)

                aug_logger.info('Saved image to {}'.format(
                    os.path.join(target_dir, name)))

                label_helper.write_to_pascal_voc(
                    df_augmented.iloc[[-1], :], os.path.join(target_dir, 'annotations'), False)
                aug_logger.debug('Saved label to {}'.format(os.path.join(
                    target_dir, 'annotations', name+'.xml')))

        except Exception as e:
            aug_logger.error('Failed on index {}'.format(index))
            print(e)
            continue
    df_augmented.to_csv(os.path.join(
        target_dir, 'annotations')+label_path.split('/')[-1].split('.')[0]+'.csv')
    aug_logger.info(f'Wrote{df_augmented.shape[0]} labels to directory...')


def main(test=False):
    for label_path in ['../../data/annotations/labels_joel_json.json']:
        create_augmented_dataset(source_dir='../../data/images/joel',
                                 label_path=label_path, target_dir='../../data/augmented', with_labels=True, repetitions_per_image=5, stop_after=False)


if __name__ == '__main__':
    main()
