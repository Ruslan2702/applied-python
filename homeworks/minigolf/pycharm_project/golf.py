from collections import OrderedDict
from abc import ABCMeta, abstractmethod


class Player:
    def __init__(self, name):
        self._name = str(name)

    @property
    def name(self):
        return self._name


class Match:
    __metaclass__ = ABCMeta

    def __init__(self, H, players_list):
        self._H = H
        self._N = len(players_list)
        self._players_list = players_list
        self._finished = False
        self._current_player = 0
        self._current_hole = 0
        self._number_of_circle = 0
        self._player_to_score_dict = OrderedDict()
        for p in self._players_list:
            self._player_to_score_dict[p.name] = 0
        self._winners_list = []
        self._result_list = [[None for i in range(self._N)] for j in range(H + 1)]
        self._MAX_HITS = 10

    def _convert_none_to_0(self, list_to_convert):
        for j in range(len(list_to_convert)):
            if list_to_convert[j] is None:
                list_to_convert[j] = 0

    @abstractmethod
    def hit(self):   
        pass

    @property
    def finished(self):
        return self._finished

    def get_table(self):
        self._result_table = []
        buf = []
        for player in self._players_list:
            buf.append(player.name)
        self._result_table.append(tuple(buf))

        for i in range(1, self._H + 1):
            self._result_table.append(tuple(self._result_list[i]))

        return self._result_table

    def get_winners(self):
        if not self._finished:
            raise RuntimeError

        max_min_score = self._func_for_get_winners(self._player_to_score_dict.values())
        for key, value in self._player_to_score_dict.items():
            if value == max_min_score:
                for p in self._players_list:
                    if p.name == key:
                        self._winners_list.append(p)
        return self._winners_list

    @abstractmethod
    def _func_for_get_winners(self, args_list):
        pass



class HitsMatch(Match):
    def __init__(self, H, players_list):
        super().__init__(H, players_list)
        self._is_player_scored = [False for i in range(self._N)]
        self._players_score_on_current_hole = [0 for i in range(self. _N)]

    def hit(self, success=False):
        if self._finished:
            raise RuntimeError

        self._players_score_on_current_hole[self._current_player] += 1
        self._player_to_score_dict[self._players_list[self._current_player].name] += 1

        if success:
            self._is_player_scored[self._current_player] = True
            self._result_list[self._current_hole + 1][self._current_player] = \
                self._players_score_on_current_hole[self._current_player]

        self._current_player += 1
        if self._current_player == self._N:
            self._current_player = 0

        while self._is_player_scored[self._current_player] == True:
            self._current_player += 1
            if self._current_player == self._N:
                self._current_player = 0

            self._if_end_of_circle()

        self._if_end_of_circle()

        if self._current_hole == self._H:
            self._finished = True

    def _func_for_get_winners(self, args_list):
        return min(args_list)

    def _if_end_of_circle(self):
        if self._current_player == self._current_hole % self._N:
            self._number_of_circle += 1
            if all(self._is_player_scored) or self._number_of_circle == self._MAX_HITS - 1:
                if self._number_of_circle == self._MAX_HITS - 1:
                    for i in range(len(self._is_player_scored)):
                        if not self._is_player_scored[i]:
                            self._player_to_score_dict[self._players_list[i].name] += 1
                            self._players_score_on_current_hole[i] += 1

                self._result_list[self._current_hole + 1] = self._players_score_on_current_hole
                self._convert_none_to_0(self._result_list[self._current_hole + 1])
                self._current_hole += 1
                self._current_player = self._current_hole % self._N
                self._number_of_circle = 0
                self._is_player_scored = [False for i in range(self._N)]
                self._players_score_on_current_hole = [0 for i in range(self._N)]



class HolesMatch(Match):
    def __init__(self, H, players_list):
        super().__init__(H, players_list)
        self._next_hole = False

    def hit(self, success=False):
        if self._finished:
            raise RuntimeError

        if success:
            player_score = 1
            self._result_list[self._current_hole + 1][self._current_player] = player_score
            self._player_to_score_dict[self._players_list[self._current_player].name] += 1
            self._next_hole = True

        self._current_player += 1

        if self._current_player == len(self._players_list):
            self._current_player = 0

        if self._current_player == self._current_hole % self._N:
            self._number_of_circle += 1
            if self._next_hole or self._number_of_circle == self._MAX_HITS:
                self._convert_none_to_0(self._result_list[self._current_hole + 1])
                self._current_hole += 1
                self._current_player = self._current_hole % self._N
                self._number_of_circle = 0
                self._next_hole = False

        if self._current_hole == self._H:
            self._finished = True

    def _func_for_get_winners(self, args_list):
        return max(args_list)