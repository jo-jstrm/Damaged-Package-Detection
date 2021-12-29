Model Comparison and Choice for the Project
===========================================

*Written by Manuel Sauter*

In this section we highlight the decision making process regarding object detection architectures. 
In general there are two state-of-the-art types of CNN object detection architectures, namely two-stage detectors and one-stage detectors, which we both introduce briefly.

Two-Stage Detectors
###################

Two-stage object detection architectures are solving two separate tasks consecutively.
The first task is to propose regions that possibly contain objects that are relevant for the later classification. The first versions of two-stage object detection architectures proposed regions through exhaustive search or sliding windows. In more recent architectures, methods like selective search or regional proposal networks became more relevant.

The second task is to classify the objects inside the regional proposals. Therefore, the proposals will get fed into a CNN, where features get extracted. Based on these features, the objects inside the regional proposals are classified.
An early implementation of the two-stage approach is *R-CNN*. Based on that *Fast R-CNN*, *Faster R-CNN* and *Mask R-CNN* were developed and have greatly improved the performance.

One-Stage Detectors
###################

Object detection algorithms from this type of architecture are different from the two-stage approaches. Instead of using regions to localize the object within the image first and using a separate algorithm for this task, one-stage algorithms are only using a single convolutional network. While training on the full image this network can predict bounding boxes and the class probabilities simultaneously.

A famous one-stage detection algorithms is YOLO (*You Only Look Once*). YOLO splits the image into a grid of size SxS. Inside every cell of the grid YOLO predicts bounding boxes and a box confidence score for each bounding box. Every cell predicts a probability for every different class and is responsible for the one with the highest probability (in the first YOLO implementation).
More recent YOLO version not only greatly improved the performance and the error rate, but also accounted for different other weaknesses of earlier versions. 
In YOLOv2 the detection of several objects per grid cell was introduced through the usage of anchor boxes. Anchor boxes get defined by exploring the training data. Anchor boxes with different height/width ratios representing the different classes are used.
YOLOv3 introduced multi-label classification for objects that belong to different classes at the same time.
YOLOv4 is the most recent version and reaches state-of-the-art performance in object detection tasks.

Another famous and state-of-the-art group of one-stage object detection architectures besides YOLO are the *Single Shot MultiBox Detectors* (SSDs). One of the main differences compared to YOLO is the possibility for predictions of detections at multiple scales. This is achieved by a different architecture that contains series of convolution filters, which decrease in size progressively. This addresses the reduced performance of YOLO when working with relatively small objects.
Further, SSD contains a base network to extract feature maps. In this project MobileNet and RestNet are used for feature extraction. This base network can be easily switched and many base networks are available.

Comparison and Project Choice
#############################

Having the two different architectures at hand, the question arises which one to use for our use case. 
In general two-stage detectors seem to reach a high accuracy and precision and have been observed to be slower in comparison to the one-stage detectors.
Even though many inference and training improvements were made, this still holds true.
One of the limitations in the project is the Jetson Nano.
Looking at his computing power it becomes clear that a one-step approach is more likely to yield the desired results.
Also, frames per second (FPS) was an important factor for in choosing our model, which was also an argument for a one-stage detector.

Therefore, we focus on using one-stage detection architectures. 
As no team experience with the use of the different one-stage object detection architectures on the Jetson Nano hardware was available, we decided to not only focus on YOLO but also try out a SSD architecture with MobileNet and ResNet networks.
