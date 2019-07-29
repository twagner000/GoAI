import random
import copy


class Gene:
    '''//creates a new gene randomly
    //(size is the length of one edge of the square gene)
    //  values 1, 2... denote a certain player
    //  value of 0 denotes neutral (no piece/any piece)
    //  value of -1 reserved for other uses
    //  value of -2 denotes empty space (no piece)'''
    def __init__(self, size=None, players=None, firstEdgeChance=0.05, secondEdgeChance=0.1):
        self.size = size
        self.players = players
        self.gene = [Gene.random_element(self.players) for i in range(self.size*self.size)]
        
        #change some genes to edges, i.e. 1 -> -11 and 2 -> -12
        if random.random() < firstEdgeChance:
            for i in range(self.size):
                if self.gene[i] > 0:
                    self.gene[i] = -self.gene[i]-10
            
            #change some genes to have two edges
            if random.random() < secondEdgeChance:
                for i in range(1,self.size):
                    if self.gene[i*self.size] > 0:
                        self.gene[i*self.size] = -self.gene[i*self.size]-10
                        
    
    @staticmethod
    def random_element(players):
        x = random.randint(-1,players)
        return -2 if x==-1 else x #-1 is reserved
    
    def mutate(self, partialGeneMutationMaxPercent):
        for i in random.choices(range(len(self.gene)), k=random.randint(1,int(len(self.gene)*partialGeneMutationMaxPercent))):
            self.gene[i] = Gene.random_element(self.players)
    
    #returns a rotated version of the gene (1-dimensional representation), t = number of turns clockwise
    def getRotatedGene(self, t):
        rotate_func = [
            lambda r,c: r*self.size+c,
            lambda r,c: (self.size-1-c)*self.size+r,
            lambda r,c: (self.size-1-r)*self.size+(self.size-1-c),
            lambda r,c: c*self.size+(self.size-1-r)]
        return [gene[rotate_func[t%4](i//self.size,i%self.size)] for i in range(self.size*self.size)]
    
    def __str__(self):
        return "{}/{}".format(self.size,"\t".join(str(i) for i in self.gene))


class Genome:
    genes = []
    maxGeneSize = None
    players = None
    
    #create individual from parents
    def __init__(self, parents=None, numGenes=None, maxGeneSize=None, players=None, wholeGeneMutationChance=0.02, partialGeneMutationChance=0.1, partialGeneMutationMaxPercent=0.3):
        if parents:
            self.maxGeneSize = max(p.maxGeneSize for p in parents)
            self.players = max(p.player for p in parents)
            self.genes = [None]*max(len(p.genes) for p in parents)
            for i in range(numGenes):
                if random.random() < wholeGeneMutationChance:
                    self.genes[i] = Gene(random.randint(2, self.maxGeneSize), self.players)
                else:
                    self.genes[i] = copy.deepcopy(random.choice(parents).genes[i]) #changed 7/28/19; old selected a random gene from that parent, not ith gene
                    if random.random() < partialGeneMutationChance:
                        self.genes[i].mutate(partialGeneMutationMaxPercent)
        else:
            self.maxGeneSize = maxGeneSize
            self.players = players
            self.genes = [Gene(random.randint(2, self.maxGeneSize), self.players) for i in range(numGenes)]
    
    def __str__(self):
        return "{}\t{}\t{}\n{}".format(len(self.genes), self.maxGeneSize, self.players, "\n".join(str(g) for g in self.genes))
        
    '''#creates individual from an array of Genes
    public Genome(Gene[] genes)
    {
        this.genes = genes;
        maxGeneSize = 0;
        for (int i=0; i<genes.length; i++)
            if (genes[i].getGeneSize() > maxGeneSize)
                maxGeneSize = genes[i].getGeneSize();
        players = getMaxPlayer();
    }'''
    
    '''//swaps all 1's in the gene with player and vice versa (including edge spaces)
    public Genome adjustForPlayer(int id)
    {
        Gene[] newGenes = genes;
        for (int i=0; i<genes.length; i++)
            genes[i].adjustForPlayer(id);
        return new Genome(newGenes);
    }'''
    
    
    
