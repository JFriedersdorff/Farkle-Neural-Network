import random as rnd


class FarkleGame:

    def __init__(self, N_players):
        self.winning_score = 2000
        self.N_players = N_players

        self.reset()

    def reset(self):
        self.scores = [0 for i in range (self.N_players)]
        self.cur_player = 0
        self.winner = None
        self.done = False
        self.start_turn()

    def calc_score(self, throw):
        score = 0

        count = [sorted(throw).count(i) for i in range (1, 7)]
        
        for i in range(5):
            if count[i + 1] >= 3:
                score += ((i + 2) * 100 * (count[i + 1] - 2))/self.winning_score

        if count[0] <= 2:
            score += (100*count[0])/self.winning_score
        else:
            score += (1000 * (count[0] - 2))/self.winning_score
        
        if count[4] <= 2:
            score += (50*count[4])/self.winning_score

        if throw == [1,2,3,4,5,6]:
            score = 2500/self.winning_score
        
        return score
    
    def is_valid_scoring(self, throw):
        if self.calc_score(throw) == 0:
            return False
        
        for d in range (len(throw)):
            throw_new = throw.copy()
            del throw_new[d] 
            if self.calc_score(throw) == self.calc_score(throw_new):
                return False
            
        if not False:
            return True

    def get_state(self):
        my_score = self.scores[self.cur_player]
        max_score = max(self.scores)
        best_opp_score = max(score for idx, score in enumerate(self.scores) if idx != self.cur_player)
        dist_to_max = max_score - my_score
        roll = self.roll
        count = [roll.count(i) for i in range (1, 7)]
        V = [my_score, max_score, best_opp_score, dist_to_max, self.meld_total, self.dice_in_play, self.phase]
        V.extend(count)
        return V 
    
    def roll_dice(self):
        self.roll = [rnd.randint(1,6) for _ in range (self.dice_in_play)]

    def step(self, action):
        if self.phase == 0:
            self.select_dice(action)
        else:
            self.to_continue(action)

    def select_dice(self, action):
        scored = []
        for i in range(len(action)):
            if action[i] == 1:
                scored.append(self.roll[i])

        if self.is_valid_scoring(scored):
            scored_tot = self.calc_score(scored)
            self.meld_total += scored_tot
            self.dice_in_play -= len(scored)
            self.phase = 1
            
            if self.dice_in_play == 0:
                self.dice_in_play = 6

        
        else:
            self.increment_player()
            self.start_turn()


    def to_continue(self, action):
        if action == 0:
            self.end_turn()

        else:
            self.roll_dice()

            if self.has_farkled():
                self.farkle()
            else:
                self.phase = 0

    def increment_player(self):
        self.cur_player += 1
        if self.cur_player > self.N_players - 1:
            self.cur_player = 0

    def is_winner(self):
        if self.scores[self.cur_player] >= 1:
            self.winner = self.cur_player
            self.done = True

    def start_turn(self):
        self.meld_total = 0
        self.dice_in_play = 6
        self.phase = 0
        self.roll_dice()

        if self.has_farkled():
            self.farkle()

    def end_turn(self):
        self.bank_score()
        self.is_winner()
        
        if not self.done:
            self.increment_player()
            self.start_turn()

    def farkle(self):
        self.meld_total = 0
        self.end_turn()

    def bank_score(self):
        self.scores[self.cur_player] += self.meld_total

    def get_legal_actions(self):
        
        if self.phase == 0:
            candidate_indices = []
            legal_actions = []
            
            for i in range(len(self.roll)):
                score = self.calc_score(self.roll)
                pot_scoring = self.roll.copy()
                del pot_scoring[i]
                if self.calc_score(pot_scoring) < score:
                    candidate_indices.append(i)

            N = len(candidate_indices)
            compressed_poss_actions = self.get_binary_count(N)


            for i in range(len(compressed_poss_actions)):
                dice = []
                for j in range(len(candidate_indices)):
                    
                    if compressed_poss_actions[i][j] == 1:
                        dice.append(self.roll[candidate_indices[j]])

                act = [0] * self.dice_in_play

                if self.is_valid_scoring(dice):
                    for k in range(len(compressed_poss_actions[i])):
                        if compressed_poss_actions[i][k] == 1:
                            act[candidate_indices[k]] = 1
                        
                    legal_actions.append(act)
            
        else:
                legal_actions = [0, 1]

        return legal_actions

    def get_binary_count(self, N):

        binary_count = []

        for i in range (2 ** N):
            bits = [(i >> d) & 1 for d in range(N - 1, -1, -1)]
            binary_count.append(bits)

        return binary_count
    
    def has_farkled(self):
        max_meld = self.calc_score(self.roll)

        if max_meld == 0:
            return True
        
        else:
            return False
        











