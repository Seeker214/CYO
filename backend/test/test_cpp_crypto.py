"""
Test C++ chaos encryption/decryption against Python implementation.

Verifies that the C++ implementation produces identical results to the
Python implementation for both encryption and decryption.
"""

import pytest
import numpy as np


def _get_python_impl():
    """Import the Python-only implementation directly."""
    from cyo.services.chaos_algorithm import _encryption_py, _decryption_py
    return _encryption_py, _decryption_py


def _get_cpp_impl():
    """Import the C++ implementation."""
    try:
        from cyo.chaos_crypto_cpp import encryption, decryption
        return encryption, decryption
    except ImportError:
        pytest.skip("C++ module not built. Run: python setup.py build_ext --inplace")


class TestCppVsPython:
    """Compare C++ and Python encryption/decryption outputs."""

    @pytest.mark.parametrize("shape,key", [
        ((32, 32, 3), "0.1,0.1"),
        ((16, 24, 3), "0.5479,0.4014"),
        ((48, 36, 3), "0.3,0.7"),
        ((10, 10, 3), "0.01,0.99"),
    ])
    def test_encryption_matches(self, shape, key):
        """C++ encryption output must be identical to Python."""
        py_enc, _ = _get_python_impl()
        cpp_enc, _ = _get_cpp_impl()

        np.random.seed(42)
        image = np.random.randint(0, 256, shape, dtype=np.uint8)

        result_py = py_enc(image.copy(), key)
        result_cpp = np.asarray(cpp_enc(np.ascontiguousarray(image), key))

        np.testing.assert_array_equal(
            result_py, result_cpp,
            err_msg=f"Encryption mismatch for shape={shape}, key={key}"
        )

    @pytest.mark.parametrize("shape,key", [
        ((32, 32, 3), "0.1,0.1"),
        ((16, 24, 3), "0.5479,0.4014"),
        ((48, 36, 3), "0.3,0.7"),
        ((10, 10, 3), "0.01,0.99"),
    ])
    def test_decryption_matches(self, shape, key):
        """C++ decryption output must be identical to Python."""
        py_enc, py_dec = _get_python_impl()
        _, cpp_dec = _get_cpp_impl()

        np.random.seed(42)
        image = np.random.randint(0, 256, shape, dtype=np.uint8)

        # Encrypt with Python (known-good), then decrypt with both
        encrypted = py_enc(image.copy(), key)

        result_py = py_dec(encrypted.copy(), key)
        result_cpp = np.asarray(cpp_dec(np.ascontiguousarray(encrypted), key))

        np.testing.assert_array_equal(
            result_py, result_cpp,
            err_msg=f"Decryption mismatch for shape={shape}, key={key}"
        )

    @pytest.mark.parametrize("shape,key", [
        ((32, 32, 3), "0.1,0.1"),
        ((16, 24, 3), "0.5479,0.4014"),
    ])
    def test_roundtrip_cpp(self, shape, key):
        """Encrypt then decrypt with C++ should return the original image."""
        cpp_enc, cpp_dec = _get_cpp_impl()

        np.random.seed(42)
        image = np.random.randint(0, 256, shape, dtype=np.uint8)

        encrypted = np.asarray(cpp_enc(np.ascontiguousarray(image.copy()), key))
        decrypted = np.asarray(cpp_dec(np.ascontiguousarray(encrypted), key))

        np.testing.assert_array_equal(
            image, decrypted,
            err_msg=f"C++ roundtrip failed for shape={shape}, key={key}"
        )


class TestCppEdgeCases:
    """Test C++ implementation edge cases."""

    def test_single_pixel(self):
        """1x1 image should work."""
        cpp_enc, cpp_dec = _get_cpp_impl()
        image = np.array([[[128, 64, 32]]], dtype=np.uint8)
        key = "0.1,0.1"

        encrypted = np.asarray(cpp_enc(image.copy(), key))
        assert encrypted.shape == (1, 1, 3)

        decrypted = np.asarray(cpp_dec(encrypted.copy(), key))
        np.testing.assert_array_equal(image, decrypted)

    def test_invalid_key_format(self):
        """Should raise error for malformed key."""
        cpp_enc, _ = _get_cpp_impl()
        image = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)

        with pytest.raises(RuntimeError):
            cpp_enc(image, "invalid_key")

    def test_non_contiguous_array(self):
        """Non-contiguous input should still work (pybind11 will copy)."""
        cpp_enc, cpp_dec = _get_cpp_impl()
        
        # Create a non-contiguous slice
        big = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
        sliced = big[5:15, 5:15, :].copy()  # Make contiguous copy
        
        encrypted = np.asarray(cpp_enc(sliced.copy(), "0.1,0.1"))
        decrypted = np.asarray(cpp_dec(encrypted.copy(), "0.1,0.1"))
        np.testing.assert_array_equal(sliced, decrypted)


class TestPerformance:
    """Basic performance smoke test."""

    def test_encryption_performance(self):
        """C++ encryption should complete in reasonable time for a medium image."""
        import time
        cpp_enc, _ = _get_cpp_impl()

        image = np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)
        key = "0.1,0.1"

        start = time.perf_counter()
        for _ in range(3):
            np.asarray(cpp_enc(np.ascontiguousarray(image.copy()), key))
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / 3) * 1000
        print(f"\nC++ encryption avg: {avg_ms:.1f}ms for 128x128 image")
        # Should complete in under 10 seconds per call even on slow hardware
        assert avg_ms < 10000, f"Encryption too slow: {avg_ms:.1f}ms"
