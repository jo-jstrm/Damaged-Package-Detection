# Tutorials for Users & Developers:

## Get started
Most things are easier if you use MacOS, Linux or the Windows Subsysmtem for Linux, which is a Linux System integrated into Windows. 
Read [here](https://docs.microsoft.com/en-us/windows/wsl/install-win10) to activate WSL on you Windows machine. 

Running natively on Windows is of course also possible, but will require some additional steps from time to time. 
The following commands assume, that you have a terminal (e.g. anaconda prompt or git bash on windows), with cwd in the Repo Base folder.

### Setup Unix-like (MacOS, Ubuntu, Windows Subsystem for Linux ,etc)
1. To get everything installed run  
```make setup``` in the home directory of this repository

### Setup on Windows
1. To get everything installed run 
```pip install -r requirements.txt``` and 
``` pip install -e .``` (This will install our aisscv package. the ```-e``` parameter means editable. This means, when you edit a file of the module it will directly be used in the package instead of the need to reinstalling everything. However for some users it only works without the ```-e```). 
2. If you want to use the TensorFlow Object detection api run ```git submodule update --init --recursive```. 
This will download the API in the folder [tf-models](./tf-models)

### First Steps. 
A good starting point would be to visualize and validate your own labels. 
So when you completed the setup, run a new python script or a jupyter notebbook. Pay attention that you are in the same virual environment / conda environment as where the package was installed, or install the package again in the correct environment. 
Then you could run the following steps. 
1. ``` from aisscv.utils import label_helper, label_reader``` to import the label_helper and reader functions.
2. ```df = label_reader.via_json_to_df("PATH_TO_YOUR_LABEL_FILE", "PATH_TO_YOUR_IMAGES")```or the eqiuvalent coco-function if you used the coco-format for export. This reads in the exported labels and stores them in a ```pandas.DataFrame``` object. 
3. ```label_helper.visualize_labels(df, 15) ``` which will sample 15 of your images with labels and show them. Click the opened window and press Enter to see the next image or any other key to quit. 

Checkout the docstring which describe every parameter and the function itself. 
If you get any exception reach out to the group to get help!

## Training with the Tensorflow Object Detection API
This will be a little work....

### Prerequisites
- First, make sure that you have docker installed and are able to run it. For Windows, the easiest way is with Windows Subsystem for Linux (check First Steps), as explained here: [Docker for Windows](https://docs.docker.com/docker-for-windows/install/)
- Ensure, the the TF API exists in the folder [tf-models](./tf-models). If it does not exists, check the setup section (run ```git submodule update --init --recursive```)
- Make sure, that all the labels you want to used are saved in pasval-voc format in [```data/labels/pascal```](./data/labels/pascal). Use our util functions to convert coco/json to pascal-voc. In [```utils```](./aisscv/utils) we have a [notebook](./aisscv/utils/labels_to_pascal.ipynb) that goes through the steps.  
- Make sure, that all the images you want to use are placed in [```data/images/ALL_IMAGES```](./data/images/ALL_IMAGES)

### Steps
Now, we will walk through the steps for the ssd_mobilenet. Of course this is directly applicable to any other model of the [Tensorflow Object Detection Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md), so feel free to download another model and try it out!

To run the container with GPU-Support please refer to [this](https://www.tensorflow.org/install/docker) information to adjust the commands accordingly. 

1. Use the Terminal and navigate to the home of our repo. Run ```docker build -f Dockerfile.tftrain -t tf-train-image .``` 
This will take quite a while. We should push those images later to a registry to speed up this step.
2. Start the container by running ```docker run -it -v $(pwd):/home/app -p 6010:6010 --name tf-training tf-train-image```.
For Windows users ```$(pwd)``` needs to be replaced with ```${pwd}```.
If there are any whitespaces in the path, the respective section needs to be enclosed in quotation marks ``` 'section with whitespaces' ```.
This will open a shell inside the container. 
3. Now, let's create the tfrecord, that will be used for training: ```python aisscv/utils/pascal_voc_to_tfrecord.py -x data/annotations/pascal/ -i data/images/ALL_IMAGES -l data/annotations/label_map.pbtxt -o data/all_data.record```. Since the Repos is passed as a volume, you should (in case of success) now see the newly created tfrecord in the data directory in our repo. 
4. Before you start the training, checkout the [config file](./models/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8/pipeline.config), the you are abel to change parameters like the learning rate, the batch size, etc.... Currently the batch size is set to 2, because otherwise my pc runs out of memory using a larger batch size. if you are using a GPU with cuda, or have large RAM increase the batch size!
5. Start the training: ```python tf-models/research/object_detection/model_main_tf2.py --model_dir=./models/finetuned --pipeline_config_path=./models/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8/pipeline.config --alsologtostderr```
6. To monitor the training process with tensorboard, open a new terminal. Run ```docker exec tf-training tensorboard --logdir /home/app/models/finetuned --port=6010 --bind_all```
## Connect to Jetson via ssh
Unfortunately it is not trivial to setup a connection to the jetson via the internet. (Thanks vodafone for not allowing Port-Forwarding on ipv6...) \
Also teamviewer is not available for jetson nano and I have not yet been able to install the raspi-version... \
So current workaround is ssh, which only works until a reboot (I guess), because the domain will change afterwards. \

Domain: 6.tcp.ngrok.io 

Port: 12227 

On unix-like connect via:
`ssh aiss@6.tcp.ngrok.io -p 12227` 

on Windows do something with [PuTTY](https://www.putty.org/). 
Also fell free to contact [Joel](mailto:joel.oswald@student.kit.edu) to get your public ssh key added. 

Another possibility is to use remote.it, whcih also allows a tunneled acces to the jetson. 
Create a free acout ad contact [Joel](mailto:joel.oswald@student.kit.edu), he will share the device-acces with your account. 

---
# YOLO Local Setup

## a) Local Install on Unix-Like
### Install Darknet/YOLO
1. Make sure you fulfill the [requirements](https://github.com/AlexeyAB/darknet#requirements)
1. `git clone https://github.com/AlexeyAB/darknet.git`
1. Download pre-trained weights [here](https://github.com/AlexeyAB/darknet#pre-trained-models)
1. `cd darknet && make`
    - For GPU and cuDNN (faster training) support, set `GPU=1` and `CUDNN=1` in `Makefile` before running `make`
    - For video support, set `OPENCV=1`

### Try out Yolo
1. `cd darknet`
1. `./darknet detector test cfg/coco.data cfg/yolov4-tiny.cfg /path/to/yolov4.weights -thresh 0.25 -ext_output /path/to/a/picture.png`
    - Will save an image with the prediction in the darknet directory

## b) Use Docker
Option a) Use my pre-built image
1. Download pre-built image: `docker pull 74797469/yolo` (or one from below)
    - `74797469/yolo` refers to the image using CUDA/cuDNN
    - `74797469/yolo-amd64-cpu` refers to the one without CUDA/CUDNN/OpenCV (e.g. for basic Windows)
1. Run image
    - Unix-Like: `docker run -it -v "$HOME"/yolo-data:/yolo-data 74797469/yolo` 
    - Windows (without CUDA): `docker run -it -v Path\to\weights-and-images:/yolo-data 74797469/yolo-amd64-cpu` 
    - `-v "$HOME"/yolo-data:/yolo-data` defines a mount point that shares persistent data between your computer and the docker container. So place the weights, images etc. in `$HOME/yolo-data` and they will be available inside the container under `/yolo-data`
    - `-it` is for interactive mode with a terminal, so that you can run commands inside the container

Option b) Build image from Dockerfile
- `docker build -f Dockerfile.yolo-XX -t name-for-my-own-yolo-image .` (Do not forget the ".")
- `docker run [...]` as above but with your image name instead of "74797469/yolo[...]"

## Docker on Jetson
### Build for Jetson on amd64 Processor
__Disclaimer__: Currently only compiles without CUDA/cuDNN.

This built works by utilizing the new dockler build system `buildx` and using a binfmt/QEMU Docker image that registers as a new Docker build context. This way you avoid installing and setting up QEMU on your machine. (Tested on Ubuntu 18.04)
1. To illustrate the changes that happen later: `docker buildx ls`
1. Get and run docker binfmt container: `docker run --privileged --rm docker/binfmt:a7996909642ee92942dcd6cff44b9b95f08dad64`
1. You should now see more options here: `docker buildx ls`
1. Build container with buildx: `docker buildx build --platform linux/arm64 -f Dockerfile.yolo-jetson -t yolo-jetson .`

### Build Jetson-Image on Jetson (not tested yet)
1. `docker build -f Dockerfile.yolo-jetson -t yolo-jetson .`
