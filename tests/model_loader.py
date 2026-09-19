from pathlib import Path
import skops.io as sio


def load_skops_model(model_path):
    """Load a model saved in .skops format."""

    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}"
        )

    # Find the types required by the .skops model
    untrusted_types = sio.get_untrusted_types(
        file=model_path
    )

    print("Untrusted types found:")
    for item in untrusted_types:
        print(f"  - {item}")

    # skops requires a list of trusted type names
    model = sio.load(
        file=model_path,
        trusted=list(untrusted_types)
    )

    return model