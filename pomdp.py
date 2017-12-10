import itertools, random, sys
import matplotlib.pyplot as plt
from termcolor import colored

epsilon = 0.2

def indexOf(iter, item):
	for i in range(len(iter)):
		if item == iter[i]:
			return i
	return -1

def generateStates():
	#state: length of stack A, index of skull in stack A, length of stack B, index of skull in stack B, bet, gameover
	stacks = [[]]
	for i in range(1, 5):
		if i < 4:
			stacks.append(['flower'] * i)
		for j in range(0, i):
			stack = ['flower'] * i
			stack[j] = 'skull'
			stacks.append(stack)
	states = []
	for stack in stacks:
		if len(stack) == 0:
			states.append((0, -1, 0, -1, 0, 0))
		else:
			others = []
			for j in range(max(len(stack) - 1, 1), len(stack) + 1):
				if j < 4:
					others.append(['flower'] * j)
				for k in range(0, j):
					other = ['flower'] * j
					other[k] = 'skull'
					others.append(other)
			for other in others:
				if len(other) == len(stack):
					for bet in range(0, len(stack) + len(other) + 1):
						if bet % 2 == 0:
							states.append((len(stack), indexOf(stack, 'skull'), len(other), indexOf(other, 'skull'), bet, 0))
						if bet > 0:
							states.append((len(stack), indexOf(stack, 'skull'), len(other), indexOf(other, 'skull'), bet, 1))
				else:
					for bet in range(1, len(stack) + len(other) + 1):
						if bet % 2 != 0:
							states.append((len(stack), indexOf(stack, 'skull'), len(other), indexOf(other, 'skull'), bet, 0))
						if bet > 0:
							states.append((len(stack), indexOf(stack, 'skull'), len(other), indexOf(other, 'skull'), bet, 1))
	return states

def generateBeliefDistribution(states):
	b_dists = []
	for state in states:
		b_dist = []
		for state_possible in states:
			if state[:3] == state_possible[:3] and state[4:] == state_possible[4:]:
				b_dist.append(1.0)
			else:
				b_dist.append(0.0)
		sum_b = float(sum(b_dist))
		b_dist = tuple([x / sum_b for x in b_dist])
		b_dists.append(b_dist)
	b_dists = set(b_dists)
	return list(b_dists)

def transitions(state, action, states):
	stackALen, stackASkull, stackBLen, stackBSkull, bet, gameover = state
	if gameover == 1:
		return 'pass', {state: 1.0}
	stackA = ['flower'] * stackALen
	if stackASkull >= 0:
		stackA[stackASkull] = 'skull'
	stackB = ['flower'] * stackBLen
	if stackBSkull >= 0:
		stackB[stackBSkull] = 'skull'
	probs = {}
	while True:
		if action == 'addSkull' or action == 'addFlower':
			if bet > 0 or len(stackA) == 4:
				# If it isn't possible to add a tile, force the bet action
				action = 'bet'
			else:
				newStackA = []
				if action == 'addSkull':
					if 'skull' in stackA:
						# If we already added our skull, we're forced to add a flower instead
						action = 'addFlower'
						continue
					else:
						newStackA = ['skull'] + stackA
				else:
					if 'skull' not in stackA and len(stackA) == 3:
						# If we ran out of flower tiles, we're forced to add a skull instead
						action = 'addSkull'
						continue
					else:
						newStackA = ['flower'] + stackA
				if len(stackB) == 0:
					# If the opponent's stack is empty, 50% chance of adding a flower or skull
					probs[(len(newStackA), indexOf(newStackA, 'skull'), len(['skull'] + stackB), 0, 0, 0)] = 0.5
					probs[(len(newStackA), indexOf(newStackA, 'skull'), len(['flower'] + stackB), indexOf(stackB, 'skull'), 0, 0)] = 0.5
				elif stackB[0] == 'skull':
					# If the opponent's skull is on top of their stack, 20% chance of starting a bet and 80% chance of adding a flower
					probs[(len(newStackA), indexOf(newStackA, 'skull'), len(stackB), 0, 1, 0)] = 0.2
					probs[(len(newStackA), indexOf(newStackA, 'skull'), len(['flower'] + stackB), 1, 0, 0)] = 0.8
				else:
					if 'skull' in stackB:
						# If the opponent's skull is in their stack, 50% chance of starting a bet and 50% chance of adding a flower
						probs[(len(newStackA), indexOf(newStackA, 'skull'), len(stackB), indexOf(stackB, 'skull'), 1, 0)] = 0.5
						probs[(len(newStackA), indexOf(newStackA, 'skull'), len(['flower'] + stackB), indexOf(stackB, 'skull')+1, 0, 0)] = 0.5
					elif len(stackB) == 3:
						# If the opponent has placed 3 flowers, 50% chance of starting a bet and 50% chance of adding their skull
						probs[(len(newStackA), indexOf(newStackA, 'skull'), len(stackB), -1, 1, 0)] = 0.5
						probs[(len(newStackA), indexOf(newStackA, 'skull'), len(['skull'] + stackB), 0, 0, 0)] = 0.5
					else:
						# If the opponent can add either a skull or a flower, 34% chance of starting a bet and 33% chance of adding a skull or flower
						probs[(len(newStackA), indexOf(newStackA, 'skull'), len(stackB), -1, 1, 0)] = 0.34
						probs[(len(newStackA), indexOf(newStackA, 'skull'), len(['skull'] + stackB), 0, 0, 0)] = 0.33
						probs[(len(newStackA), indexOf(newStackA, 'skull'), len(['flower'] + stackB), -1, 0, 0)] = 0.33
				return action, probs
		elif action == 'bet':
			if len(stackA) < 1 or len(stackB) < 1:
				# If we haven't both placed at least one tile, force us to add a flower
				action = 'addFlower'
			elif bet == len(stackA) + len(stackB):
				# If the bet is already equal to the number of tiles on the table, force us to pass
				action = 'pass'
			elif bet % 2 != len(stackA) - len(stackB):
				# If we made the last bet, then the opponent passed and we must pass too
				action = 'pass'
			else:
				if bet + 1 >= len(stackA) + len(stackB) or (len(stackA) == 4 and bet + 1 >= 4):
					# If it's impossible to make the bet or we have all our tiles out and the bet is at least 4, the opponent passes 100%
					probs[(len(stackA), indexOf(stackA, 'skull'), len(stackB), indexOf(stackB, 'skull'), bet + 1, 1)] = 1.0
				elif 'skull' in stackB and bet + 1 >= indexOf(stackB, 'skull'):
					# The opponent bluffs 20% and passes 80% when it knows it can't make the bet
					probs[(len(stackA), indexOf(stackA, 'skull'), len(stackB), indexOf(stackB, 'skull'), bet + 1, 1)] = 0.8
					probs[(len(stackA), indexOf(stackA, 'skull'), len(stackB), indexOf(stackB, 'skull'), bet + 2, 0)] = 0.2
				else:
					# The opponent passes 20% and makes a bet 80%
					probs[(len(stackA), indexOf(stackA, 'skull'), len(stackB), indexOf(stackB, 'skull'), bet + 1, 1)] = 0.2
					probs[(len(stackA), indexOf(stackA, 'skull'), len(stackB), indexOf(stackB, 'skull'), bet + 2, 0)] = 0.8
				return action, probs

		elif action == 'pass':
			if bet == 0:
				# If we can't pass because the betting hasn't started, force us to add a flower
				action = 'addFlower'
			else:
				# Game over
				probs[(len(stackA), indexOf(stackA, 'skull'), len(stackB), indexOf(stackB, 'skull'), bet, 1)] = 1.0
				return action, probs

def reward(state, action, nextState):
	stackALen, stackASkull, stackBLen, stackBSkull, bet, gameover = state
	_, _, _, _, nextBet, nextGameover = nextState
	stackA = ['flower'] * stackALen
	if stackASkull >= 0:
		stackA[stackASkull] = 'skull'
	stackB = ['flower'] * stackBLen
	if stackBSkull >= 0:
		stackB[stackBSkull] = 'skull'
	reward = 0
	if action == 'bet':
		if 'skull' in stackA and bet >= stackA.index('skull'):
			if nextBet > bet + 1:
				reward = 1
			#reward = 0
	if nextGameover == 1:
		if nextBet % 2 == len(stackA) - len(stackB):
			if 'skull' in stackB and nextBet > stackB.index('skull'):
				reward = 1
			elif 'skull' in stackA and nextBet > len(stackB) + stackA.index('skull'):
				reward = 1
			else:
				reward = -1
		else:
			if 'skull' in stackA and nextBet > stackA.index('skull'):
				reward = -1
			elif 'skull' in stackB and nextBet > len(stackA) + stackB.index('skull'):
				reward = -1
			else:
				reward = 1
	return reward

def policyIteration(belief_dists, states, actions, discount):
	policy = {belief_dist: (random.choice(range(len(actions))), -1) for belief_dist in belief_dists}
	V = {belief_dist: 0 for belief_dist in belief_dists}
	n = 0
	while True:
		V = updateV(V, policy, states, belief_dists, actions, discount)
		policyChanged, policy = updatePolicy(V, policy, states, belief_dists, actions)
		n += 1
		print "Finished %d iterations, %d updates" % (n, policyChanged)
		if policyChanged == 0:
			return policy, V, n

def beliefFromState(state, states):
	belief_dist = []
	for state_poss in states:
		if state[:3] == state_poss[:3] and state[4:] == state_poss[4:]:
			belief_dist.append(1.0)
		else:
			belief_dist.append(0.0)
	sum_b = float(sum(belief_dist))
	belief_dist = [x / sum_b for x in belief_dist]
	return tuple(belief_dist)

def updateV(V, policy, states, belief_dists, actions, discount):
	newV = {belief_dist: 0 for belief_dist in belief_dists}
	for i in range(len(belief_dists)):
		belief_dist = belief_dists[i]
		action = actions[policy[belief_dist][0]]
		chance = random.random()
		if chance < epsilon:
			action = random.choice(actions)
		value = 0
		for j in range(len(belief_dist)):
			if belief_dist[j] > 0.0:
				state = states[j]
				action, probs = transitions(state, action, states)
				for nextState in probs:
					value += belief_dist[j] * probs[nextState] * reward(state, action, nextState)
					value += belief_dist[j] * discount * probs[nextState] * V[beliefFromState(nextState, states)]
		newV[belief_dist] = value
	return newV

def updatePolicy(V, policy, states, belief_dists, actions):
	policyChanged = 0
	newPolicy = {belief_dist: 0 for belief_dist in belief_dists}
	for i in range(len(belief_dists)):
		belief_dist = belief_dists[i]
		rewards = [-1*sys.maxint-1] * len(actions)
		for action in actions:
			value = 0
			for j in range(len(belief_dist)):
				if belief_dist[j] > 0.0:
					state = states[j]
					realAction, probs = transitions(state, action, states)
					for nextState in probs:
						value += belief_dist[j] * probs[nextState] * V[beliefFromState(nextState, states)]
			rewards[actions.index(realAction)] = value
		bestAction = rewards.index(max(rewards))
		rewards[bestAction] = -1*sys.maxint-1
		runner_up = rewards.index(max(rewards))
		if rewards[runner_up] == -1*sys.maxint-1:
			runner_up = -1
		if bestAction != policy[belief_dist][0]:
			policyChanged += 1
		newPolicy[belief_dist] = (bestAction, runner_up)
		#print ""
	return policyChanged, newPolicy

def calculateBluffRatio(policy, V, actions, belief_dists, states):
	return sum([detectBluff(belief_dist, V, policy[belief_dist][0], actions, states) for belief_dist in belief_dists]) / float(sum([possibleToBluff(b_dist, actions, states) for b_dist in belief_dists]))

def possibleToBluff(b_dist, actions, states):
	state = ()
	for i in range(len(b_dist)):
		if b_dist[i] > 0.0:
			state = states[i]
	if state[5] == 1:
		return 0
	stackALen, stackASkull, _, _, bet, _ = state
	if bet + 1 <= stackASkull:
		return 0
	realAction, probs = transitions(state, 'bet', states)
	if realAction != 'bet':
		return 0
	return 1

def detectBluff(belief_dist, V, action, actions, states):
	state = ()
	for i in range(len(belief_dist)):
		if belief_dist[i] > 0.0:
			state = states[i]
	if state[5] == 1:
		return 0
	stackALen, stackASkull, stackBLen, stackBSkull, bet, _ = state
	state = list(state)
	state[3] = '?'
	stackA = ['flower'] * stackALen
	if stackASkull >= 0:
		stackA[stackASkull] = 'skull'
	if actions[action] == 'bet':
		if 'skull' in stackA and bet >= stackA.index('skull'):
			print state, actions[action], V[belief_dist], colored("BLUFF", 'red')
			return 1
	print state, actions[action], V[belief_dist]
	return 0

def savePolicy(policy, states, actions):
	with open('policy.txt', 'w') as file:
		for b_dist in policy:
			state = ()
			for i in range(len(b_dist)):
				if b_dist[i] > 0.0:
					state = states[i]
			state = list(state)
			state[3] = '?'
			state = tuple(state)
			best_action = policy[b_dist][0]
			runner_up = policy[b_dist][1]
			if runner_up == -1:
				runner_up = best_action
			file.write(str(state) + ': ' + actions[best_action] + ',' + actions[runner_up] + '\n')

def main():
	states = generateStates()
	belief_dists = generateBeliefDistribution(states)
	actions = ['addSkull', 'addFlower', 'bet', 'pass']
	discount = 0.9
	policy, V, n = policyIteration(belief_dists, states, actions, discount)
	print "Policy iteration converged after %d iterations" % n
	print "Best policy is to bluff %d%% of the time" % (100 * calculateBluffRatio(policy, V, actions, belief_dists, states))
	print "There are %d possible belief distributions" % len(belief_dists)
	savePolicy(policy, states, actions)

if __name__ == '__main__':
	main()