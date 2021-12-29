# YOLO Training
- yolov4:
    - `./darknet detector train /home/jo/Downloads/yolo-data/training-config/aisscv-yolo.data /home/jo/Downloads/yolo-data/training-config/aisscv-yolov4-tiny-5classes.cfg /home/jo/Downloads/yolo-data/weights/pre-trained/aisscv-yolov4.conv.137 -map`
- yolov4-tiny:
    - `./darknet detector train /home/jo/Downloads/yolo-data/training-config/2-class/aisscv-yolo-2class.data /home/jo/Downloads/yolo-data/training-config/2-class/aisscv-yolov4-tiny-2class.cfg /home/jo/Downloads/yolo-data/weights/pre-trained/aisscv-yolov4-tiny.conv.29 -map`

## Docker
- `nvidia-docker run -it -p 8888:8888 -v /home/jo/Downloads/yolo-data/training-data/dataset_final_02_yolo/train:/training-data 74797469/yolo-amd64-gpu:latest`
- `/darknet/darknet detector train /training/aisscv-yolo-2class.data /training/aisscv-yolov4-tiny-2class.cfg /training/yolov4-tiny.conv.29 -map -dont_show -mjpeg_port 8888`

## Azure
- `az container create -g aiss-cv -f azure_yolo_train.yaml`