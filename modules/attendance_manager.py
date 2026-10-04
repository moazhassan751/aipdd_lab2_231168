"""AttendanceManager: student records, face matching, attendance and sync."""
from typing import Callable, Dict, List, Optional, Set, Tuple
import numpy as np
from types_common import InferenceResult


class AttendanceManager:
    """Keeps registered students, matches faces and records attendance.

    It covers face matching, one attendance record per student per class,
    sending records to the central database, and admin changes to student data.
    """

    def __init__(self, match_threshold: float = 0.6) -> None:
        self.match_threshold = match_threshold
        self._students: Dict[str, Tuple[str, np.ndarray]] = {}
        self._marked: Set[Tuple[str, str]] = set()   # (session_id, student_id)
        self._pending: List[dict] = []                # records not yet sent

    # ---- admin functions (FR-05) ----
    def register_student(self, student_id: str, name: str,
                         face_vector: np.ndarray) -> None:
        """Add a student, or replace the data of an existing student."""
        self._students[student_id] = (name, face_vector / np.linalg.norm(face_vector))

    def remove_student(self, student_id: str) -> bool:
        """Delete a student. Returns False if the student was not found."""
        return self._students.pop(student_id, None) is not None

    # ---- face matching (FR-02) ----
    def match_face(self, face_vector: np.ndarray) -> Optional[str]:
        """Return the student ID with the highest similarity above the threshold."""
        query = face_vector / np.linalg.norm(face_vector)
        best_id, best_score = None, self.match_threshold
        for sid, (_, vec) in self._students.items():
            score = float(np.dot(query, vec))
            if score >= best_score:
                best_id, best_score = sid, score
        return best_id

    # ---- attendance records (FR-03) ----
    def mark_attendance(self, student_id: str, timestamp: float,
                        camera_id: str, session_id: str) -> bool:
        """Save one record per student per session. Returns False if a duplicate."""
        key = (session_id, student_id)
        if key in self._marked:
            return False
        self._marked.add(key)
        self._pending.append({"student_id": student_id, "timestamp": timestamp,
                              "camera_id": camera_id, "session_id": session_id})
        return True

    def process_result(self, result: InferenceResult, session_id: str) -> List[str]:
        """Match every face in a result and mark attendance. Returns new IDs."""
        new_ids = []
        for d in result.detections:
            if d.embedding is None:
                continue
            sid = self.match_face(d.embedding)
            if sid is None:
                continue
            d.student_id = sid
            if self.mark_attendance(sid, result.timestamp, result.camera_id,
                                    session_id):
                new_ids.append(sid)
        return new_ids

    # ---- database sync (FR-04) ----
    def sync_pending(self, send_fn: Callable[[dict], bool]) -> int:
        """Send waiting records. Records that fail stay in the list for retry."""
        still_waiting, sent = [], 0
        for rec in self._pending:
            try:
                ok = send_fn(rec)
            except Exception:
                ok = False
            if ok:
                sent += 1
            else:
                still_waiting.append(rec)
        self._pending = still_waiting
        return sent

    def pending_count(self) -> int:
        return len(self._pending)
