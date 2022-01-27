from dataclasses import dataclass
import random
from wordle_solver.wordle import WordleGame


@dataclass
class RandomSolver:
    wordle_game: WordleGame
    max_trial: int

    def solve(self):
        answer = self.word_choice()
        for _ in range(self.max_trial):
            result = self.wordle_game.check(answer=answer)
            if result.is_solved:
                print(f"{result=}")
                break
            print(f"{result=}")
            answer = self.word_choice()

    def word_choice(self) -> str:
        word = "abcdefghijklnmopqrstuvwxyz"
        word_candidate = [word[random.randint(0, len(word)) - 1] for _ in range(5)]

        # replace
        for k, v in self.wordle_game.get_whole_position_correct().items():
            word_candidate[k] = v
        return "".join(word_candidate)
