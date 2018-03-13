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
    def __init__(self, suit, face, is_face_down=True):
        """
        Create a poker card
        :param suit: one of Suit enum
        :param face: 1 - 13 inclusive
        """
        self.suit = suit
        self.face = face
        self.face_str = FACES[face]
        self.value = min(face, 10)
        self.face_down = True
        self.is_ace = False
        if not is_face_down:
            self.reveal()

    def hide(self):
        """
        Turn card face down
        :return: 
        """
        if not self.face_down:
            self.face_down = True

    def reveal(self):
        """
        Turn card face up
        :return: 
        """
        if self.face_down:
            self.face_down = False
            self.is_ace = self.face == 1

    def __add__(self, other):
        val = 0 if self.face_down else self.value
        if type(other) == int:
            return val + other
        else:
            return val + other.value

    def __radd__(self, other):
        return self.__add__(other)

    def __str__(self):
        if not self.face_down:
            return '%s %s' % (self.suit.name, self.face_str)
        else:
            return '* *'

    def __repr__(self):
        return self.__str__()


def get_hand_value(cards):
    """
    Calculates possible values of a list of cards
    :param cards: list of cards
    :return: list of int of possible values
    """
    values = [0]

    for card in cards:
        new_values = set()
        for val in values:
            new_values.add(val + card)
            # handle ace
            if card.is_ace:
                new_values.add(val + 11)
        values = list(new_values)

    return list(set(values))


def get_hand_best_value(cards):
    """
    Returns a single int of the best hand value on current cards, i.e. largest < 21
    Returns 99 if all busted
    :param cards: current cards
    :return: int of best hand value
    """
    values = [val for val in get_hand_value(cards) if val <= 21]
    return 99 if len(values) == 0 else max(values)


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
    card0.reveal()
    print("Drew first card: %s" % card0)
    assert len(deck) == ndecks * 52 - 1

    card1 = deck.draw()
    card1.reveal()
    print("Drew second card: %s" % card1)
    assert sum([card0, card1]) == card0.value + card1.value

    deck.shuffle_cards()
    assert len(deck) == ndecks * 52

    # test calculating hand value
    hand = [Card(Suit(1), 1, is_face_down=False),
            Card(Suit(1), 10, is_face_down=False)]
    print(get_hand_value(hand))
    assert sorted(get_hand_value(hand)) == [11, 21]

    hand = [Card(Suit(1), 1, is_face_down=False),
            Card(Suit(1), 10, is_face_down=False),
            Card(Suit(1), 1, is_face_down=False)]
    print(get_hand_value(hand))
    assert sorted(get_hand_value(hand)) == [12, 22, 32]

    hand = [Card(Suit(1), 1, is_face_down=True),
            Card(Suit(1), 10, is_face_down=False),
            Card(Suit(1), 1, is_face_down=False)]
    print(get_hand_value(hand))
    assert sorted(get_hand_value(hand)) == [11, 21]
