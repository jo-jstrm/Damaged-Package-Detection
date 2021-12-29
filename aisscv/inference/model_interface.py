class Model(object):
    """Interface for detection model.
    This allows a model-agnostic control loop"""

    def __init__(self, model_path, input_shape):
        self.model = model_path
        self.input_shape = input_shape
        self.index_offset = -1

    def detect(self, img, conf_th):
        """
        Abstract function. To be overritten
        """
        pass
