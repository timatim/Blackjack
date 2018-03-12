from enum import Enum
import numpy as np


class Suit(Enum):
    SPADE = 1
    HEART = 2
    DIAMOND = 3
    CLOVER = 4


FACES = {1 : 'A',
         2 : '2',
         3 : '3',
         4 : '4',
         5 : '5',
         6 : '6',
         7 : '7',
         8 : '8',
         9 : '9',
         10: '10',
         11: 'J',
         12: 'Q',
         13: 'K'}


class Card(object):
    """
    Representation of a single poker card
    """
    def __init__(self, suit, face):
        """
        Create a poker card
        :param suit: one of Suit enum
        :param face: 1 - 13 inclusive
        """
        self.suit = suit
        self.face = face
        self.face_str = FACES[face]
        self.value = min(face, 10)
        self.ace = (face == 1)
        if self.ace:
            self.value += 10

    def __add__(self, other):
        # TODO: consider Ace
        if type(other) == int:
            return self.value + other
        else:
            return self.value + other.value

    def __radd__(self, other):
        return self.__add__(other)

    def __str__(self):
        return '%s %s' % (self.suit.name, self.face_str)

    def __repr__(self):
        return self.__str__()


class Deck(object):
    """
    Representation of the entire deck of poker cards in the game
    """
    def __init__(self, ndecks=6, shuffle_lim=10):
        """
        :param ndecks: how many decks pokers to use, default to 6
        :param shuffle_lim: trigger shuffle after current turn when this number of cards left
        """
        self.ndecks = ndecks
        self.cards = []
        self.shuffle_cards()
        self.shuffle_lim = shuffle_lim
        self.shuffle_next = False

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def draw(self):
        """
        Draws one card from the deck without replacement
        :return: a Card
        """
        if len(self.cards) < self.shuffle_lim + 1:
            self.shuffle_next = True
        return self.cards.pop()

    def shuffle_cards(self):
        """
        :return: nothing, sets the cards to newly shuffled full set of cards 
        """
        cards = []
        for i in range(self.ndecks):
            for s in Suit:
                for face in range(1, 14):
                    cards.append(Card(s, face))
        np.random.shuffle(cards)
        self.cards = cards

        self.shuffle_next = False

        return None

if __name__ == "__main__":
    print('Testing cards...')
    print('Testing deck...')
    ndecks = 8
    deck = Deck(ndecks)
    print(deck.cards)
    assert len(deck) == ndecks * 52
    card0 = deck.draw()
    print("Drew first card: %s" % card0)
    assert len(deck) == ndecks * 52 - 1

    card1 = deck.draw()
    print("Drew second card: %s" % card1)
    assert sum([card0, card1]) == card0.value + card1.value

    deck.shuffle_cards()
    assert len(deck) == ndecks * 52

    # 85 per suit, 4 suits
    assert sum(deck) == ndecks * 4 * 85