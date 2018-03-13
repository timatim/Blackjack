from enum import Enum
from Cards import get_hand_best_value


class Action(Enum):
    Hit = 'h'
    Stand = 's'
    Split = 'sp'
    Double = 'd'


class Player(object):
    def __init__(self, ntokens=100):
        self.hand = [] # list of Cards
        self.tokens = ntokens
        self.bet = 0

    def initialize(self):
        """
        Clear bets and hand for next round
        :return: None
        """
        self.hand = []
        self.bet = 0

    def choose_action(self, valid_actions):
        """
        Player chooses action from list of valid actions
        :param valid_actions: list of actions that are valid
        :return: an action
        """
        while True:
            print("Choose an action:")
            try:
                action = Action(input(', '.join(["'%s' for %s" % (act.value, act.name)
                                                 for act in valid_actions])
                                      + '\n'))
            except ValueError:
                print("Not a valid action.\n")
                continue

            if action not in valid_actions:
                print("Not a valid action.\n")
                continue

            # if double, check if enough tokens
            if action == Action.Double:
                if self.bet > self.tokens:
                    print("Not enough tokens.\n")
                    continue
                else:
                    self.tokens -= self.bet
                    self.bet *= 2
            print("Player chose to %s\n" % action.name)
            break
        return action

    def place_bet(self, min_bet, max_bet):
        """
        Player places bet, returns validated bet
        :param min_bet: minimum bet
        :param max_bet: maximum bet
        :return: player's validated bet
        """
        while True:
            # check int
            try:
                bet = int(input("Player place bet: "))
            except ValueError:
                print("Please enter an integer.")
                continue

            # check remaining
            if bet > self.tokens:
                print("Please enter a bet you can afford.")
                continue

            # check min
            if bet < min_bet:
                print("Please enter a bet greater than the minimum.")
                continue
            # check max
            if bet > max_bet:
                print("Please enter a bet smaller than the maximum.")
                continue

            break

        # deduct bet from token
        self.tokens -= bet
        self.bet = bet
        return bet


class Dealer(object):
    def __init__(self):
        self.hand = []

    def initialize(self):
        """
        Clears hand for next round
        :return: None
        """
        self.hand = []

    def choose_action(self):
        """
        Choose dealer's action according to rule:
        Must draw to at least hard 17
        :return: 
        """
        if get_hand_best_value(self.hand) < 17:
            return Action.Hit
        else:
            return Action.Stand
