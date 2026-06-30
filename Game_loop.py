from Game import FarkleGame
from agents import HumanAgent
from agents import RandomAgent
from agents import NNAgent

import random as rnd

N_humans = int(input("how many Humans are playing: "))
N_random = int(input("how many random agents are playing: "))
N_neural = int(input("how many neural networks are playing (max 20): "))
N_games = int(input("how many games would you like to play: "))

N_total = N_humans + N_random + N_neural

game = FarkleGame(N_total)

agents = [HumanAgent() for i in range(N_humans)]
agents.extend(RandomAgent() for i in range(N_random))
agents.extend(NNAgent.get_agent(i + 1,5) for i in range(N_neural))

win_counter = [0 for i in range (N_total)]




for i in range(N_games):

    game.reset()

    while not game.done:

        current_player = game.cur_player
        agent = agents[current_player]
        state = game.get_state()
        action = agent.choose_action(game)
        
        game.step(action)
        print(game.scores)

    win_counter[game.winner] += 1

print(win_counter)
    




