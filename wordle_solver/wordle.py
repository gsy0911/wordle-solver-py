from dataclasses import dataclass
from enum import Enum, auto


class Result(Enum):
    WORD_HIT_POSITION_INCORRECT = auto()
    WORD_HIT_POSITION_CORRECT = auto()
    MISSED = auto()


@dataclass(frozen=True)
class Wordle:
    correct_word: str
    word_length: int

    @staticmethod
    def of(correct_word: str) -> "Wordle":
        return Wordle(correct_word=correct_word, word_length=len(correct_word))

    def check(self, answer: str) -> tuple[bool, list[Result]]:
        result = self._check_words(answer=answer)
        return self.correct_word == answer, result

    def _check_words(self, answer: str) -> list[Result]:
        if len(answer) != self.word_length:
            raise ValueError("word length not matched")
        return [self._check_char(idx=idx, s=s) for idx, s in enumerate(answer)]

    def _check_char(self, idx: int, s: str) -> Result:
        if s == self.correct_word[idx]:
            return Result.WORD_HIT_POSITION_CORRECT
        if s in self.correct_word:
            return Result.WORD_HIT_POSITION_INCORRECT
        return Result.MISSED
