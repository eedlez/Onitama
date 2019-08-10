import heapq
import colorama as col
import numpy as np
import onitama
from utils import INF

class Agent:
	@property
	def name(self):
		raise NotImplementedError('Agent.name')

class BFSAgent(Agent):
	def __init__(self, *, depth, heuristic):
		self.depth = depth
		self.heuristic = heuristic
		self.expansion_count = 0
	
	@property
	def name(self):
		return 'BFSAgent(depth = {}, heuristic = {})'.format(self.depth, self.heuristic.__name__)
	
	def act(self, env):
		return self._minimax(env.state, env, self.depth)[0]
	
	def _minimax(self, state, env, depth):
		next_states = []
		
		self.expansion_count += 1
		for action in state.build_actions():
			s = state.step(action)
			if s.turn is None:
				return action, 1
			value = 1 - self.heuristic(s, env)
			next_states.append((value, action, s))
		
		if len(next_states) > 1:
			next_states = sorted(next_states, reverse = True)[:3]
		
		max_value = -INF
		max_actions = []
		for value, action, s in next_states:
			if depth > 1:
				value = 1 - self._minimax(s, env, depth - 1)[1]
			if value > max_value:
				if value >= 1:
					return action, value
				max_value = value
				max_actions = [action]
			elif value == max_value:
				max_actions.append(action)
		return env.random.choice(max_actions), max_value

class TreeAgent(Agent):
	# Approx. equivalent to BFS (depth, expansions):
	# 1,  1
	# 2,  5
	# 3, 21
	
	def __init__(self, *, expansions, heuristic):
		self.expansions = expansions
		self.heuristic = heuristic
		self.expansion_count = 0
	
	@property
	def name(self):
		return 'TreeAgent(expansions = {}, heuristic = {})'.format(self.expansions, self.heuristic.__name__)
	
	def act(self, env):
		queue = []
		
		self.expansion_count += 1
		state = env.state
		for a in state.build_actions():
			s = state.step(a)
			d = 0
			if s.turn is None:
				v = 1
			else:
				v = self.heuristic(s, env)
				d += 1
			if d%2 != 0: v = 1-v
			heapq.heappush(queue, (-v, a, d, id(s), s))
		
		i = self.expansions - 1
		while i > 0 and queue:
			(_, action, depth, _, state) = heapq.heappop(queue)
			if state.turn is None:
				if depth%2 == 0: return action
				continue
			
			self.expansion_count += 1
			for a in state.build_actions():
				s = state.step(a)
				d = depth
				if s.turn is None:
					v = 1
				else:
					v = self.heuristic(s, env)
					d += 1
				if d%2 != 0: v = 1-v
				heapq.heappush(queue, (-v, action, d, id(s), s))
			i -= 1
		
		return heapq.heappop(queue)[1]

def pawn_heuristic(state, env):
	turn = state.turn
	other_turn = 1 - turn
	board = state.board
	my_pieces = np.count_nonzero(board == onitama.PLAYER_MARK[turn])
	other_pieces = np.count_nonzero(board == onitama.PLAYER_MARK[other_turn])
	return 0.5 + (my_pieces - other_pieces) * 0.1

class random_playout_heuristic:
	def __init__(self, n, depth = 50):
		self.n = n
		self.depth = depth
	
	def __call__(self, state, env):
		n = self.n
		depth = self.depth
		sum = 0
		for _ in range(n):
			s = state.clone()
			for _ in range(depth):
				t = s.turn
				s.step_mutate(env.random.choice(s.build_actions()))
				if s.turn is None:
					sum += (state.turn == t)
					break
		return sum / n

class RandomAgent(Agent):
	@property
	def name(self):
		return 'RandomAgent'
	
	def act(self, env):
		return env.random.choice(env.state.build_actions())

class HumanAgent(Agent):
	def act(self, env):
		print()
		env.render()
		print()
		
		state = env.state
		turn = state.turn
		other_turn = 1 - turn
		
		print(colored_by_turn("Opponent has:", other_turn))
		for card_no in state.cards_by_player[other_turn]:
			print('\t', end = '')
#			if state.card_index_to_swap is not None and state.cards_by_player[state.card_index_to_swap] is card:
#				print("[USED]", end = '')
#			for dx, dy in card[turn]:
			#For Visibility
			card = env.cards[card_no]
			for dx, dy in card[other_turn]:
				print('({: 2},{: 2}) '.format(dx, dy), end = '')
			print()

		print("Card to swap:")
		print('\t', end = '')
		card_to_swap = env.cards[state.card_index_to_swap]
		for dx, dy in card_to_swap[turn]:
			print('({: 2},{: 2}) '.format(dx, dy), end = '')
		print()
		
#		actions = onitama.build_actions(env.state)
		actions = state.build_actions()
		must_pass = (actions[0][1] is None)
		action_mapping = []
		if must_pass:
			print("No moves. Pick card (0/1) to swap.")
		else:
			print(colored_by_turn("My cards:", turn))
			for card_index, card_no in enumerate(state.cards_by_player[turn]):
				print('\t', end = '')
				card = env.cards[card_no]
#				print(card_index,card_no,card)
				for move_index, (dx, dy) in enumerate(card[turn]):
					print('{}:({: 2},{: 2}) '.format(len(action_mapping), dx, dy), end = '')
#					action_mapping.append((card_index, move_index))
					action_mapping.append((card_index, move_index, card_no))
				print()
		
		return self._get_action(must_pass, action_mapping, actions)
	
	def _get_action(self, must_pass, action_mapping, actions):
		while True:
			inp = input("Your move (xy move_id f.e. b0 2): ").strip()
			
			if not inp:
				continue
			
			if inp == 'q':
				action = None
				break
			
			if must_pass:
				try:
					card_index = int(inp)
					action = [a for a in actions if a[0] == card_index][0]
				except:
					continue
				break
			
			if inp[:1] == '!':
				inp = inp[1:]
				import pdb; pdb.set_trace()
			
			try:
				first, second = inp.lower().split(' ')
				x = ord(first[0]) - ord('a')
				y = int(first[1])
#				card_index, move_index = action_mapping[int(second)]
				card_index, move_index, card_no = action_mapping[int(second)]
#				print(card_index, move_index)
			except:
				raise
				#continue
			
#			action = (card_index, move_index, x, y)
			action = (card_no, move_index, x, y)
#			print("action: ", action)
			if action in actions:
#				return a_selected
				return action
			else:
				print("invalid move")

def colored_by_turn(txt, turn):
	c = (col.Fore.MAGENTA if turn == 0 else col.Fore.CYAN)
	return c + col.Style.BRIGHT + txt + col.Style.RESET_ALL
