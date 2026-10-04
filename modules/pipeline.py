"""Wires the four modules together."""
from data_ingestion import DataIngestion
from image_preprocessor import ImagePreprocessor
from model_inference_engine import ModelInferenceEngine
from alert_logger import AlertLogger


def run_pipeline(source: str, model_path: str, max_frames: int = 5) -> int:
    ingest = DataIngestion(source)
    prep = ImagePreprocessor()
    engine = ModelInferenceEngine(model_path)
    logger = AlertLogger()
    engine.load_model()
    ingest.connect()
    processed = 0
    for frame in ingest.stream(max_frames):
        result = engine.infer(prep.process(frame))
        logger.log(result)
        if logger.should_alert(result):
            print(logger.send_alert(result))
        processed += 1
    ingest.release()
    return processed


if __name__ == "__main__":
    print("Frames processed:", run_pipeline("rtsp://demo", "model.onnx"))
