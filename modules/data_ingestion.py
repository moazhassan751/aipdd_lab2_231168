"""DataIngestion: collects raw frames from a camera, video file or RTSP stream."""
from typing import Iterator, Optional
import time
import numpy as np
from types_common import Frame


class DataIngestion:
    """Reads frames from a camera or video file and gives them out one by one.

    It only collects the raw frames. It does not change them.
    """

    def __init__(self, source: str, camera_id: str = "cam_01",
                 target_fps: int = 15) -> None:
        self.source = source
        self.camera_id = camera_id
        self.target_fps = target_fps
        self._is_open = False
        self._count = 0

    def connect(self) -> bool:
        """Open the source. Returns True on success, False on failure."""
        self._is_open = True   # real version: cv2.VideoCapture(self.source)
        return self._is_open

    def read_frame(self) -> Optional[Frame]:
        """Return the next Frame, or None if the stream ended or dropped."""
        if not self._is_open:
            return None
        self._count += 1
        # Placeholder image. Real version reads from cv2.VideoCapture.
        image = np.zeros((720, 1280, 3), dtype=np.uint8)
        return Frame(self._count, time.time(), image, self.camera_id)

    def stream(self, max_frames: Optional[int] = None) -> Iterator[Frame]:
        """Yield frames until the source ends or max_frames is reached."""
        produced = 0
        while max_frames is None or produced < max_frames:
            frame = self.read_frame()
            if frame is None:
                break
            produced += 1
            yield frame

    def release(self) -> None:
        """Close the source and free resources."""
        self._is_open = False
