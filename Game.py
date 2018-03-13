from Player import *
from Cards import *
from time import sleep


class Condition(Enum):
    CONTINUE = 0
    BLACKJACK = 1
    WIN = 2
    LOSE = 3
    PUSH = 4


class Game(object):
    def __init__(self, num_player=1, player_tokens=1000,
                 ndecks=6, shuffle_lim=10):
        # self.players = [Player.Player(ntokens=player_tokens) for _ in range(num_player)]
        self.player = Player(ntokens=player_tokens)
        self.dealer = Dealer()
        self.draw_count = 0  # keeps track of number of draws - first two counts as one
        self.min_bet = 10
        self.max_bet = 500
        self.current_bet = 0
        self.deck = Deck(ndecks, shuffle_lim)

    def initialize_round(self):
        # for p in self.players:
        #     p.initialize()
        self.player.initialize()
        # clear dealer hand
        self.dealer.initialize()
        # clear draw count
        self.draw_count = 0

    def players_bet(self):
        self.current_bet = self.player.place_bet(min_bet=self.min_bet, max_bet=self.max_bet)

    def draw_cards(self, side, face_down=True):
        new_card = self.deck.draw()

        if not face_down:
            new_card.reveal()

        if side == 'p':
            self.player.hand.append(new_card)
        elif side == 'd':
            self.dealer.hand.append(new_card)

    def players_actions(self):
        """
        Get player action from player
        :return: 
        """
        # compile list of valid actions for player
        # hit and stand are always valid
        valid_actions = [Action.Hit, Action.Stand]

        # split and double only occurs in draw one
        if self.draw_count == 1:
            valid_actions.append(Action.Double)
            if len(self.player.hand) == 2 and self.player.hand[0].value == self.player.hand[1].value:
                valid_actions.append(Action.Split)

        action = self.player.choose_action(valid_actions)

        return action

    def result(self, code):
        # player blackjack, pays 3 to 2
        if code == Condition.BLACKJACK:
            print("Congratulations, you got a blackjack!")
            update_tokens = int(self.current_bet * (1 + 1.5))
        # player wins
        elif code == Condition.WIN:
            print("You won!")
            update_tokens = self.current_bet * 2
        # player loses
        elif code == Condition.LOSE:
            print("You lost!")
            # player token already deducted, do nothing
            update_tokens = 0
        # push
        elif code == Condition.PUSH:
            print("Push!")
            update_tokens = self.current_bet
        # compare hand values
        else:
            raise NotImplementedError
        self.player.tokens += update_tokens

    def condition(self):
        """
        Check the current condition and returns a condition code
        :return: condition code
        """
        # check blackjack
        if get_hand_best_value(self.player.hand) == 21:
            # player blackjack, pays 3 to 2
            if self.draw_count == 1:
                # check if dealer also blackjack
                return Condition.PUSH if get_hand_best_value(self.dealer.hand) == 21 else Condition.BLACKJACK
        # check dealer blackjack
        elif get_hand_best_value(self.dealer.hand) == 21 and self.draw_count == 1:
            print("Dealer got a blackjack!")
            return Condition.LOSE
        # check player bust
        elif get_hand_best_value(self.player.hand) > 21:
            print("You busted!")
            return Condition.LOSE
        # check dealer bust
        elif get_hand_best_value(self.dealer.hand) > 21:
            print("Dealer busted!")
            return Condition.WIN
        # continue
        else:
            return Condition.CONTINUE

    def compare_hands(self):
        """
        Compares the hands between dealer and player to decide result
        :return: a result code
        """
        # take max <= 21
        player_best = get_hand_best_value(self.player.hand)
        dealer_best = get_hand_best_value(self.dealer.hand)

        # check blackjack
        if player_best == 21 and dealer_best != 21 and self.draw_count == 1:
            return Condition.BLACKJACK
        # check dealer bust
        if dealer_best > 21:
            return Condition.WIN
        if player_best > dealer_best:
            return Condition.WIN
        elif player_best < dealer_best:
            return Condition.LOSE
        elif player_best == dealer_best:
            return Condition.PUSH
        else:
            raise NotImplementedError

    def display_hands(self):
        # only print values <= 21, print minimum if no values <= 21
        dealer_values = get_hand_value(self.dealer.hand)
        dealer_print = sorted([val for val in dealer_values if val <= 21])
        if len(dealer_print) == 0:
            dealer_print = [min(dealer_values)]

        player_values = get_hand_value(self.player.hand)
        player_print = sorted([val for val in player_values if val <= 21])
        if len(player_print) == 0:
            player_print = [min(player_values)]

        print("Dealer hand: %s, %s" %
              (self.dealer.hand, dealer_print))
        print("Player hand: %s, %s" %
              (self.player.hand, player_print))
        print()
        sleep(0.5)

    def round(self):
        self.initialize_round()
        print("Player making bet...")
        self.players_bet()
        # draw two initial cards
        print("Drawing first two cards...")
        self.draw_cards('d', face_down=False)
        self.draw_cards('p', face_down=False)
        self.draw_cards('d', face_down=True)
        self.draw_cards('p', face_down=False)

        self.draw_count += 1

        # self.player.hand = [Card(Suit['SPADE'], 1), Card(Suit['SPADE'], 11)]
        self.display_hands()

        # check for condition
        code = self.condition()

        # player draws until 21 or stand or double or busted
        while True:
            # drew to 21
            if get_hand_best_value(self.player.hand) == 21:
                break
            # busted, reveal dealer card and end round
            if get_hand_best_value(self.player.hand) > 21:
                code = Condition.LOSE
                # reveal dealer's cards
                for card in self.dealer.hand:
                    card.reveal()
                self.display_hands()
                self.result(code)
                return

            player_action = self.players_actions()

            # player stand, end player drawing phase
            if player_action == Action.Stand:
                break

            if player_action == Action.Split:
                # TODO: split logic
                pass

            self.draw_cards('p', face_down=False)
            self.draw_count += 1
            self.display_hands()
            code = self.condition()

            # if player doubled
            if player_action == Action.Double:
                # checked if player had enough tokens
                # deducted from player balance
                # add to current bet
                self.current_bet *= 2
                # end player draw (only one draw on doubles)
                break

        # reveal dealer's cards
        for card in self.dealer.hand:
            card.reveal()
        self.display_hands()

        # dealer draws until >= 17
        while True:
            dealer_action = self.dealer.choose_action()
            if dealer_action == Action.Stand:
                break
            self.draw_cards('d', face_down=False)
            self.display_hands()

        # dealer done drawing but still no result, so compare hands
        code = self.compare_hands()

        # game ended
        self.result(code)


if __name__ == "__main__":
    game = Game()
    print(game.player)

    while True:
        if game.player.tokens < game.min_bet:
            print("You're broke.")
            break
        print("Player has %d tokens remaining." % game.player.tokens)
        game.round()
