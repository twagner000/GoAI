import random
import copy

import numpy as np

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
        self.size = size
        self.n_players = n_players
        self.gene = [Gene.random_element(n_players) for i in range(size*size)]
        self.edges = [random.choice(self.EDGE_CHOICES) if random.random() < edge_chance else self.EDGE_EITHER for i in range(4)]
    
    def mutate(self, max_percent, edge_chance):
        for i in random.choices(range(len(self.gene)), k=random.randint(1,int(len(self.gene)*elements_max_percent))):
            self.gene[i] = Gene.random_element(self.n_players)
        self.edges = [random.choice(self.EDGE_CHOICES) if random.random() < edge_chance else e for e in self.edges]
    
    def __str__(self):
        return "size={}, edges={}, elements={}".format(self.size,self.edges,self.gene)


class Individual: #renamed from Genome
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
    #with unoccupied spaces = 0
    #this player = 1
    #other players = 2, ...
    def get_move(self, board, min_for_move):
        bsize = len(board)
        moves = np.zeros((bsize,bsize), dtype='int')
        for gene_obj in self.genes:
            gsize = gene_obj.size
            gene = np.reshape(gene_obj.gene, (gsize, gsize))
            for r in range(bsize-gsize):
                for c in range(bsize-gsize):
                    for rot in range(4):
                        if rot:
                            gene = np.rot90(gene)
                        
                        #check edge constraints
                        if r!=0 and sum(gene[0,:] <= -8):
                            continue
                        if r!=bsize-gsize-1 and sum(gene[gsize-1,:] <= -8):
                            continue
                        if c!=0 and sum(gene[:,0] <= -8):
                            continue
                        if c!=bsize-gsize-1 and sum(gene[:,gsize-1] <= -8):
                            continue
                        
                        #make a copy and convert edge constraints to player constraints
                        gene_copy = np.copy(gene)
                        gene_copy[gene<=-8] = -gene[gene<=-8]-10
                        
                        #check player constraints and add move candidates
                        board_segment = board[r:r+gsize,c:c+gsize]
                        match = ((board_segment==0) & (gene_copy==Gene.UNOCCUPIED_ONLY)) | (gene_copy==Gene.ANYTHING) | ((gene_copy>Gene.ANYTHING) & (board_segment==gene_copy))
                        if np.sum(match) == match.size:
                            moves[r:r+gsize,c:c+gsize] += (board_segment==0) & (gene_copy==Gene.ANYTHING+1)
                            
        loc = np.empty((bsize, bsize), object)
        loc[:] = [[(r,c) for c in range(bsize)] for r in range(bsize)]
        loc = loc[(moves>=min_for_move) & (moves==moves.max())]
        if len(loc):
            return np.random.choice(loc)
        else:
            return None
    
    
    
