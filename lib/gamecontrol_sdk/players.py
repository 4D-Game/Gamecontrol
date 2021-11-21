class Players:
    """
        Class to manage playerdata
    """

    _ready = dict()
    _score = dict()

    @property
    def ready(self):
        """
            Ready state of all players (readonly)
        """

        return self._ready.copy()

    def set_ready(self, seat: int, ready: bool):
        """
            Set ready state for specific player

            Arguments:
                seat: Player Id
                ready: Ready state
        """

        self._ready[seat] = ready

    @property
    def score(self):
        """
            Scores of all player (readonly)
        """

        return self._score.copy()

    def set_score(self, seat: int, score: int):
        """
            Set score of specific player

            Arguments:
                seat: Player ID
                score: Value of the score
        """

        self._score[seat] = score

    def __init__(self, seats: list):
        """
        Arguments:
            seats: List of Player Id's
        """

        for seat in seats:
            self._ready[seat] = False
            self._score[seat] = 0

    def reset_ready(self):
        """
            Reset ready state of all players to `False`
        """

        for key in self._ready.keys():
            self._ready[key] = False

    def reset(self):
        """
            Reset ready state and score of all players to `Fales` e.q. `0`
        """

        for key in self._ready.keys():
            self._ready[key] = False
            self._score[key] = 0
