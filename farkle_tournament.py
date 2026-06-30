import random as rnd
import numpy as np
from agents import RandomAgent
from Game import FarkleGame
from agents import NNAgent
import torch
import torch.nn.functional as F
from torch import nn
from FarkleNeuralNetwork import NeuralNetwork
import time
import copy
import os


torch.set_num_threads(1)

class RandomTournament:

    def __init__(self, N_Agents, Epochs, games):

        self.Agents = [RandomAgent() for r in range(N_Agents)]
        self.Epochs = Epochs
        self.games = games
        self.results = [[0, 0, 0] for i in range(N_Agents)] # results rep. by a 2D list with each idx the results of the corresponding agent
                                                            # results [weighted wins (per win +1/N_players), number of games (+1 per game), fitness (wieghted wins/number of games)]
        self.idx_list = list(range(len(self.Agents)))                                                   

    def generate_schedule(self):

        all_pools = []

        temp_idx = self.idx_list.copy()

        rnd.shuffle(temp_idx)
        
        ptr = 0

        while ptr < len(temp_idx):
            size = rnd.randint(2, 10)
            pool = temp_idx[ptr : ptr + size]
            
            
            if len(pool) < 2:
                all_pools[-1].extend(pool)
            
            else:
                all_pools.append(pool)
            
            ptr += size

        return all_pools
    
    def run_game(self, agents):

        game = FarkleGame(len(agents))

        game.reset()

        while not game.done:

            current_player = game.cur_player
            agent = agents[current_player]
            state = game.get_state()
            action = agent.choose_action(state, game)
    
            game.step(action)

        winner = agents[game.winner]
        return winner
    
    def run_epoch(self):
        sch = self.generate_schedule()

        for _ in range(self.games):
            for j in sch:
                current_order = j[:]
                rnd.shuffle(current_order)

                participants = [self.Agents[i] for i in current_order]

                winner = self.run_game(participants)
                win_idx = self.Agents.index(winner)
                N = len(participants)
                    
                self.results[win_idx][0] += N/10
                for idx in j:
                    self.results[idx][1] += 1
            
    

    def run_tournament(self):
        for e in range(self.Epochs):
            start = time.time()
            self.run_epoch()
            print(f"Epoch {e+1} finished in {time.time() - start:.2f} seconds")
            
        
        self.calc_fitness()
        fitnesses = [self.results[i][2] for i in range(len(self.results))]
        sd = np.std(fitnesses)
        print(sd)       
        

    def calc_fitness(self):
        for i in self.results:
            Weighted_wins = i[0]
            games_played = i[1]
            if i[1] > 0:
                i[2] = Weighted_wins / games_played

    def convergence_test(self, sd_limit):

        self.run_epoch()
        self.calc_fitness()

        fitnesses = [self.results[i][2] for i in range(len(self.results))]
        sd = np.std(fitnesses)
        E = 1


        while sd > sd_limit:
            self.run_epoch()
            self.calc_fitness()
            E += 1
            fitnesses = [self.results[i][2] for i in range(len(self.results))]
            sd = np.std(fitnesses)

            if E % 10 == 0:
                print(f"your current standard deviation is: {sd}")
        
        print(f"{E} epochs until standard deviation of fitness below {sd_limit}")


class EvolutionTraining:

    def __init__(self, N_Agents, Generations,Epochs, games):

        self.Agents = [NNAgent() for r in range(N_Agents)]
        self.gen = Generations
        self.Epochs = Epochs
        self.games = games
        self.results = [[0, 0, 0, 0, 0] for i in range(N_Agents)] # results rep. by a 2D list with each idx the results of the corresponding agent
                                                            # results [weighted wins (per win +1/N_players), number of games (+1 per game), total points, N_turns, fitness]
        self.idx_list = list(range(len(self.Agents)))                                                   

    def generate_schedule(self):

        all_pools = []

        temp_idx = self.idx_list.copy()

        rnd.shuffle(temp_idx)
        
        ptr = 0

        while ptr < len(temp_idx):
            size = rnd.randint(2, 10)
            pool = temp_idx[ptr : ptr + size]
            
            
            if len(pool) < 2:
                all_pools[-1].extend(pool)
            
            else:
                all_pools.append(pool)
            
            ptr += size

        return all_pools
    
    def run_game(self, agents):

        Max_turns = 15
        turn_count = 1

        game = FarkleGame(len(agents))

        game.reset()



        while not game.done:


            current_player = game.cur_player
            agent = agents[current_player]
            state = game.get_state()
            action = agent.choose_action(game)

            prev_player_idx = game.cur_player
    
            game.step(action)

            if game.cur_player != prev_player_idx:
                if game.cur_player == 0:
                    turn_count += 1

            if turn_count > Max_turns:
                return [None, turn_count] + game.scores

        return [game.winner, turn_count] + game.scores
    
    def run_epoch(self):
        sch = self.generate_schedule()

        for _ in range(self.games):
            for j in sch:
                current_order = j[:]
                rnd.shuffle(current_order)
                
                participants = [self.Agents[i] for i in current_order]

                res = self.run_game(participants)

                winner = res[0]
                turn_count = res[1]
                scores = res[2:]

                if winner is not None:
                    
                    win_idx = current_order[winner]
                    N = len(participants)
                    self.results[win_idx][0] += N/10
                        
                        
                
                for idx in range(len(current_order)):
                    self.results[current_order[idx]][1] += 1
                    self.results[current_order[idx]][2] += min(res[idx + 2], 1.0)
                    self.results[current_order[idx]][3] += res[1]
                    



    def run_tournament(self):
        for _ in range(self.Epochs):
            self.run_epoch()
        
        self.calc_fitness()


    def calc_fitness(self):
        for i in self.results:
            Weighted_wins = i[0]
            games_played = i[1]
            points = i[2]
            turns = i[3]
            if i[1] > 0:
                i[4] = 0.5*(Weighted_wins / games_played) + 0.5*(points / turns)

    def convergence_test(self, sd_limit):

        self.run_epoch()
        self.calc_fitness()

        fitnesses = [self.results[i][4] for i in range(len(self.results))]
        sd = np.std(fitnesses)
        E = 1


        while sd > sd_limit:
            self.run_epoch()
            self.calc_fitness()
            E += 1
            fitnesses = [self.results[i][4] for i in range(len(self.results))]
            sd = np.std(fitnesses)

            if E % 10 == 0:
                print(f"your current standard deviation is: {sd}")
        
        print(f"{E} epochs until standard deviation of fitness below {sd_limit}")

    def ranking(self):
        ranked_pop = []
        for i in range (len(self.Agents)):
            ranked_pop.append([i, self.Agents[i], self.results[i][4]])

        ranked_pop = sorted(ranked_pop, key = lambda elem: elem[2], reverse = True)

        Ranked_agents = []

        for i in ranked_pop:
            Ranked_agents.append(i[1])

        return Ranked_agents

        # output should be an ordered list of all agents
        

    def run_training(self):
        sd_limit = 0.001
        gen_limit = self.gen

        generations =  0
        converged = False

        while generations <= gen_limit and not converged:
            start = time.time()
            generations += 1
            self.results = [[0, 0, 0, 0, 0] for i in range(len(self.Agents))]

            self.run_tournament()

            fitnesses = [self.results[i][4] for i in range(len(self.results))]
            sd = np.std(fitnesses)
            run_time = time.time() - start

            self.get_readout(fitnesses, generations, run_time, sd, sd_limit)

            if sd < sd_limit:
                converged = True

            elif generations <= gen_limit:
                self.breed()

        self.save_agents()

        print("training is now complete")


        # should run_tournament N times and breed after each. after training is complete it should save the best 20 using save_agent()

    def breed(self):
        Ranked_agents = self.ranking()
        survivors = []
        for i in range(20):
            survivors.append(copy.deepcopy(Ranked_agents[i]))

        mutation_rate = 0.02
        mutation_strength = 0.15

        while len(survivors) < len(self.Agents):
            parent = rnd.choice(survivors[:20])
            child = copy.deepcopy(parent)

            with torch.no_grad():
                for param in child.brain.parameters():
                    mask = (torch.rand(param.shape) < mutation_rate).float()
                    noise = torch.randn(param.shape) * mutation_strength
                    param.add_(mask * noise)

            survivors.append(child)

        self.Agents = survivors

    # overwrites the self.Agents list with a list of surviving agents and their (mutated) children


    def save_agents(self):
        agents = self.ranking()

        elites = [agents[i] for i in range(20)]
        
        if not os.path.exists("final_models"):
            os.makedirs("final_models")

        for i in range(len(elites)):
            file_path = f"final_models/FarkleNN_{i+1}.pt"
            torch.save(elites[i].brain.state_dict(), file_path)

        print(f"top 20 agents saved under final_models!")


    # should save an agent in a file such that it can easily be loaded back in. and the file can be easily found


    def get_readout(self, fitnesses, generation, gen_time, sd, sd_limit):
        max_fit = max(fitnesses)
        avg_fit = np.mean(fitnesses)

        print(f"\n========== Summary: Generation {generation} ==========")
        print(f"\n Performance metrics:")
        print(f"\n===== Maximum fitness: {max_fit} =====")
        print(f"\n===== Average fitness: {avg_fit} =====")
        print(f"\n Population Health data:")
        print(f"\n===== Standard deviation of fitness: {sd} with limit {sd_limit} =====")
        print(f"\n===== The generation lasted for {gen_time} seconds =====")

    def load_models(self):
        ag = []
        mutation_rate = 0.04
        mutation_strength = 0.035        

        for agent_number in range (20):
            file_path = f"final_models_4/FarkleNN_{agent_number + 1}.pt"
            loaded_agent = NNAgent()
            state_dict = torch.load(file_path, map_location=torch.device('cpu'), weights_only=True)
            loaded_agent.brain.load_state_dict(state_dict)
            loaded_agent.brain.eval()
            ag.append(loaded_agent)
        
            while len(ag) < len(self.Agents):
                parent = rnd.choice(ag[:20])
                child = copy.deepcopy(parent)

                with torch.no_grad():
                    for param in child.brain.parameters():
                        mask = (torch.rand(param.shape) < mutation_rate).float()
                        noise = torch.randn(param.shape) * mutation_strength
                        param.add_(mask * noise)

                ag.append(child)

        self.Agents = ag
        print("agents successfully loaded into training program")

        



        
Training = EvolutionTraining(200, 200, 20, 10)
#Training.load_models()
Training.run_training()



    







    
                
                



            
                





        











            






            