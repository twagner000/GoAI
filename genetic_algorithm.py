import random
import copy

import numpy as np

from match import Match, Player

class Gene:
    UNOCCUPIED_ONLY = -2
    ANYTHING = -1
    
    EDGE_YES = 1
    EDGE_EITHER = 0
    EDGE_NO = -1
    EDGE_CHOICES = (EDGE_YES, EDGE_EITHER, EDGE_NO)
    
    @staticmethod
    def random_element(n_players):
        return random.randint(-2,n_players-1)
    
    #randomly generate a new gene of shape (size,size)
    #element value of UNOCCUPIED_ONLY denotes empty space (no piece)
    #element value of ANYTHING denotes neutral (no piece/any piece)
    #element values greater than ANYTHING denote specific players, starting with current player
    def __init__(self, size, n_players, edge_chance):
        self.n_players = n_players
        self.gene = np.reshape([Gene.random_element(n_players) for i in range(size*size)], (size,size))
        self.edges = np.reshape([random.choice(self.EDGE_CHOICES) if random.random() < edge_chance else self.EDGE_EITHER for i in range(4)], (2,2))
        
    @property
    def size(self):
        return len(self.gene)
    
    def mutate(self, max_percent, edge_chance):
        n_elem = self.size*self.size
        for i in random.choices(range(n_elem), k=random.randint(1,int(n_elem*max_percent))):
            self.gene[np.unravel_index(i,self.gene.shape)] = Gene.random_element(self.n_players)
        for i in range(4):
            if random.random() < edge_chance:
                self.edges[np.unravel_index(i,(2,2))] = random.choice(self.EDGE_CHOICES)
    
    def __str__(self):
        return "size={}, edges={}, elements={}".format(self.size,self.edges,self.gene)


class Individual: #renamed from Genome
    MIN_FOR_MOVE = 2
    
    def __init__(self, parents=None, n_genes=None, max_gene_size=None, n_players=None, edge_chance=0.05, whole_gene_mutation_chance=0.02, partial_gene_mutation_chance=0.1, partial_gene_mutation_max_percent=0.3, partial_gene_mutation_edge_chance=0.01):
        if parents:
            #create new individual from parents
            self.max_gene_size = max(p.max_gene_size for p in parents)
            self.n_players = max(p.n_players for p in parents)
            self.genes = [None]*max(len(p.genes) for p in parents)
            for i in range(len(self.genes)):
                if random.random() < whole_gene_mutation_chance:
                    self.genes[i] = Gene(random.randint(2, self.max_gene_size), self.n_players, edge_chance)
                else:
                    self.genes[i] = copy.deepcopy(random.choice(parents).genes[i]) #changed 7/28/19; old selected a random gene from that parent, not ith gene
                    if random.random() < partial_gene_mutation_chance:
                        self.genes[i].mutate(partial_gene_mutation_max_percent, partial_gene_mutation_edge_chance)
        else:
            #create new individual with random genes
            self.max_gene_size = max_gene_size
            self.n_players = n_players
            self.genes = [Gene(random.randint(2, self.max_gene_size), self.n_players, edge_chance) for i in range(n_genes)]
    
    def __str__(self):
        return "n_genes={}, max_gene_size={}, n_players={}\n{}".format(len(self.genes), self.max_gene_size, self.n_players, "\n".join(str(g) for g in self.genes))
        
    #board is a 2d numpy array of integers
    def get_move(self, board, cur_player):
        #adjust board for player (2 players only!)
        if cur_player != 0:
            board = board.copy()
            board[board>=0] = 1-board[board>=0]
        bsize = len(board)
        moves = np.zeros((bsize,bsize), dtype='int')
        for gene_obj in self.genes:
            gsize = gene_obj.size
            gene = gene_obj.gene
            edges = gene_obj.edges
            for r in range(bsize-gsize):
                for c in range(bsize-gsize):
                    cur_edges = np.array([[r==0, c==bsize-gsize-1], [r==bsize-gsize-1, c==0]], dtype='float')-0.5
                    for rot in range(4):
                        if rot:
                            gene = np.rot90(gene)
                            edges = np.rot90(edges)
                        
                        #check edge constraints
                        if np.any(cur_edges*edges < 0):
                            continue #at least one failure
                            
                        #check player constraints and add move candidates
                        board_segment = board[r:r+gsize,c:c+gsize]
                        match = ((gene==Gene.UNOCCUPIED_ONLY) & (board_segment==Match.UNOCCUPIED)) | (gene==Gene.ANYTHING) | ((gene>Gene.ANYTHING) & ((board_segment==Match.UNOCCUPIED) | (board_segment==gene)))
                        
                        #print('match for {},{},{}:\n'.format(r,c,rot),match)
                        if np.all(match):
                            moves[r:r+gsize,c:c+gsize] += (board_segment==Match.UNOCCUPIED) & (gene==Gene.ANYTHING+1)
                            
        #changed 7/29/19; old selected first space with max score
        locs = np.arange(bsize*bsize)[((moves>=self.MIN_FOR_MOVE) & (moves==moves.max())).flatten()]
        if len(locs):
            loc = np.random.choice(locs) 
            return (loc//bsize,loc%bsize)
        else:
            return None
    
class AIPlayer(Player):
    def __init__(self, player_idx, individual, *args, **kwargs):
        super().__init__(self, player_idx, *args, **kwargs)
        self.individual = individual
        
    def get_move(self, board_array):
        return self.individual.get_move(board_array, self.player_idx)

class Generation:
    pop = []
    scores = []

    #create new generation
    def __init__(self, pop=None, pop_size=50, n_genes=10, max_gene_size=9):
        if pop:
            self.pop = pop
        else:
            self.pop = [Individual(n_genes=n_genes, max_gene_size=max_gene_size, n_players=2) for i in range(pop_size)]

    def play_one(self, board_size):
        match = Match(AIPlayer(0,self.pop[0]),AIPlayer(1,self.pop[1]),board_size)
        scores = match.play(verbose=True)
        print("\nFinal Score: {}".format(scores))
    
    #plays the entire generation against itself
    def play(self, board_size):
        self.scores = [0]*len(self.pop);
        for i in range(len(self.pop)):
            for j in range(len(self.pop)):
                if i==j: continue
                match = Match(AIPlayer(0,self.pop[i]),AIPlayer(1,self.pop[j]),board_size)
                scores = match.play()
                score_gap = scores[0][0]-scores[1][0]
                if scores[0][0] == scores[1][0]:
                    print("Game {}, {} finished. Tie. Score: {} - {}".format(i,j,scores[0][0],scores[1][0]))
                elif scores[0][1] == 0:
                    print("Game {}, {} finished. Player 1 Won. Score: {} - {}".format(i,j,scores[0][0],scores[1][0]))
                    self.scores[i] += score_gap
                    self.scores[j] -= score_gap
                else:
                    print("Game {}, {} finished. Player 2 Won. Score: {} - {}".format(i,j,scores[1][0],scores[0][0]))
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
        for j in range(pop_size):
            #weight random parent selection by score
            parents = random.choices(surv_idx, weights=surv_score, k=2)
            ngen.append(Individual([self.pop[p] for p in parents]))
        
        return Generation(ngen)
    
    def __str__(self):
        return "\n".join("Individual {}\n{}".format(i,str(g)) for i,g in enumerate(self.pop))
    
