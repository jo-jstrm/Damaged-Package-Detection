"""ControlLoop.py

Key Loop for our AISS_CV Projekt. 
Heavily based on the work of jkjung: https://github.com/jkjung-avt/tensorrt_demos
"""


import os
import time
import argparse
import numpy as np
import cv2
import pycuda.autoinit  # This is needed for initializing CUDA driver
import requests
import threading
import traceback
from aisscv.inference.model_interface import Model
from aisscv.inference.camera import add_camera_args, Camera
from aisscv.inference.display import open_window, set_display, show_fps
from aisscv.inference.visualization import BBoxVisualization
from aisscv.inference.yolo_with_plugins import TrtYOLO
from aisscv.inference.ssd_tf import TfSSD
import logging


logger = logging.getLogger('inference')
logger.setLevel(logging.DEBUG)

WINDOW_NAME = 'PandamicPackage'


def parse_args():
    """Parse command line arguments."""
    desc = ('Capture and display live camera video, while doing '
            'real-time object detection with TensorRT optimized '
            'YOLO model on Jetson')
    parser = argparse.ArgumentParser(description=desc)
    parser = add_camera_args(parser)
    parser.add_argument(
        '-c', '--category_num', type=int, default=80,
        help='number of object categories [80]')
    parser.add_argument(
        '-m', '--model', type=str, required=True,
        help=('[aisscv-yolov4-tiny-2class|tf'))
    parser.add_argument(
        '-l', '--letter_box', action='store_true',
        help='inference with letterboxed image [False]')
    parser.add_argument(
        '--headless', action='store_true',
        help='Do not show images in an X.Org-Window')
    args = parser.parse_args()
    return args


def notify(img: np.ndarray, damage: str = 'Damage'):
    """
    Call Pushover-API to notify smartphone about warning.
    Please call in a thread, as this will block the loop otherwise. 

    Parameters
    ----------
    img : np.ndarray
        Opencv image that should be transmitted
    damage : str
        Name of the damage that should be displayed

    Returns
    -------
    None

    """
    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": "azfjvmj5p96sydm337nqsezsc3ts5h",
        "user": "urjgtk3d1o6yp9sv5ngi2zg1ooo6pn",
        "message": "WARNING- Detected Package with {}".format(damage)
    },
        files={
        "attachment": ("image.jpg", cv2.imencode('.jpeg', img)[1].tobytes(), "image/jpeg")
    })
    logger.info(r.text)


def loop_and_detect(cam: Camera, model: Model, conf_th: float, vis: BBoxVisualization, cls_dict: dict, freq: int = 10, headless: bool = False) -> None:
    """
    Continuously capture images from camera and detectt Boxes&Damages. 
    If an image is detected, notify the connected phones via pushover API (in a thread, so that the loop may go on).
    If not in headless mode, this function will also display a window with current detections.

    Parameters
    ----------
    cam: 
        the camera instance (video source).
    model: 
        the object detector instance wich implements the model_interface (e.g. TRT-Yolo or Tf-SSD).
    conf_th: 
        confidence/score threshold for object detection.
    cls_dict: 
        Dictionary which assigns a class name to each index.
    vis: 
        for visualization.
    freq: int,
        frequency to run the control loop
    headless: bool
        prevent the image and boxes to be visualized in an X-Window

    Returns
    -------
    None

    """

    full_scrn = False
    fps = 0.0
    tic = time.time()
    cycle_time = 1/freq
    cooldown_ttg = 0
    confirm_cycles = 0
    curr_fps = 0
    while True:
        try:
            if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
                break
            img = cam.read()
            if img is None:
                break

            boxes, confs, clss = model.detect(img, conf_th)
            clss = clss+model.index_offset
            img = vis.draw_bboxes(img, boxes, confs, clss)

            if np.any(clss != 0) and cooldown_ttg == 0:
                damage = clss[np.where(clss != 0)][0]
                logger.info('Found some damage')
                confirm_cycles += 1
                if confirm_cycles >= 3:
                    logger.info('DAMAGE LOCKED IN')
                    threading.Thread(target=notify, args=(
                        img, cls_dict[damage])).start()
                    confirm_cycles = 0
                    cooldown_ttg = 50

            else:
                confirm_cycles = 0
                cooldown_ttg = max(cooldown_ttg-1, 0)

            img = show_fps(img, fps)
            logger.info('FPS: {}'.format(curr_fps))
            cv2.imshow(WINDOW_NAME, img)
            toc = time.time()
            #print('toc-tic=', toc-tic)
            curr_fps = 1.0 / (toc - tic)
            # calculate an exponentially decaying average of fps number
            fps = curr_fps if fps == 0.0 else (fps*0.95 + curr_fps*0.05)
            sleep_time = cycle_time-(toc-tic)
            tic = toc
            if not headless:
                key = cv2.waitKey(1)
                if key == 27 or key == ord('q'):  # ESC key: quit program
                    break
                elif key == ord('F') or key == ord('f'):  # Toggle fullscreen
                    full_scrn = not full_scrn
                    set_display(WINDOW_NAME, full_scrn)
                elif key == ord('R') or key == ord('r'):  # Toggle fullscreen
                    img_name = f'images/{time.strftime("%Y-%m-%d-%H-%M-%S")}.jpg'
                    cv2.imwrite(img_name, img)
                    print('Wrote image ',
                          f'images/{time.strftime("%Y-%m-%d-%H-%M-%S")}.jpg')

            # Sleep for remaining time of the cycle
            print('Remaining time: ', max(sleep_time, 0))
            time.sleep(max(sleep_time, 0))
        except Exception as e:
            logger.error('Exception: ', str(e))
            logger.error(traceback.format_exc())
            break  # REMOVE THIS! ONLY FOR DEBUGGInG


def main() -> None:
    """
    Main Function that reads arguments and sets up the control loop. 
    End with 'ESC' or 'q' key to properly close camera stream

    Returns
    -------
    None
    """
    args = parse_args()
    if args.category_num <= 0:
        raise SystemExit('ERROR: bad category_num (%d)!' % args.category_num)
    if not os.path.exists('{}'.format(args.model)):
        logger.error('file {} not found'.format(args.model))

    cam = Camera(args)
    if not cam.isOpened():
        raise SystemExit('ERROR: failed to open camera!')

    cls_dict = {
        0: "BOX",
        1: "WET",
        2: "DENT",
        3: "HOLE",
        4: "OPENING"
    }

    vis = BBoxVisualization(cls_dict)

    # TODO: Seperate for tensorflow/YOLO model
    #model = TrtYOLO(os.path.join('inference_models', args.model), args.category_num, args.letter_box)
    model_type = ""
    try:
        if 'yolo' in args.model.lower():
            model = TrtYOLO(args.model, args.category_num, args.letter_box)
            model_type = 'YOLO'
            logger.info('loaded yolo model')
        else:
            model = TfSSD(args.model, (320, 320))
            model_type = 'TF'
            logger.info('loaded tensorflow model')

    except Exception as e:
        logger.error('Failed to laod model')
        logger.error('Exception: ', str(e))
        print(traceback.format_exc())

    open_window(
        WINDOW_NAME, WINDOW_NAME + ' - ' + model_type,
        cam.img_width, cam.img_height)
    loop_and_detect(cam, model=model, conf_th=0.35,
                    cls_dict=cls_dict, freq=25, vis=vis, headless=args.headless)

    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print("in main")
    main()
