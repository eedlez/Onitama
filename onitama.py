import random
import numpy as np
import colorama as col
import gym
from gym.utils import seeding

col.init()

PLAYER_MARK = [1, 2]
MASTER_MARK = 4
MIDDLE = 2
SIZE = 2*MIDDLE + 1
FILE_LETTERS = 'abcde'

class OnitamaEnv(gym.Env):
	def seed(self, seed = None):
		seed = seeding.create_seed(seed)
		self.random = random.Random(seed)
		return [seed]
	
	def reset(self):
		self.ply = 0
#		self.state = State.Start(list(self.random.sample(CARDS, 4)), self.random.randrange(2))
		self.state = State.Start(list(self.random.sample(CARDS, 5)), self.random.randrange(2))
	
	def render(self, mode = 'human', close = False):
		if close: return
		if mode != 'human': return
		for y in range(SIZE - 1, -1, -1):
			print('\t', y, '|' + ''.join(piece_repr(piece) for x, piece in enumerate(self.state.board[y])))
		print('\t', '  ', ' '.join(FILE_LETTERS))
	
	def step(self, action):
		self.state.step_mutate(action)
		done = (self.state.turn is None)
		
		if not done:
			self.ply += 1
		
		reward = (1 if done else 0)
		return self.state, reward, done, None

class State:
	@classmethod
	def Start(cls, cards, turn):
		board = np.zeros((SIZE, SIZE), dtype = np.int8)
		board[0,:] |= PLAYER_MARK[0]
		board[0,MIDDLE] |= MASTER_MARK
		board[-1,:] |= PLAYER_MARK[1]
		board[-1,MIDDLE] |= MASTER_MARK
#		return cls(turn, [cards[:2], cards[2:]], None, board)
		return cls(turn, [cards[:2], cards[2:4]], cards[4], board)
	
	def __init__(self, turn, cards_by_player, card_index_to_swap, board):
		self.turn = turn
		self.cards_by_player = cards_by_player
		self.card_index_to_swap = card_index_to_swap
		self.board = board
	
	def step(self, action):
		s = self.clone()
		s.step_mutate(action)
		return s
	
	def step_mutate(self, action):
		card_index = action[0]
		
		turn = self.turn
		other_turn = 1 - turn
		
		cbp = self.cards_by_player
		card = cbp[turn][card_index]
#		c2s = self.card_index_to_swap
#		if c2s is None:
#			self.card_index_to_swap = card_index
#		else:
#			cbp[turn][card_index] = cbp[other_turn][c2s]
#			cbp[other_turn][c2s] = card
#			self.card_index_to_swap = None
		cbp[turn][card_index] = self.card_index_to_swap
		self.card_index_to_swap = card
		
		done = False
		board = self.board
		
		move_index = action[1]
		if move_index is not None:
			dx, dy = card[turn][move_index]
			x1, y1 = action[2:]
			piece = board[y1,x1]
			board[y1,x1] = 0
			x2 = x1 + dx
			y2 = y1 + dy
			if board[y2,x2] & MASTER_MARK or (piece & MASTER_MARK and x2 == MIDDLE and y2 == (SIZE - 1 if turn == 0 else 0)):
				done = True
			board[y2,x2] = piece
		
		if done:
			self.turn = None
		else:
			self.turn = other_turn
	
	def clone(self):
		return State(self.turn, [list(self.cards_by_player[0]), list(self.cards_by_player[1])], self.card_index_to_swap, np.copy(self.board))
	
	def build_actions(self):
		board = self.board
		turn = self.turn
		cards = self.cards_by_player[turn]
		p = PLAYER_MARK[turn]
		actions = []
		for x1 in range(SIZE):
			for y1 in range(SIZE):
				if not board[y1,x1] & p: continue
				for card_index, card in enumerate(cards):
					for move_index, (dx, dy) in enumerate(card[turn]):
						x2 = x1 + dx
						if not 0 <= x2 < SIZE: continue
						y2 = y1 + dy
						if not 0 <= y2 < SIZE: continue
						if board[y2,x2] & p: continue
						tmp = (card_index, move_index, x1, y1)
						actions.append(tmp)
		if not actions:
			# "Pass" moves
			actions.extend((card_index, None) for card_index, _ in enumerate(cards))
		return actions

def piece_repr(p: int) -> str:
	if p == 0:
		return '_|'
	
	if p & MASTER_MARK:
		c = (col.Back.MAGENTA if p & PLAYER_MARK[0] else col.Back.CYAN)
	else:
		c = (col.Back.RED if p & PLAYER_MARK[0] else col.Back.BLUE)
	return c + ' ' + col.Style.RESET_ALL + '|'

_CARDS = [
	[(0, -1), (0, 2)], # Tiger
	[(0, 1), (-2, 0), (2, 0)], # Crab
	[(-1, -1), (-1, 1), (1, -1), (1, 1)], # Monkey
	[(0, 1), (-1, -1), (1, -1)], # Crane
	[(-1, -1), (1, -1), (-2, 1), (2, 1)], # Dragon
	[(-1, 0), (1, 0), (-1, 1), (1, 1)], # Elephant
	[(0, -1), (-1, 1), (1, 1)], # Mantis
	[(-1, 0), (1, 0), (0, 1)], # Boar
	[(-2, 0), (-1, 1), (1, -1)], # Frog
	[(-1, 0), (-1, 1), (1, 0), (1, -1)], # Goose
	[(-1, 0), (0, 1), (0, -1)], # Horse
	[(-1, 1), (-1, -1), (1, 0)], # Eel
	[(2, 0), (1, 1), (-1, -1)], # Rabbit
	[(1, 0), (1, 1), (-1, 0), (-1, -1)], # Rooster
	[(1, 0), (0, 1), (0, -1)], # Ox
	[(1, 1), (1, -1), (-1, 0)], # Cobra
]
CARDS = [
	[c, [(-dx, -dy) for (dx, dy) in c]]
	for c in _CARDS
]