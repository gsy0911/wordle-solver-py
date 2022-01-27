from dataclasses import dataclass
from enum import Enum


class Color:
    BLACK = '\033[30m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'


class Result(Enum):
    MISSED = (0, Color.BLACK)
    WORD_HIT_POSITION_INCORRECT = (1, Color.YELLOW)
    WORD_HIT_POSITION_CORRECT = (2, Color.GREEN)

    def __init__(self, id_: str, color: Color):
        self.id_ = id_
        self.color = color

    def __repr__(self):
        return f"{self.color}■{Color.RESET}"

    __str__ = __repr__


@dataclass(frozen=True)
class WordleAnswerResult:
    answer: str
    trial: int
    is_solved: bool
    result: list[Result]

    def get_position_correct(self) -> dict[int, str]:
        return {
            idx: z[1] for idx, z in enumerate(zip(self.result, self.answer)) if z[0] == Result.WORD_HIT_POSITION_CORRECT
        }

    def get_char_correct(self) -> list[str]:
        return [s for r, s in zip(self.result, self.answer) if r == Result.WORD_HIT_POSITION_INCORRECT]

    def __repr__(self):
        wordle_display = " ".join([r.__str__() for r in self.result])
        return f"{wordle_display}: {self.answer}"


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

    def get_whole_position_correct(self):
        whole = {}
        for r in self.wordle_answer_result_list:
            whole.update(r.get_position_correct())
        return whole

    def get_whole_char_correct(self) -> list[str]:
        whole = []
        for r in self.wordle_answer_result_list:
            whole.extend(r.get_char_correct())
        return whole
