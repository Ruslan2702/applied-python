from collections import OrderedDict

class Player:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


# class HitsMatch:
#     def __init__(self, H, players_list):
#         self._H = H
#         self._players_list = players_list
        
#     def hit(self, success = False):
#         if success:
#             pass # Кинуть RuntimeError если матч завершен 

#     @property
#     def finished(self):
#         pass # Проверка, завершен ли матч

#     def get_winners(self):
#         if finished:
#             return self._winners_list
#         raise RuntimeError

#     def get_table(self):
#         pass


class HolesMatch:  # Лунки
    def __init__(self, H, players_list):
        self._H = H
        self._players_list = players_list
        self._finished = False
        self._current_player = 0
        self._current_hole = 0
        self._number_of_circle = 0
        self._player_to_score_dict = OrderedDict()
        for p in self._players_list:
            self._player_to_score_dict[p.name] = 0
        self._winners_list = []
        self._result_list = [[None for i in range(len(players_list))] for j in range(H + 1)]
        self._next_hole = False
        self._MAX_HITS = 10

    def hit(self, success=False):
        if self._finished:
            raise RuntimeError

        if success:
            player_score = 1
            self._result_list[self._current_hole + 1][self._current_player] = player_score
            self._player_to_score_dict[self._players_list[self._current_player].name] += 1
            # self._result_list[self._current_hole + 1][self._current_player] = \
            #     self._player_to_score_dict.get(self._players_list[self._current_player].name, 0)
            self._next_hole = True

        self._current_player += 1
        if self._current_player == len(self._players_list):
            self._current_player = 0
            self._number_of_circle += 1
            if self._next_hole or self._number_of_circle == self._MAX_HITS:
                self._convert_none_to_0(self._result_list[self._current_hole + 1])
                self._current_hole += 1
                self._number_of_circle = 0
                self._next_hole = False

        if self._current_hole == self._H:
            self._finished = True

    @property
    def finished(self):
        return self._finished  # Проверка, завершен ли матч

    def get_winners(self):
        if not self._finished:
            raise RuntimeError

        max_score = -1
        for key, value in self._player_to_score_dict.items():
            if value >= max_score:
                max_score = value
                self._winners_list.append(key)
        return self._winners_list

    def get_table(self):
        self._result_table = []
        buf = []
        for player in self._players_list:
            buf.append(player.name)
        self._result_table.append(tuple(buf))

        for i in range(1, self._H + 1):
            # if self.finished:
            #     self._convert_none_to_0(self._result_list[i])
            self._result_table.append(tuple(self._result_list[i]))

        return self._result_table

    def _convert_none_to_0(self, list_to_convert):
        for j in range(len(list_to_convert)):
            if list_to_convert[j] is None:
                list_to_convert[j] = 0









