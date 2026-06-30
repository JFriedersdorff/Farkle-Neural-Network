import random as rnd
import torch
import torch.nn.functional as F
from torch import nn
from FarkleNeuralNetwork import NeuralNetwork
import copy
torch.set_num_threads(1)

class HumanAgent:

    def choose_action(self, game):
        phase = game.phase
        
        if phase == 0:
            roll = game.roll
            
            print("\nYour dice:")
            for i, d in enumerate(roll):
                print(f"{i}: {d}")
            
            raw = input("dice to keep (abc...): ")

            to_keep = list(raw)

            action = [0] * len(roll)

            for i in to_keep:
                action[int(i)] = 1

            return action
        
        if phase == 1:
            action = input("would you like to continue or bank your score? (1/0): ")

            return int(action)


class RandomAgent:

    def choose_action(self, game):
            legal = game.get_legal_actions()
            
            if len(legal) > 1:
                action_idx = rnd.randint(0, len(legal) - 1)
                action = legal[action_idx]
            
            else:
                action = legal[0]
            
            return action
    

class NNAgent:

    def __init__(self):
        self.brain = NeuralNetwork()

    def choose_action(self, game):
        action = None
        legal = game.get_legal_actions()

        desirability = []
        for act in legal:
            new_state = self.get_hypo_state(game, act)
            input_tensor = new_state
            with torch.no_grad():
                if game.phase == 0:
                    desirability.append(self.brain(input_tensor)[0].item())
                else:
                    desirability.append(self.brain(input_tensor)[1].item())

        best_idx = desirability.index(max(desirability))
        action = legal[best_idx]
        
        return action
    
    def get_hypo_state(self, game, action):
        new_state = game.get_state().copy()
        if game.phase == 0:
            dice = []
            for i in range(game.dice_in_play):
                if action[i] == 1:
                    dice.append(game.roll[i])

            meld = game.calc_score(dice)
            new_state[6] = 1
            new_state[4] += meld
            if new_state[5] - len(dice) == 0:
                new_state[5] = 6
            else:
                new_state[5] -= len(dice)

        else:
            if action == 0:
                new_state[0] += game.meld_total
                new_state[4] = 0

                max_score = max(game.scores)

                if new_state[0] == max_score:
                    new_state[1] = new_state[0]
                    new_state[3] = 0

                else:
                    new_state[3] = max_score - new_state[0]

        new_state_tensor = torch.FloatTensor(new_state)

        return new_state_tensor
    
    @classmethod
    def get_agent(cls, agent_number, gen):
        file_path = f"final_models_{gen}/FarkleNN_{agent_number}.pt"
        loaded_agent = cls()
        state_dict = torch.load(file_path, map_location=torch.device('cpu'), weights_only=True)
        loaded_agent.brain.load_state_dict(state_dict)
        loaded_agent.brain.eval()
        return loaded_agent

 


    


