"""ssd_tf.py

This module implements the TfSSD class.
"""


import numpy as np
import cv2
from aisscv.inference.model_interface import Model
#import tensorflow.compat.v1.keras.backend as K
import tensorflow as tf
# tf.compat.v1.disable_eager_execution()
#from  tensorflow.python.ops.numpy_ops import np_config
# np_config.enable_numpy_behavior()


# REPLACE HERE WITH STUFF FROM INFERENCE NOTEBOOK

def _postprocess_tf(img, boxes, scores, classes, conf_th):
    """Postprocess TensorFlow SSD output."""
    h, w, _ = img.shape
    out_boxes = boxes[0].numpy() * np.array([h, w, h, w])
    out_boxes = out_boxes.astype(np.int32)
    out_boxes = out_boxes[:, [1, 0, 3, 2]]  # swap x's and y's
    out_confs = scores[0].numpy()
    out_clss = classes[0].numpy().astype(np.int32)

    # only return bboxes with confidence score above threshold
    mask = np.where(out_confs >= conf_th)
    return out_boxes[mask], out_confs[mask], out_clss[mask]


class TfSSD(Model):
    """TfSSD class encapsulates things needed to run TensorFlow SSD."""

    def __init__(self, model_path, input_shape):
        Model.__init__(self, model_path, input_shape)

        # Load pipeline config and build a detection model
        # configs = config_util.get_configs_from_pipeline_file(pipeline_config)
        # model_config = configs['model']
        # detection_model = model_builder.build(
        #     model_config=model_config, is_training=False)
        self.detect_fn = tf.saved_model.load(model_path)
        # load detection graph
        # ssd_graph = tf.Graph()
        # with ssd_graph.as_default():
        #     graph_def = tf.GraphDef()
        #     with tf.gfile.GFile(model_path, 'rb') as fid:
        #         serialized_graph = fid.read()
        #         graph_def.ParseFromString(serialized_graph)
        #         tf.import_graph_def(graph_def, name='')

        # # define input/output tensors
        # self.image_tensor = ssd_graph.get_tensor_by_name('image_tensor:0')
        # self.det_boxes = ssd_graph.get_tensor_by_name('detection_boxes:0')
        # self.det_scores = ssd_graph.get_tensor_by_name('detection_scores:0')
        # self.det_classes = ssd_graph.get_tensor_by_name('detection_classes:0')

        # # create the session for inferencing
        # self.sess = tf.Session(graph=ssd_graph)

    # def __del__(self):
    #     #self.sess.close()
    # @override
    def detect(self, img, conf_th):
        #img_resized = _preprocess_tf(img, self.input_shape)
        image_np = np.asarray(img)
        image_resized = cv2.resize(
            image_np, self.input_shape, interpolation=cv2.INTER_CUBIC)
        input_tensor = tf.convert_to_tensor(image_resized)
        # The model expects a batch of images, so add an axis with `tf.newaxis`.
        input_tensor = input_tensor[tf.newaxis, ...]

        # input_tensor = np.expand_dims(image_np, 0)
        detections = self.detect_fn(input_tensor)
        # print(detections)
        # boxes, scores, classes = self.sess.run(
        #     [self.det_boxes, self.det_scores, self.det_classes],
        #     feed_dict={self.image_tensor: np.expand_dims(img_resized, 0)})
        return _postprocess_tf(img, detections['detection_boxes'], detections['detection_scores'], detections['detection_classes'], conf_th)
