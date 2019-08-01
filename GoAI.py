import pickle
from collections import OrderedDict

from match import Match, HumanPlayer
from genetic_algorithm import Generation, AIPlayer

def run_ga(settings):
    for i in range(settings['n_gen']):
        if i==0:
            g = Generation(pop_size=settings['pop_size'], n_genes=settings['n_genes'], max_gene_size=settings['max_gene_size'])
        else:
            g = g.reproduce(settings['pop_size'])
        #g.play_one(settings['board_size'])
        g.play(settings['board_size'])
        with open("{}{}.pickle".format(settings['path'],i), "wb") as f:
            pickle.dump(g, f)
        print("Generation {} completed.".format(i+1))
        
def brief_ga():
    run_ga({
        'n_gen': 2,
        'pop_size': 5,
        'board_size': 6,
        'path': "data_quick\\",
        'n_genes': 5,
        'max_gene_size': 4,
        })

def full_ga():
    run_ga({
        'n_gen': 10,
        'pop_size': 10,
        'board_size': 9,
        'path': "data\\",
        'n_genes': 10,
        'max_gene_size': 9,
        })
        
def play_ga(board_size=9):
    with open("data_20190730\\4.pickle","rb") as f:
        g = pickle.load(f)
    match = Match(HumanPlayer(0),AIPlayer(1,g.pop[0]),board_size)
    scores = match.play()
    print("\nFinal Score: {}".format(scores))

def main():
    menu_options = OrderedDict([("Q",{"prompt":"Quit"}),("B",{"prompt":"Run brief genetic algorithm", "fn":brief_ga}),("P",{"prompt":"Play against a genetic algorithm", "fn":play_ga})])
    while True:
        menu_response = input("\n".join("{}: {}".format(i,v["prompt"]) for i,v in menu_options.items())+"\n").upper()
        if menu_response == 'Q':
            break
        menu_options.get(menu_response,{"fn":lambda:False})["fn"]()


if __name__ == '__main__':
    main()
