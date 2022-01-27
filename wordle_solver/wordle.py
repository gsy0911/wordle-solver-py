from dataclasses import dataclass, field
from enum import Enum, auto


class Result(Enum):
    WORD_HIT_POSITION_INCORRECT = auto()
    WORD_HIT_POSITION_CORRECT = auto()
    MISSED = auto()


@dataclass(frozen=True)
class WordleAnswerResult:
    answer: str
    trial: int
    is_solved: bool
    result: list[Result]


@dataclass(frozen=True)
class Wordle:
    correct_word: str
    word_length: int

    @staticmethod
    def of(correct_word: str) -> "Wordle":
        return Wordle(correct_word=correct_word, word_length=len(correct_word))

    def check(self, answer: str, trial: int = 1) -> WordleAnswerResult:
        result = self._check_words(answer=answer)
        return WordleAnswerResult(answer=answer, trial=trial, is_solved=self.correct_word == answer, result=result)

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


@dataclass(frozen=True)
class WordleGame:
    wordle: Wordle
    wordle_answer_result_list: list[WordleAnswerResult]

    @staticmethod
    def of(correct_word: str) -> "WordleGame":
        return WordleGame(wordle=Wordle.of(correct_word=correct_word), wordle_answer_result_list=[])

    def check(self, answer: str):
        wordle_result = self.wordle.check(answer=answer, trial=len(self.wordle_answer_result_list) + 1)
        self.wordle_answer_result_list.append(wordle_result)
        return wordle_result
