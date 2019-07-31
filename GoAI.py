from collections import defaultdict
import random
import pickle

from genetic_algorithm import Individual
from match import Match

class Generation:
    pop = []
    scores = []

    #create new generation
    def __init__(self, pop=None, pop_size=50, n_genes=10, max_gene_size=9):
        if pop:
            self.pop = pop
        else:
            self.pop = [Individual(n_genes=n_genes, max_gene_size=max_gene_size, n_players=2) for i in range(pop_size)]

    def play_one(self, board_size, min_for_move=2):
        match = Match(self.pop[0],self.pop[1],board_size,min_for_move)
        scores = match.play(verbose=True)
        print("\nFinal Score: {}".format(scores))
    
    #plays the entire generation against itself
    def play(self, board_size, min_for_move=2):
        self.scores = [0]*len(self.pop);
        for i in range(len(self.pop)):
            for j in range(len(self.pop)):
                if i==j: continue
                match = Match(self.pop[i],self.pop[j],board_size,min_for_move)
                scores = match.play()
                score_gap = scores[0][0]-scores[1][0]
                if scores[0][0] == scores[1][0]:
                    print("Game {}, {} finished. Tie. Score: {}-{}".format(i,j,scores[0][0],scores[1][0]))
                elif scores[0][1] == 0:
                    print("Game {}, {} finished. Player 1 Won. Score: {}-{}".format(i,j,scores[0][0],scores[1][0]))
                    self.scores[i] += score_gap
                    self.scores[j] -= score_gap
                else:
                    print("Game {}, {} finished. Player 2 Won. Score: {}-{}".format(i,j,scores[1][0],scores[0][0]))
                    self.scores[i] -= score_gap
                    self.scores[j] += score_gap
            print("Individual {} has finished its games.".format(i))
        for i in range(len(self.pop)):
            print("{}: {}".format(i, self.scores[i]))
    
    def reproduce(self, pop_size):
        surv_idx, surv_score = zip(*[(k,v) for k,v in enumerate(self.scores) if v>0])
        print("There were {} survivors.".format(len(surv_idx)))
        if not surv_idx: return None
        
        ngen = []
        for j in range(len(pop_size)):
            #weight random parent selection by score
            parents = random.choices(surv_idx, weights=surv_score, k=2)
            ngen.append(Individual([self.pop[p] for p in parents]))
        
        return Generation(ngen)
    
    def __str__(self):
        return "\n".join("Individual {}\n{}".format(i,str(g)) for i,g in enumerate(self.pop))
    
    def save(self, fname):
        with open(fname, "wb") as f:
            pickle.dump(self, f)
            
            
            
pop_size = 10
board_size = 9
path = "data\\"
            
for i in range(5):
    if i==0:
        g = Generation(pop_size=pop_size, n_genes=10, max_gene_size=3)
    else:
        g = g.reproduce(pop_size)
    g.play_one(board_size)
    break
    g.play(board_size)
    g.save("{}{}.pickle".format(path,i))
    print("Generation {} completed.".format(i+1))
