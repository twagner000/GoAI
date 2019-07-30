import numpy as np

class Match:
    UNOCCUPIED = -1
    
    def __init__(self, player1, player2, board_size, min_for_move):
        self._players = [player1, player2]
        self._board_size = board_size
        self._min_for_move = min_for_move
        self._dragons = None
        self._board = None
        self._scores = None
    
    #returns None or a list of tuples (score, player) with winner listed first.
    @property
    def scores(self):
        return self._scores
    
    @property
    def board_size(self):
        return self._board_size
        
    def board_array(self):
        return np.array([[self._board[r,c]['player_idx'] for c in range(self._board_size)] for r in range(self._board_size)], dtype='int')
    
    def __str__(self):
        return str(self.board_array())
        '''scores = self.scores
        if not scores:
            return "Match incomplete."
        outcome = "Tie" if scores[0][0] == scores[1][0] else "Player {} Won.".format(scores[0][1]+1)
        return "{} Score: {}-{}".format(outcome, scores[0][0], scores[1][0])'''
        
    def play(self, verbose=False):
        n_players = len(self._players)
        
        #list of dictionaries with keys 'player_idx' and 'spaces'
        #'spaces' is a list of location tuples
        self._dragons = [{'player_idx':self.UNOCCUPIED, 'spaces':[(r,c) for c in range(self._board_size) for r in range(self._board_size)]}]
        
        #board is a dictionary where keys are (row,column) and value is the current dragon in that space
        self._board = dict((space,self._dragons[0]) for space in self._dragons[0]['spaces'])
        
        self._prisoners_lost = [0]*len(self._players)
        self._not_passed = [1]*len(self._players)
        
        for turn in range(4*self._board_size*self._board_size):
            #end if all players have passed
            if sum(self._not_passed) == 0: break
            
            cur_player = turn%n_players
            
            if verbose: print("\n\n\nTurn {}, Player {}".format(turn, cur_player))
            
            loc = self._players[cur_player].get_move(self.board_array()+1, self._min_for_move)
            self._not_passed[cur_player] = 1*self.make_move(loc,cur_player)
            
            if verbose: print("\nMove {}:\n\n{}".format(loc, str(self)))
            
            self.clear_dead_dragons(1-cur_player) #check opponent first
            self.clear_dead_dragons(cur_player)
            
            if verbose: print("\n",str(self))
            
            #NOTE: does not check for position that has occurred previously in the game
        
        return self.score()
        
        
    def get_neighbors(self,loc):
        r,c = loc
        return [
            (r-1,c) if r>0 else None,
            (r,c+1) if c<self._board_size-1 else None,
            (r+1,c) if r<self._board_size-1 else None,
            (r,c-1) if c>0 else None]
            
    def merge_dragons(self, dragon1, dragon2):
        print('merging dragons...')
        if dragon1['player_idx'] != dragon2['player_idx']:
            raise Exception("Dragons must belong to the same player in order to merge.")
        print('dragon1',self._dragons.index(dragon1),dragon1['spaces'])
        print('dragon2',self._dragons.index(dragon2),dragon2['spaces'])
        for space in dragon2['spaces']:
            self._board[space] = dragon1
        dragon1['spaces'] += dragon2['spaces']
        print('final dragon1',self._dragons.index(dragon1),dragon1['spaces'])
        self._dragons.remove(dragon2)
    
    def get_dragon_liberties(self, dragon):
        empty_neighbors = set()
        for space in dragon['spaces']:
            for neighbor in self.get_neighbors(space):
                if neighbor != None and self._board[neighbor]['player_idx'] == self.UNOCCUPIED:
                    empty_neighbors.add(neighbor)
        return empty_neighbors
    
    
    def make_move(self, loc, player_idx):
        #space must be unoccupied
        if loc == None or self._board[loc]['player_idx'] != self.UNOCCUPIED:
            return False
        
        #remove space from its current dragon
        self._board[loc]['spaces'].remove(loc)
        
        #find any adjacent dragons that already belong to this player
        same_player_dragons = []
        for neighbor in self.get_neighbors(loc):
            if neighbor != None and self._board[neighbor]['player_idx'] == player_idx:
                same_player_dragons.append(self._board[neighbor])
        
        if same_player_dragons:
            #add new location to the player's first adjacent dragon
            self._board[loc] = same_player_dragons[0]
            same_player_dragons[0]['spaces'].append(loc)
            #merge any remaining dragons of the player's that were connected
            for dragon in same_player_dragons[1:]:
                if dragon['spaces']: #may have already been merged if neighbor multiple times
                    self.merge_dragons(same_player_dragons[0],dragon)
        else:
            #create a new dragon
            self._dragons.append({'player_idx':player_idx, 'spaces':[loc]})
            self._board[loc] = self._dragons[-1]        
        
        return True
    
    def clear_dead_dragons(self, player_idx):
        for dragon in self._dragons:
            if dragon['player_idx'] == player_idx:
                if not dragon['spaces']:
                    print("Why is there a dragon that doesn't occupy any spaces?")
                    self._dragons.remove(dragon)
                else:
                    if not self.get_dragon_liberties(dragon):
                        self._prisoners_lost[dragon['player_idx']] += len(dragon['spaces'])
                        dragon['player_idx'] = 0
    

    '''a player's score is...
    *the number of points of his/her color
    *plus the number of empty points that reach only his/her color
    *minus the number of its pieces which were captured (prisonersLost)
    *(according to New Zealand rules and Eric's prisoner addition)
    '''
    def score(self):
        scores = [-v for v in self._prisoners_lost]
        for dragon in self._dragons:
            if dragon['player_idx'] > self.UNOCCUPIED:
                #add points for spaces covered by stones
                scores[dragon['player_idx']] += len(dragon['spaces'])
            else:
                #if unoccupied dragon only touches one player, they get points for territory
                players_touching = set()
                for space in dragon['spaces']:
                    for neighbor in self.get_neighbors(space):
                        if neighbor != None and self._board[neighbor]['player_idx'] != self.UNOCCUPIED:
                            players_touching.add(self._board[neighbor]['player_idx'])
                if len(players_touching) == 1:
                    scores[list(players_touching)[0]] += len(dragon['spaces'])
        self._scores = tuple(sorted([(s,p) for p,s in enumerate(scores)], reverse=True))
        return self._scores
    
    
    