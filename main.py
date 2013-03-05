from startautomaton import *

def analyse_lexical(expression):
	pass


def renverser_tuple(tuple):	
	origin, lettre, fin = tuple
	return (fin, lettre, origin)



a = startautomaton(
    epsilons = ['0'],
    states = [5], initials = [0,1], finals = [3,4],
    transitions=[(0,'a',1), (1,'b',2), (2,'b',2), (2,'0',3), (3,'a',4)]
    )
