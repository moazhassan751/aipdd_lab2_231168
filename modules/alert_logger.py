"""AlertLogger: decides when to send an alert and saves all results."""
from typing import Callable, Optional, Set
import csv
import os
from types_common import InferenceResult


class AlertLogger:
    """Saves log entries and creates alerts for the labels being watched."""

    def __init__(self, log_path: str = "detections_log.csv",
                 alert_labels: Set[str] = None,
                 alert_confidence: float = 0.7,
                 notifier: Optional[Callable[[str], None]] = None) -> None:
        # notifier sends the message (SMS, email, app). It is passed in so the
        # delivery service can be changed without changing this class.
        self.notifier = notifier
        self.log_path = log_path
        self.alert_labels = alert_labels or {"person", "weapon"}
        self.alert_confidence = alert_confidence
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="") as f:
                csv.writer(f).writerow(
                    ["frame_id", "timestamp", "camera_id", "label",
                     "confidence", "x1", "y1", "x2", "y2"])

    def log(self, result: InferenceResult) -> int:
        """Add all detections to the CSV file. Returns the number of rows written."""
        with open(self.log_path, "a", newline="") as f:
            w = csv.writer(f)
            for d in result.detections:
                w.writerow([result.frame_id, result.timestamp,
                            result.camera_id, d.label,
                            round(d.confidence, 4), *d.bbox])
        return len(result.detections)

    def should_alert(self, result: InferenceResult) -> bool:
        """Return True if a watched label is found at or above the alert confidence."""
        return any(d.label in self.alert_labels
                   and d.confidence >= self.alert_confidence
                   for d in result.detections)

    def send_alert(self, result: InferenceResult) -> str:
        """Create the alert message, send it with the notifier, and return it."""
        labels = sorted({d.label for d in result.detections
                         if d.label in self.alert_labels})
        message = (f"ALERT camera={result.camera_id} frame={result.frame_id} "
                   f"labels={','.join(labels)}")
        if self.notifier is not None:
            self.notifier(message)
        return message
