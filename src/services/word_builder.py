"""Intelligent word building and sentence assembly."""

from typing import List, Optional
from collections import deque
import time
from src.core.logger import get_logger

logger = get_logger(__name__)


class WordBuilder:
    """
    Build words and sentences with:
    - Character history buffer
    - Automatic word finalization on pause
    - Duplicate letter prevention within word
    - Word validation
    """

    def __init__(self, pause_threshold_sec: float = 2.0, max_word_length: int = 50):
        """
        Initialize word builder.

        Args:
            pause_threshold_sec: Seconds of inactivity to trigger word finalization
            max_word_length: Maximum characters in a word
        """
        self.pause_threshold_sec = pause_threshold_sec
        self.max_word_length = max_word_length

        self.current_word: str = ""
        self.last_letter: Optional[str] = None
        self.last_letter_time: float = time.time()

        self.completed_words: deque = deque(maxlen=100)
        self.history: deque = deque(maxlen=500)

    def add_letter(self, letter: str) -> Optional[str]:
        """
        Add letter to current word.

        Args:
            letter: Letter to add

        Returns:
            Completed word if finalized, None otherwise
        """
        current_time = time.time()

        # Check for pause - finalize previous word if needed
        if self.last_letter_time and (current_time - self.last_letter_time) > self.pause_threshold_sec:
            if self.current_word:
                finished_word = self._finalize_word()
                logger.debug(f"Auto-finalized word on pause: '{finished_word}'")

        # Reject duplicates within word
        if letter == self.last_letter:
            logger.debug(f"Duplicate letter rejected: '{letter}'")
            return None

        # Add letter to word
        if len(self.current_word) < self.max_word_length:
            self.current_word += letter
            self.last_letter = letter
            self.last_letter_time = current_time
            logger.debug(f"Letter added: '{letter}' -> current word: '{self.current_word}'")
            return None
        else:
            logger.warning(f"Word length limit reached: {self.max_word_length}")
            return self._finalize_word()

    def finalize_word(self) -> Optional[str]:
        """Manually finalize current word."""
        if self.current_word:
            return self._finalize_word()
        return None

    def _finalize_word(self) -> Optional[str]:
        """Internal method to finalize word."""
        if not self.current_word:
            return None

        # Validate word
        if self._validate_word(self.current_word):
            self.completed_words.append(self.current_word)
            self.history.append(self.current_word)
            word = self.current_word
            logger.info(f"Word completed: '{word}'")

            # Reset state
            self.current_word = ""
            self.last_letter = None
            self.last_letter_time = time.time()

            return word
        else:
            logger.warning(f"Word validation failed: '{self.current_word}'")
            self.current_word = ""
            self.last_letter = None
            return None

    def _validate_word(self, word: str) -> bool:
        """Validate word before completion."""
        if not word:
            return False

        # Reject all-numbers or all-special chars
        if word.isdigit():
            return False

        # Must have at least one letter
        if not any(c.isalpha() for c in word):
            return False

        return True

    def get_current_word(self) -> str:
        """Get current incomplete word."""
        return self.current_word

    def get_completed_words(self) -> List[str]:
        """Get list of completed words."""
        return list(self.completed_words)

    def get_sentence(self) -> str:
        """Get completed sentence (joined words)."""
        return " ".join(self.get_completed_words())

    def get_history(self) -> List[str]:
        """Get all words in history."""
        return list(self.history)

    def clear(self) -> None:
        """Clear all state."""
        self.current_word = ""
        self.last_letter = None
        self.last_letter_time = time.time()
        self.completed_words.clear()
        self.history.clear()
        logger.info("Word builder cleared")

    def get_stats(self) -> dict:
        """Get statistics."""
        return {
            "current_word": self.current_word,
            "completed_words": len(self.completed_words),
            "total_history": len(self.history),
            "last_letter": self.last_letter,
            "current_sentence": self.get_sentence(),
        }
