"""Convert the trained RandomForest pipeline into ONNX format."""

from pathlib import Path
import json
import joblib
import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.pipeline import Pipeline


def convert_model() -> None:
    """Convert the persisted scaler + model into a single ONNX graph."""

    print("FinGuard AI - ONNX Conversion")
    print("=" * 50)
    
    ml_dir = Path("ml")
    model_path = ml_dir / "model.pkl"
    scaler_path = ml_dir / "scaler.pkl"
    features_path = ml_dir / "features.json"

    if not model_path.exists() or not scaler_path.exists():
        raise FileNotFoundError(
            "Missing model artifacts. Run ml/train.py before conversion."
        )

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    with open(features_path) as f:
        features_config = json.load(f)
    
    feature_names = features_config["features"]
    n_features = len(feature_names)
    
    print(f"Model features: {n_features}")
    print(f"Features: {', '.join(feature_names)}")
    
    initial_type = [("float_input", FloatTensorType([None, n_features]))]
    
    pipeline = Pipeline([
        ("scaler", scaler),
        ("classifier", model),
    ])

    print("Converting pipeline...")
    onnx_model = convert_sklearn(
        pipeline,
        initial_types=initial_type,
        options={"classifier": {"zipmap": False, "output_class_labels": True}},
        target_opset=17,
    )
    
    onnx_path = ml_dir / "model.onnx"
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
    
    size_mb = onnx_path.stat().st_size / (1024 * 1024)
    print(f"ONNX model saved -> {onnx_path} ({size_mb:.2f} MB)")

    import onnxruntime as ort

    session = ort.InferenceSession(str(onnx_path))
    input_name = session.get_inputs()[0].name
    output_names = [o.name for o in session.get_outputs()]
    probability_output = output_names[-1]

    dummy_features = np.linspace(0.1, 1.0, n_features, dtype=np.float32).reshape(1, -1)
    probabilities = session.run([probability_output], {input_name: dummy_features})[0]

    print("Inference test")
    print(f"  Input tensor: {input_name}")
    print(f"  Output tensors: {output_names}")
    print(f"  Dummy probabilities: {probabilities}")
    print("Conversion successful!")


if __name__ == "__main__":
    convert_model()
