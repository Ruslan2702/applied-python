from collections import OrderedDict


class Player:
    def __init__(self, name):
        self._name = str(name)

    @property
    def name(self):
        return self._name


class HitsMatch:
    def __init__(self, H, players_list):
        self._H = H
        self._N = len(players_list)
        self._are_payer_scored_ball = [False for i in range(self._N)]
        # self._start_player = 0
        self._players_list = players_list
        self._finished = False
        self._current_player = 0
        self._current_hole = 0
        self._number_of_circle = 0
        self._num_of_strikes = OrderedDict()
        for p in self._players_list:
            self._num_of_strikes[p.name] = 0
        self._winners_list = []
        self._result_list = [[None for i in range(self._N)] for j in range(H + 1)]
        self._next_hole = False
        self._MAX_HITS = 10

    @property
    def finished(self):
        return self._finished

    def hit(self, success=False):
        if self._finished:
            raise RuntimeError

        # while self._are_payer_scored_ball[self._current_player]:
        #     self._current_player += 1
        #     if self._current_player == len(self._players_list):
        #         self._current_player = 0

        self._num_of_strikes[self._players_list[self._current_player].name] += 1
        if success:
            self._are_payer_scored_ball[self._current_player] = True
            if self._result_list[self._current_hole + 1][self._current_player] is None:
                self._result_list[self._current_hole + 1][self._current_player] = 1
            else:
                self._result_list[self._current_hole + 1][self._current_player] += 1

        self._current_player += 1

        if self._current_player == self._N:
            self._current_player = 0

        if self._current_player == self._current_hole:    # С этого человека начинали
            self._number_of_circle += 1
            if all(flag for flag in self._are_payer_scored_ball) or \
                    self._number_of_circle == self._MAX_HITS - 1:
                if self._number_of_circle == self._MAX_HITS - 1:
                    for i in range(self._N):
                        if not self._are_payer_scored_ball[i]:
                            self._num_of_strikes[self._players_list[i].name] += 1
                            if self._result_list[self._current_hole + 1][i] is None:
                                self._result_list[self._current_hole + 1][i] = 1
                            else:
                                self._result_list[self._current_hole + 1][i] += 1

                self._current_hole += 1
                self._current_player = self._current_hole
                while self._are_payer_scored_ball[self._current_player]:
                    self._current_player += 1

                    if self._current_player == self._N :
                        self._current_player


                self._number_of_circle = 0
                self._are_payer_scored_ball = [False for i in range(len(self._players_list))]

        if self._current_hole == self._H:
            self._finished = True











class HolesMatch:
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
            self._next_hole = True

        self._current_player += 1

        if self._current_player == len(self._players_list):
            self._current_player = 0

        if self._current_player == self._current_hole % len(self._players_list):
            self._number_of_circle += 1
            if self._next_hole or self._number_of_circle == self._MAX_HITS:
                self._convert_none_to_0(self._result_list[self._current_hole + 1])
                self._current_hole += 1
                self._current_player = self._current_hole % len(self._players_list)
                self._number_of_circle = 0
                self._next_hole = False

        if self._current_hole == self._H:
            self._finished = True

    @property
    def finished(self):
        return self._finished

    def get_winners(self):
        if not self._finished:
            raise RuntimeError

        max_score = max(self._player_to_score_dict.values())
        for key, value in self._player_to_score_dict.items():
            if value >= max_score:
                for p in self._players_list:
                    if p.name == key:
                        self._winners_list.append(p)
        return self._winners_list

    def get_table(self):
        self._result_table = []
        buf = []
        for player in self._players_list:
            buf.append(player.name)
        self._result_table.append(tuple(buf))

        for i in range(1, self._H + 1):
            self._result_table.append(tuple(self._result_list[i]))

        return self._result_table

    def _convert_none_to_0(self, list_to_convert):
        for j in range(len(list_to_convert)):
            if list_to_convert[j] is None:
                list_to_convert[j] = 0