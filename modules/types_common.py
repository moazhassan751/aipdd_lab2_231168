"""Shared data types used by all modules."""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np


@dataclass
class Frame:
    """One raw camera frame."""
    frame_id: int
    timestamp: float            # seconds since epoch
    image: np.ndarray           # H x W x 3, uint8, BGR
    camera_id: str = "cam_01"


@dataclass
class ProcessedFrame:
    """A frame that is ready for the model."""
    frame_id: int
    timestamp: float
    tensor: np.ndarray          # 1 x 3 x H x W, float32, values 0..1
    scale: Tuple[float, float]  # (sx, sy) to map boxes back to original size
    camera_id: str = "cam_01"


@dataclass
class Detection:
    """One detected object."""
    label: str
    confidence: float           # 0.0 to 1.0
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2 in original image pixels
    embedding: Optional[np.ndarray] = None  # face feature vector, if a face
    student_id: Optional[str] = None        # set after face matching


@dataclass
class InferenceResult:
    frame_id: int
    timestamp: float
    detections: List[Detection] = field(default_factory=list)
    latency_ms: float = 0.0
    camera_id: str = "cam_01"
