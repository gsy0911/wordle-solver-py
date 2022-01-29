from collections import OrderedDict
from dataclasses import dataclass, field
from itertools import product
import random
import os

from joblib import Parallel, delayed
import pandas as pd
import numpy as np
from scipy.stats import entropy

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
        word_list = [''.join(OrderedDict.fromkeys(s)) for s in word_list]
        word_list = [s for s in word_list if len(s) == 5]
        return word_list

    @staticmethod
    def _get_word_df(data: list[str]) -> pd.DataFrame:
        df_char = pd.DataFrame([list(key) for key in data], columns=range(1, 6))
        df_char.index = data
        return df_char

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

    @staticmethod
    def _filter_word_list_by_char_missed(word_list: list, char_missed_list: list):
        word_list_candidate = []
        for v in char_missed_list:
            word_list_candidate.append(set([s for s in word_list if (v not in s)]))
        return list(set.intersection(*word_list_candidate))

    def _filtered_word_list(self) -> list[str]:
        position_correct_dict = self.wordle_game.get_whole_position_correct()
        char_correct_list = self.wordle_game.get_whole_char_correct()
        char_missed_list = self.wordle_game.get_whole_char_missed()
        answers = self.wordle_game.get_answers()

        word_list_candidate = self.word_list
        if char_correct_list:
            word_list_candidate = self._filter_word_list_by_char_correct(
                word_list=word_list_candidate, char_correct_list=char_correct_list)
        if char_missed_list:
            word_list_candidate = self._filter_word_list_by_char_missed(
                word_list=word_list_candidate, char_missed_list=char_missed_list)
        if position_correct_dict:
            word_list_candidate = self._filter_word_list_by_position_correct(
                word_list=word_list_candidate, position_correct_dict=position_correct_dict)
        if answers:
            word_list_candidate = [word for word in word_list_candidate if (word not in answers)]
        return word_list_candidate


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
        word_list_candidate = self._filtered_word_list()

        length = len(word_list_candidate) - 1
        idx = random.randint(0, length)
        return word_list_candidate[idx]


@dataclass
class EntropySolver(Solver):
    """
    See Also: https://qiita.com/Ken-ichi_Hironaka/items/dbcf3f4d3c702fb62ec6
    """

    def _word_choice(self) -> str:
        word_list_candidate = self._filtered_word_list()

        if len(word_list_candidate) == len(self.word_list):
            # initial hand
            return "raise"
        df_char = self._get_word_df(data=word_list_candidate)
        df_entropy = self._order_by_entropy(df_char)

        return df_entropy.iloc[0]["word"]

    @staticmethod
    def _calc_cluster_entropy(df_char: pd.DataFrame, input_word: str):
        cluster_size = np.zeros(np.repeat(3, 5))
        green = pd.DataFrame()
        yellow = pd.DataFrame()
        gray = pd.DataFrame()

        for pos, char in enumerate(list(input_word)):
            green[pos] = (df_char[pos + 1] == char)
            yellow[pos] = (~green[pos]) & (df_char.index.str.contains(char))
            gray[pos] = (~yellow[pos]) & (~green[pos])

        responses = [gray, yellow, green]
        for idx in product(range(3), range(3), range(3), range(3), range(3)):
            tfs = [responses[res][pos] for pos, res in enumerate(idx)]
            cluster_size[idx] = (tfs[0] & tfs[1] & tfs[2] & tfs[3] & tfs[4]).sum()

        cluster_size = np.int64(cluster_size.ravel())
        return entropy(cluster_size, base=2)

    @staticmethod
    def _order_by_entropy(df_temp: pd.DataFrame):
        data = Parallel(n_jobs=-1)(
            delayed(EntropySolver._calc_cluster_entropy)(df_temp, index) for index in df_temp.index)
        df_entropy = pd.DataFrame(data, index=df_temp.index, columns=["entropy"])
        df_entropy.sort_values("entropy", ascending=False, inplace=True)
        df_entropy["word"] = df_entropy.index
        return df_entropy
