from dataclasses import dataclass, field
import random
import os
from wordle_solver.wordle import WordleGame


@dataclass
class Solver:
    wordle_game: WordleGame
    max_trial: int
    word_list: list[str] = field(default_factory=list)

    @classmethod
    def of(cls, wordle_game: WordleGame, max_trial: int = 100):
        word_list = Solver._get_word_list()
        return cls(wordle_game=wordle_game, max_trial=max_trial, word_list=word_list)

    def solve(self):
        answer = self._word_choice()
        for _ in range(self.max_trial):
            result = self.wordle_game.check(answer=answer)
            if result.is_solved:
                print(f"{result=}")
                break
            print(f"{result=}")
            answer = self._word_choice()

    def _word_choice(self):
        raise NotImplementedError()

    @staticmethod
    def _get_random_word():
        word = "abcdefghijklnmopqrstuvwxyz"
        word_candidate = [word[random.randint(0, len(word)) - 1] for _ in range(5)]
        return word_candidate

    @staticmethod
    def _get_word_list() -> list[str]:
        with open(f"{os.path.dirname(__file__)}/words_dic.txt", "r") as f:
            word_list = [s.replace("\n", "") for s in f.readlines()]
        return word_list

    @staticmethod
    def _filter_word_list_by_position_correct(word_list: list, position_correct_dict: dict):
        word_list_candidate = []
        for k, v in position_correct_dict.items():
            word_list_candidate.append(set([s for s in word_list if s[k] == v]))
        return list(set.intersection(*word_list_candidate))

    @staticmethod
    def _filter_word_list_by_char_correct(word_list: list, char_correct_list: list):
        word_list_candidate = []
        for v in char_correct_list:
            word_list_candidate.append(set([s for s in word_list if (v in s)]))
        return list(set.intersection(*word_list_candidate))


@dataclass
class RandomSolver(Solver):

    def _word_choice(self) -> str:
        word_candidate = self._get_random_word()

        # replace
        for k, v in self.wordle_game.get_whole_position_correct().items():
            word_candidate[k] = v
        return "".join(word_candidate)


@dataclass
class DictionarySolver(Solver):
    def _word_choice(self) -> str:
        position_correct_dict = self.wordle_game.get_whole_position_correct()
        char_correct_list = self.wordle_game.get_whole_char_correct()
        answers = self.wordle_game.get_answers()

        word_list_candidate = self.word_list
        if char_correct_list:
            word_list_candidate = self._filter_word_list_by_char_correct(
                word_list=word_list_candidate, char_correct_list=char_correct_list)
        if position_correct_dict:
            word_list_candidate = self._filter_word_list_by_position_correct(
                word_list=word_list_candidate, position_correct_dict=position_correct_dict)
        if answers:
            word_list_candidate = [word for word in word_list_candidate if (word not in answers)]

        length = len(word_list_candidate) - 1
        idx = random.randint(0, length)
        return word_list_candidate[idx]
