"""ImagePreprocessor: changes a raw frame into the input the model needs."""
from typing import Tuple
import numpy as np
from types_common import Frame, ProcessedFrame


class ImagePreprocessor:
    """Gets a frame ready for the model.

    It resizes the frame, scales the pixel values and arranges the channels.
    """

    def __init__(self, target_size: Tuple[int, int] = (640, 640)) -> None:
        self.target_width, self.target_height = target_size

    def resize(self, image: np.ndarray) -> np.ndarray:
        """Change the image to the target size."""
        h, w = image.shape[:2]
        ys = (np.arange(self.target_height) * h / self.target_height).astype(int)
        xs = (np.arange(self.target_width) * w / self.target_width).astype(int)
        return image[ys][:, xs]

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """Change pixel values from the range 0 to 255 into the range 0 to 1."""
        return image.astype(np.float32) / 255.0

    def process(self, frame: Frame) -> ProcessedFrame:
        """Run all steps: resize, scale values, change BGR to RGB, rearrange the shape."""
        h, w = frame.image.shape[:2]
        resized = self.resize(frame.image)
        norm = self.normalize(resized)
        rgb = norm[:, :, ::-1]
        tensor = np.transpose(rgb, (2, 0, 1))[np.newaxis, ...]
        scale = (w / self.target_width, h / self.target_height)
        return ProcessedFrame(frame.frame_id, frame.timestamp,
                              np.ascontiguousarray(tensor), scale,
                              frame.camera_id)
