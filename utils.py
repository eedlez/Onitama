import math
import onitama

INF = float('inf')

def compare_agents(a1, a2, n, max_plies = 100):
	agents = [a1, a2]
	env = onitama.OnitamaEnv()
	
	wins = [0, 0]
	
	for i in range(0, n):
		env.seed(i)
		env.reset()
		
		for _ in range(max_plies):
			turn = env.state.turn
			action = agents[turn].act(env)
			assert action is not None
			_, _, done, _ = env.step(action)
			if done: break
		
		if done:
			wins[turn] += 1
	
	d_elo = p_to_elo_diff(wins[1] / (wins[0] + wins[1]))
	return d_elo

def p_to_elo_diff(p1):
	p0 = 1 - p1
	e1_minus_e0 = 400 * (math.log(p1 + 1e-10, 10) - math.log(p0 + 1e-10, 10))
	return e1_minus_e0
