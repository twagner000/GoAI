from collections import defaultdict
import random
import pickle

from Genome import Genome

class Generation:
    pop = []
    scores = []

    #create new generation
    def __init__(self, pop=None, popSize=50, numGenes=10, maxGeneSize=9):
        if pop:
            self.pop = pop
        else:
            self.pop = [Genome(numGenes=numGenes, maxGeneSize=maxGeneSize, players=2) for i in range(popSize)]

    #plays the entire generation against itself
    def play(self, boardSize):
        minForMove = 2
        self.scores = [0]*len(self.pop);
        for i in range(len(self.pop)):
            for j in range(len(self.pop)):
                if i==j: continue
                match = GoMatch2Player(Player(1,pop[i]),Player(2,pop[j]),boardSize,minForMove)
                match.play()
                winner = match.getWinner()
                if winner == -1:
                    print("Game {}, {} finished. Tie. Score: {}-{}".format(i,j,match.getWinningScore(),match.getWinningScore()))
                elif winner == 0:
                    print("Game {}, {} finished. Player 1 Won. Score: {}-{}".format(i,j,match.getWinningScore(),match.getWinningScore()-match.getScoreGap()))
                    self.scores[i] += match.getScoreGap()
                    self.scores[j] -= match.getScoreGap()
                else:
                    print("Game {}, {} finished. Player 2 Won. Score: {}-{}".format(i,j,match.getWinningScore()-match.getScoreGap(),match.getWinningScore()))
                    self.scores[i] -= match.getScoreGap()
                    self.scores[j] += match.getScoreGap()
            print("Individual {} has finished its games.".format(i))
        for i in range(len(self.pop)):
            print("{}: {}".format(i, self.scores[i]))
    
    '''i (eric) put this in mostly for my own amusment.
     *it plays one game, printing the board each time a move is made,
     *so the user can "watch" the game being played and see how good 
     *these AIs are'''
    def playOne(self, boardSize):
        minForMove=2;
        match = GoMatch2Player(Player(1,pop[0]),Player(2,pop[1]),boardSize,minForMove)
        match.play()
        match.printWinnerAndScore()

    #this should call a method of the Genome object
    def printGeneSizes(self):
        for genome in self.pop:
            geneLengths = defaultdict(int)
            for gene in genome.genes:
                geneLengths[gene.size] += 1
            print(" ".join("{} ({})".format(k,v) for k,v in sorted(geneLengths.items())))
    
    def reproduce(self, popSize, numGenes):
        surv_idx, surv_score = zip(*[(k,v) for k,v in enumerate(self.scores) if v>0])
        print("There were {} survivors.".format(len(surv_idx)))
        if not surv_idx: return None
        
        ngen = []
        for j in range(len(popSize)):
            #weight random parent selection by score
            parents = random.choices(surv_idx, weights=surv_score, k=2)
            ngen.append(Genome([self.pop[p] for p in parents]))
        
        return Generation(ngen)
    
    def __str__(self):
        return "\n".join("Individual {}\n{}".format(i,str(g)) for i,g in enumerate(self.pop))
    
    def save(self, fname):
        with open(fname, "wb") as f:
            pickle.dump(self, f)
            
            
            
popSize = 50
boardSize = 9
path = "Data/"
            
for i in range(5):
    if i==0:
        g = Generation(popSize=popSize, numGenes=10, maxGeneSize=9)
    else:
        g = g.reproduce(i,popSize)
    print(g)
    g.play(boardSize)
    g.save("{}{}.pickle".format(path,i))
    print("Generation {} completed.".format(i+1))
