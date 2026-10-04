"""ModelInferenceEngine: runs the detection model and cleans up its output."""
from typing import List
import time
import numpy as np
from types_common import ProcessedFrame, InferenceResult, Detection


class ModelInferenceEngine:
    """Loads the model, runs it on a frame and returns the detections."""

    def __init__(self, model_path: str, conf_threshold: float = 0.5,
                 iou_threshold: float = 0.45) -> None:
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self._model = None

    def load_model(self) -> None:
        """Load weights from disk (real version: ONNX / PyTorch / TFLite)."""
        self._model = object()  # placeholder for the real model

    def _raw_predict(self, tensor: np.ndarray) -> List[Detection]:
        """Run the model. Placeholder returns no detections."""
        return []

    def postprocess(self, detections: List[Detection],
                    scale: tuple) -> List[Detection]:
        """Remove low-confidence boxes and convert the rest to the original image size."""
        sx, sy = scale
        kept = []
        for d in detections:
            if d.confidence < self.conf_threshold:
                continue
            x1, y1, x2, y2 = d.bbox
            kept.append(Detection(d.label, d.confidence,
                                  (int(x1 * sx), int(y1 * sy),
                                   int(x2 * sx), int(y2 * sy))))
        return kept

    def infer(self, pframe: ProcessedFrame) -> InferenceResult:
        """Run the model on one processed frame."""
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        start = time.perf_counter()
        raw = self._raw_predict(pframe.tensor)
        final = self.postprocess(raw, pframe.scale)
        latency = (time.perf_counter() - start) * 1000.0
        return InferenceResult(pframe.frame_id, pframe.timestamp, final,
                               latency, pframe.camera_id)
