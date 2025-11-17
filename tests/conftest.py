import sys
import types
from types import SimpleNamespace

import pytest
from tests.fixtures_data import ALL_FIXTURES


def _ensure_torch_stub() -> None:
    if "torch" in sys.modules:
        return
    fake_torch = types.ModuleType("torch")
    setattr(fake_torch, "cuda", SimpleNamespace(is_available=lambda: False))
    sys.modules["torch"] = fake_torch


def _ensure_transformers_stub() -> None:
    if "transformers" in sys.modules:
        return

    class _MissingDependency:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):  # pragma: no cover
            raise RuntimeError("transformers not installed; tests provide stubs")

    fake_transformers = types.ModuleType("transformers")
    setattr(fake_transformers, "DonutProcessor", _MissingDependency)
    setattr(fake_transformers, "VisionEncoderDecoderModel", _MissingDependency)
    sys.modules["transformers"] = fake_transformers


def _ensure_pillow_stub() -> None:
    if "PIL" in sys.modules:
        return

    pil_pkg = types.ModuleType("PIL")
    image_module = types.ModuleType("PIL.Image")

    def _open(path):  # pragma: no cover
        raise RuntimeError("Pillow not installed; tests stub Image.open")

    setattr(image_module, "open", _open)
    setattr(pil_pkg, "Image", image_module)
    sys.modules["PIL"] = pil_pkg
    sys.modules["PIL.Image"] = image_module


_ensure_torch_stub()
_ensure_transformers_stub()
_ensure_pillow_stub()


@pytest.fixture(scope="session")
def fixtures():
    return ALL_FIXTURES
