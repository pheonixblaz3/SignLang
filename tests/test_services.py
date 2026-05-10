"""Unit tests for backend services."""

import pytest
import numpy as np
from src.services.inference import InferencePipeline
from src.services.websocket_manager import WebSocketManager
from src.services.word_builder import WordBuilder


class TestInferencePipeline:
    """Test inference pipeline smoothing and debouncing."""

    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly."""
        pipeline = InferencePipeline(
            frame_buffer_size=5, confidence_threshold=0.4, letter_hold_frames=3
        )
        assert pipeline.frame_buffer_size == 5
        assert pipeline.confidence_threshold == 0.4
        assert pipeline.letter_hold_frames == 3

    def test_confidence_threshold_filtering(self):
        """Test that predictions below threshold are filtered."""
        pipeline = InferencePipeline(confidence_threshold=0.5)
        result = pipeline.process("A", 0.3, 10.0, [("A", 0.3), ("B", 0.2), ("C", 0.1)])

        assert result["letter"] is None
        assert result["state"] == "low_confidence"

    def test_letter_hold_timer(self):
        """Test that letter must be stable for minimum frames."""
        pipeline = InferencePipeline(letter_hold_frames=3, confidence_threshold=0.4)

        # First frame - changing
        result1 = pipeline.process("A", 0.8, 10.0)
        assert result1["letter"] is None
        assert "letter_changing" in result1["state"]

        # Second frame - same letter
        result2 = pipeline.process("A", 0.8, 10.0)
        assert result2["letter"] is None
        assert "holding" in result2["state"]

        # Third frame - still same
        result3 = pipeline.process("A", 0.8, 10.0)
        assert result3["letter"] is None
        assert "holding" in result3["state"]

        # Fourth frame - accepted
        result4 = pipeline.process("A", 0.8, 10.0)
        assert result4["letter"] == "A"
        assert result4["state"] == "accepted"

    def test_duplicate_suppression(self):
        """Test that duplicate letters are suppressed."""
        pipeline = InferencePipeline(
            letter_hold_frames=3, confidence_threshold=0.4, letter_cooldown_ms=200
        )

        # First letter
        for _ in range(4):
            pipeline.process("A", 0.8, 10.0)

        result1 = pipeline.process("A", 0.8, 10.0)
        assert result1["letter"] == "A"
        assert "cooldown" in result1["state"]

    def test_frame_buffer_aggregation(self):
        """Test prediction aggregation from frame buffer."""
        pipeline = InferencePipeline(frame_buffer_size=3, confidence_threshold=0.3)

        # Add different predictions to buffer
        pipeline.process("A", 0.9, 10.0)
        pipeline.process("A", 0.8, 10.0)
        pipeline.process("B", 0.7, 10.0)

        # A should be most common
        aggregated = pipeline._aggregate_predictions()
        assert aggregated["letter"] == "A"

    def test_fps_calculation(self):
        """Test FPS calculation."""
        pipeline = InferencePipeline()

        for i in range(5):
            pipeline.process("A", 0.8, 10.0)

        fps = pipeline._calculate_fps()
        assert fps > 0

    def test_pipeline_reset(self):
        """Test pipeline reset functionality."""
        pipeline = InferencePipeline()
        pipeline.process("A", 0.8, 10.0)
        pipeline.reset()

        assert len(pipeline.prediction_buffer) == 0
        assert len(pipeline.confidence_buffer) == 0
        assert pipeline.current_letter is None


class TestWordBuilder:
    """Test word building and sentence assembly."""

    def test_word_builder_initialization(self):
        """Test word builder initializes correctly."""
        builder = WordBuilder(pause_threshold_sec=2.0, max_word_length=50)
        assert builder.current_word == ""
        assert len(builder.completed_words) == 0

    def test_add_letter(self):
        """Test adding letters to word."""
        builder = WordBuilder()
        builder.add_letter("H")
        builder.add_letter("E")
        builder.add_letter("L")
        builder.add_letter("L")
        builder.add_letter("O")

        assert builder.get_current_word() == "HELLO"

    def test_duplicate_suppression(self):
        """Test duplicate letters are rejected within word."""
        builder = WordBuilder()
        builder.add_letter("A")
        result = builder.add_letter("A")  # Should be rejected

        assert result is None
        assert builder.get_current_word() == "A"

    def test_word_finalization(self):
        """Test word finalization."""
        builder = WordBuilder()
        builder.add_letter("H")
        builder.add_letter("I")

        word = builder.finalize_word()
        assert word == "HI"
        assert builder.get_current_word() == ""

    def test_sentence_building(self):
        """Test sentence assembly from words."""
        builder = WordBuilder()

        # First word
        builder.add_letter("H")
        builder.add_letter("I")
        builder.finalize_word()

        # Second word
        builder.add_letter("Y")
        builder.add_letter("O")
        builder.add_letter("U")
        builder.finalize_word()

        sentence = builder.get_sentence()
        assert sentence == "HI YOU"

    def test_word_validation(self):
        """Test word validation rejects invalid words."""
        builder = WordBuilder()
        builder.add_letter("1")
        builder.add_letter("2")
        builder.add_letter("3")

        # Numbers should be rejected
        assert builder._validate_word("123") is False

    def test_max_word_length(self):
        """Test maximum word length enforcement."""
        builder = WordBuilder(max_word_length=5)
        builder.add_letter("A")
        builder.add_letter("B")
        builder.add_letter("C")
        builder.add_letter("D")
        builder.add_letter("E")

        # Adding sixth letter should finalize word
        result = builder.add_letter("F")
        assert result == "ABCDE" or builder.get_current_word() == "F"

    def test_builder_clear(self):
        """Test clearing word builder state."""
        builder = WordBuilder()
        builder.add_letter("A")
        builder.finalize_word()
        builder.clear()

        assert builder.get_current_word() == ""
        assert len(builder.completed_words) == 0
        assert builder.get_sentence() == ""


class TestWebSocketManager:
    """Test WebSocket connection manager."""

    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test WebSocket manager initializes correctly."""
        manager = WebSocketManager()
        assert manager.get_connection_count() == 0

    @pytest.mark.asyncio
    async def test_connection_count(self):
        """Test connection counting."""
        manager = WebSocketManager()

        # Mock connection object (simplified)
        class MockConnection:
            async def send_json(self, msg):
                pass

            async def close(self):
                pass

        conn1 = MockConnection()
        conn2 = MockConnection()

        await manager.add_connection(conn1)
        assert manager.get_connection_count() == 1

        await manager.add_connection(conn2)
        assert manager.get_connection_count() == 2

        await manager.remove_connection(conn1)
        assert manager.get_connection_count() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
