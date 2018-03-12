from Player import *
from Cards import *
from time import sleep

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

    def draw_cards(self, side): #player_action=Action.Hit, dealer_action=Action.Hit):
        new_card = self.deck.draw()
        if side == 'p':
            self.player.hand.append(new_card)
        elif side == 'd':
            self.dealer.hand.append(new_card)
        # self.dealer.hand.append(self.deck.draw())
        # if player_action == Action.Hit:
        #     self.player.hand.append(self.deck.draw())
        # if dealer_action == Action.Hit:
        #     self.dealer.hand.append(self.deck.draw())

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
        if code == 1:
            print("Congratulations, you got a blackjack!")
            update_tokens = int(self.current_bet * (1 + 1.5))
        # player wins
        elif code == 2:
            print("You won!")
            update_tokens = self.current_bet * 2
        # player loses
        elif code == 3:
            print("You lost!")
            # player token already deducted, do nothing
            update_tokens = 0
        # push
        elif code == 4:
            print("Push!")
            update_tokens = self.current_bet
        # compare hand values
        else:
            raise NotImplementedError
        self.player.tokens += update_tokens

    def condition(self):
        # check player 21, priority before dealer blackjack
        if sum(self.player.hand) == 21:
            # player blackjack, pays 3 to 2
            if self.draw_count == 1:
                return 1
            # win with 21
            else:
                return 2
        # check dealer blackjack
        elif sum(self.dealer.hand) == 21 and self.draw_count == 1:
            print("Dealer got a blackjack!")
            return 3
        # check player bust
        elif sum(self.player.hand) > 21:
            print("You busted!")
            return 3
        # check dealer bust
        elif sum(self.dealer.hand) > 21:
            print("Dealer busted!")
            return 2
        # continue
        else:
            return 0

    def compare_hands(self):
        """
        Compares the hands between dealer and player to decide result
        :return: a result code
        """
        player_sum = sum(self.player.hand)
        dealer_sum = sum(self.dealer.hand)
        if player_sum > dealer_sum:
            return 2
        elif player_sum < dealer_sum:
            return 3
        elif player_sum == dealer_sum:
            return 4
        else:
            raise NotImplementedError

    def round(self):
        self.initialize_round()
        print("Player making bet...")
        self.players_bet()
        # draw two initial cards
        print("Drawing first two cards...")
        self.draw_cards('d')
        self.draw_cards('p')
        self.draw_cards('d')
        self.draw_cards('p')

        self.draw_count += 1

        # test blackjack
        # self.player.hand = [Card(Suit['SPADE'], 1), Card(Suit['SPADE'], 11)]
        print("Dealer hand: %s, %d" % (self.dealer.hand, sum(self.dealer.hand)))
        print("Player hand: %s, %d" % (self.player.hand, sum(self.player.hand)))

        # check for condition
        code = self.condition()

        # TODO: dealer only draws after player's done
        while code == 0:
            # once a STAND, always a STAND
            player_action = self.players_actions()
            if player_action == Action.Stand:
                break

            self.draw_cards('p')

            print("Dealer hand: %s, %d" % (self.dealer.hand, sum(self.dealer.hand)))
            print("Player hand: %s, %d" % (self.player.hand, sum(self.player.hand)))
            code = self.condition()

            # if player doubled
            if player_action == Action.Double:
                # checked if player had enough tokens
                # deducted from player balance
                # add to current bet
                self.current_bet *= 2
                # end player draw (only one draw on doubles)
                break

        # dealer draws if game hasn't ended
        if code == 0:
            # dealer draw
            dealer_action = self.dealer.choose_action()
            code = self.condition()
            while dealer_action == Action.Hit and code == 0:
                self.draw_cards('d')
                print("Dealer hand: %s, %d" % (self.dealer.hand, sum(self.dealer.hand)))
                print("Player hand: %s, %d" % (self.player.hand, sum(self.player.hand)))
                dealer_action = self.dealer.choose_action()
                code = self.condition()
                sleep(1)

        # dealer done drawing but still no result, so compare hands
        if code == 0:
            code = self.compare_hands()

        # game ended
        self.result(code)


if __name__ == "__main__":
    game = Game()
    print(game.player)

    while True:
        print("Player has %d tokens remaining." % game.player.tokens)
        game.round()
