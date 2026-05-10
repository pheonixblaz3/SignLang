"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from main import app, model_loader, inference_pipeline, word_builder

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_ping_endpoint(self):
        """Test /ping endpoint."""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json()["message"] == "pong 🟢"

    def test_health_endpoint(self):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "camera" in data
        assert "model" in data
        assert "uptime_seconds" in data

    def test_stats_endpoint(self):
        """Test /stats endpoint."""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "fps" in data
        assert "avg_inference_ms" in data
        assert "frame_count" in data
        assert "uptime_seconds" in data
        assert "websocket_connections" in data

    def test_model_info_endpoint(self):
        """Test /model-info endpoint."""
        response = client.get("/model-info")
        assert response.status_code == 200
        data = response.json()
        
        if model_loader and model_loader.model:
            assert "type" in data
            assert "classes" in data


class TestStreamEndpoint:
    """Test stream endpoint."""

    def test_stream_endpoint_exists(self):
        """Test /stream endpoint responds."""
        response = client.get("/stream", timeout=2)
        # Stream endpoint returns 200 with streaming content
        assert response.status_code == 200

    def test_stream_media_type(self):
        """Test stream returns correct media type."""
        response = client.get("/stream", timeout=2)
        assert "multipart/x-mixed-replace" in response.headers.get("content-type", "")


class TestRootEndpoints:
    """Test root endpoints."""

    def test_root_endpoint(self):
        """Test / endpoint."""
        response = client.get("/")
        assert response.status_code == 200

    def test_app_endpoint(self):
        """Test /app endpoint."""
        response = client.get("/app")
        assert response.status_code in [200, 404]  # 404 if file not found


class TestInferencePipelineIntegration:
    """Test inference pipeline integration."""

    def test_pipeline_stats_available(self):
        """Test pipeline stats can be retrieved."""
        stats = inference_pipeline.get_stats()
        assert "frame_count" in stats
        assert "fps" in stats
        assert "current_letter" in stats


class TestWordBuilderIntegration:
    """Test word builder integration."""

    def test_word_builder_stats(self):
        """Test word builder stats."""
        stats = word_builder.get_stats()
        assert "current_word" in stats
        assert "completed_words" in stats
        assert "sentence" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
