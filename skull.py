import random

epsilon = 0.3

def setup():
	decks = [['skull', 'flower', 'flower', 'flower'], ['skull', 'flower', 'flower', 'flower']]
	return decks

def readPolicy():
	policy = {}
	with open('policy.txt', 'r') as file:
		for line in file:
			state = [int(x) for x in line.split(':')[0][1:-1].split(', ') if x != "'?'"]
			state = tuple(state[:3] + ['?'] + state[3:])
			action = line.split(':')[1][1:].rstrip().split(',')
			policy[state] = tuple(action)
	return policy

def play(decks, policy):
	actions = ['addFlower', 'addSkull', 'bet', 'pass']
	stacks = [[], []]
	state = [0, -1, 0, -1, 0, 0]
	passed = False
	print "RL player 0, human player 1"
	print "RL player goes first"
	correct = 0
	false_pos = 0
	false_neg = 0
	while passed == False:
		for i in range(2):
			if i == 0:
				action = policy[tuple(state[:3] + ['?'] + state[4:])]
				chance = random.random()
				if chance >= epsilon:
					action = action[0]
				else:
					action = action[1]
				if action == 'addFlower':
					stacks[0].insert(0, decks[0].pop(decks[0].index('flower')))
					state[0] += 1
					if state[1] > -1:
						state[1] = stacks[0].index('skull')
					print "RL player added a tile to their stack"
				elif action == 'addSkull':
					stacks[0].insert(0, decks[0].pop(decks[0].index('skull')))
					state[0] += 1
					state[1] = stacks[0].index('skull')
					print "RL player added a tile to their stack"
				elif action == 'bet':
					state[4] += 1
					print "RL player bet %d" % state[4]
					bluff_guess = raw_input("Do you think the RL player is bluffing? y/n:")
					if state[1] > -1 and state[4] > state[1]:
						bluff_actual = 'y'
					else:
						bluff_actual = 'n'
					if bluff_guess == bluff_actual:
						correct += 1
					elif bluff_guess == 'y':
						false_pos += 1
					else:
						false_neg += 1
				elif action == 'pass':
					passed = True
					print "RL player passed their turn"
				else:
					print "RL player did invalid action", action
				print ""
			else:
				print "Human player's turn"
				print "Your deck:", decks[1]
				print "Your stack:", stacks[1]
				print "RL player's stack:", ['?' for x in stacks[0]]
				action = raw_input("Select an action from " + str(actions) + ": ")
				while action not in actions:
					action = raw_input("Not a valid action, try again: ")
				if action == 'addFlower':
					stacks[1].insert(0, decks[1].pop(decks[1].index('flower')))
					state[2] += 1
					if state[3] > -1:
						state[3] = stacks[1].index('skull')
				elif action == 'addSkull':
					stacks[1].insert(0, decks[1].pop(decks[1].index('skull')))
					state[2] += 1
					state[3] = stacks[1].index('skull')
				elif action == 'bet':
					state[4] += 1
				elif action == 'pass':
					passed = True
				print ""
	winner = 0
	if len(stacks[0]) - len(stacks[1]) == state[4] % 2:
		if state[3] > -1 and state[4] > state[3]:
			winner = 0
			print "Human player flips over a skull in their own stack"
		elif state[1] > -1 and state[4] > state[2] + state[1]:
			winner = 0
			print "Human player flips over a skull in RL player's stack"
		else:
			winner = 1
			print "Human player flips over %d flowers" % state[4]
	else:
		if state[1] > -1 and state[4] > state[1]:
			winner = 1
			print "RL player flips over a skull in their own stack"
		elif state[3] > -1 and state[4] > state[0] + state[3]:
			winner = 1
			print "RL player flips over a skull in human player's stack"
		else:
			winner = 0
			print "RL player flips over %d flowers" % state[4]
	if winner == 0:
		print "RL agent won!\n"
	else:
		print "Human player won!\n"
	return winner, correct, false_pos, false_neg

def main():
	policy = readPolicy()
	win_count = [0,0]
	correct_guesses = [0,0]
	false_positives = [0,0]
	false_negatives = [0,0]
	while True:
		decks = setup()
		winner, correct, false_pos, false_neg = play(decks, policy)
		win_count[winner] += 1
		correct_guesses[winner] += correct
		false_positives[winner] += false_pos
		false_negatives[winner] += false_neg
		quit = raw_input("Quit now? y/n:")
		if quit == 'y':
			break
	print "Victories", win_count
	print "Correct bluff guesses:", correct_guesses
	print "False positives:", false_positives
	print "False false_negatives", false_negatives

if __name__ == '__main__':
	main()