import utils

def main():
	run_onitama()

def run_onitama():
	import onitama
	from agents import RandomAgent, HumanAgent, BFSAgent, TreeAgent, pawn_heuristic, random_playout_heuristic
	
	env = onitama.OnitamaEnv()
	
	wins = [0, 0]
	
	# R -> 1: 491
	# R -> 2: 727
	# R -> 3: 705
	# R -> 4: 782
	# R -> 5: 920
	# 1 -> 2: 295
	# 2 -> 3: 117
	# 3 -> 4: 165
	
	ec0 = 0
	ec1 = 1
	
	for i in range(0, 1000):
		env.seed(i)
		env.reset()
		agents = [
			#RandomAgent(),
			#BFSAgent(depth = 1, heuristic = random_playout_heuristic(1)),
			BFSAgent(depth = 3, heuristic = pawn_heuristic),
			TreeAgent(expansions = 21, heuristic = pawn_heuristic),
			#HumanAgent()
		]
		
		#print("Seed:", i)
		#print("Agents:", [a.name for a in agents])
		
		for _ in range(100):
			turn = env.state.turn
			action = agents[turn].act(env)
			assert action is not None
			#print("Turn:", turn, action)
			if action is None:
				break
			_, reward, done, _ = env.step(action)
			if done: break
		
		rewards = [0, 0]
		if done:
			rewards[turn] += reward
			wins[turn] += 1
		
		ec0 += agents[0].expansion_count
		ec1 += agents[1].expansion_count
		
		print("Game {:4}, ply {:3}: {}".format(i, env.ply, rewards))
	
	print(ec0, ec1)
	
	for i in range(len(wins)):
		print("Player {}: {:4}".format(i, wins[i]))
	print("Delta Elo: {:.0f}".format(utils.p_to_elo_diff(wins[1] / (wins[0] + wins[1]))))

if __name__ == '__main__':
	main()
