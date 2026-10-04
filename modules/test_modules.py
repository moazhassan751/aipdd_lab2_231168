"""Quick tests to prove every module works."""
import os, tempfile
import numpy as np
from types_common import Frame, ProcessedFrame, Detection, InferenceResult
from data_ingestion import DataIngestion
from image_preprocessor import ImagePreprocessor
from model_inference_engine import ModelInferenceEngine
from alert_logger import AlertLogger
import pipeline
from attendance_manager import AttendanceManager


def test_ingestion():
    d = DataIngestion("rtsp://x"); assert d.connect()
    frames = list(d.stream(3)); assert len(frames) == 3
    d.release(); assert d.read_frame() is None


def test_preprocessor():
    f = Frame(1, 0.0, np.full((720, 1280, 3), 255, np.uint8))
    p = ImagePreprocessor((640, 640)).process(f)
    assert p.tensor.shape == (1, 3, 640, 640)
    assert p.tensor.dtype == np.float32 and p.tensor.max() == 1.0
    assert p.scale == (2.0, 1.125)


def test_engine():
    e = ModelInferenceEngine("m.onnx", conf_threshold=0.5)
    pf = ProcessedFrame(1, 0.0, np.zeros((1, 3, 640, 640), np.float32), (2.0, 1.0))
    try:
        e.infer(pf); assert False
    except RuntimeError:
        pass
    e.load_model()
    assert e.infer(pf).detections == []
    out = e.postprocess([Detection("person", 0.9, (10, 10, 20, 20)),
                         Detection("cat", 0.2, (1, 1, 2, 2))], (2.0, 1.0))
    assert len(out) == 1 and out[0].bbox == (20, 10, 40, 20)


def test_logger():
    path = os.path.join(tempfile.mkdtemp(), "log.csv")
    lg = AlertLogger(path)
    r = InferenceResult(1, 0.0, [Detection("person", 0.9, (1, 2, 3, 4))])
    assert lg.log(r) == 1 and lg.should_alert(r)
    assert "person" in lg.send_alert(r)
    assert not lg.should_alert(InferenceResult(2, 0.0, [Detection("cat", 0.99, (0, 0, 1, 1))]))


def test_pipeline():
    os.chdir(tempfile.mkdtemp())
    assert pipeline.run_pipeline("rtsp://x", "m.onnx", 4) == 4


def test_attendance():
    m = AttendanceManager(0.6)
    m.register_student("S1", "Ali", np.array([1.0, 0.0, 0.0]))
    m.register_student("S2", "Sara", np.array([0.0, 1.0, 0.0]))
    assert m.match_face(np.array([0.9, 0.1, 0.0])) == "S1"
    assert m.match_face(np.array([0.0, 0.0, 1.0])) is None
    r = InferenceResult(1, 5.0, [Detection("face", 0.9, (0, 0, 5, 5), np.array([0.0, 1.0, 0.0]))])
    assert m.process_result(r, "class1") == ["S2"]
    assert m.process_result(r, "class1") == []          # no duplicate
    assert m.pending_count() == 1
    assert m.sync_pending(lambda rec: False) == 0       # network down
    assert m.pending_count() == 1                       # kept for retry
    assert m.sync_pending(lambda rec: True) == 1
    assert m.pending_count() == 0
    assert m.remove_student("S1") and not m.remove_student("S1")


def test_notifier():
    sent = []
    lg = AlertLogger(os.path.join(tempfile.mkdtemp(), "l.csv"), notifier=sent.append)
    r = InferenceResult(7, 0.0, [Detection("person", 0.95, (1, 2, 3, 4))])
    lg.send_alert(r)
    assert len(sent) == 1 and "frame=7" in sent[0]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("PASS", name)
