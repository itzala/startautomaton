from automaton import *

def renverser_tuple(transition):	
	origin, lettre, fin = transition
	return (fin, lettre, origin)

class startautomaton(automaton):


	def __init__(self, alphabet=None, epsilons=None, states=None, initials=None, finals=None, 
        transitions=None):
		automaton.__init__(self, alphabet, epsilons, states, initials, finals, transitions)	

	def echanger_etats_ini_fin(self):

		ei = self._initial_states
		self.remove_initial_states()
		self.add_initial_states(self._final_states)
		self.remove_final_states()
		self.add_final_states(ei)


	def remove_initial_states(self):
		self._initial_states = set()

	def remove_final_states(self):
		self._final_states = set()

	def remove_transitions(self):
		self._adjacence.clear()

	def completer(self):	
		# Ajout de l etat puit :)
		etat_puit = self.get_maximal_id() + 1
		self.add_state(etat_puit)

		# for a in self.get_alphabet():
		# 	print(a)
		# 	print(self.delta(a))


		for e in self.get_states() :
			for a in self.get_alphabet() :
				tmp = self._delta(a, [e])
				if tmp == pretty_set():
					self.add_transition( (e, a, etat_puit) )


		return self

	def minimiser(self):
		return self

	def determinisation(self):
		"""
		1/ récupérer les états initiaux en un ensemble
		2/ déterminiser cet ensemble et enfiler les nouveaux états
		3/ récursif tant que file non vide


		nico -> si {1,2,3} alors new = 123
		"""
		return self

	def miroir(self):
		# Echange des etats finaux et initiaux
		self.echanger_etats_ini_fin()

		# Inversion de toutes les transitions
		tmp = self.get_transitions()
		self.remove_transitions()
		for trans in tmp:
			self.add_transition(renverser_tuple(trans))
			
		return self

	def express_to_auto(self):
		return self


	def est_deterministe(self):
		res = True
		for e in self.get_states():
			for l in self.get_alphabet():				
				res = False
		
		return res

	def est_complet(self):
		return True

	def union(self, aut2, deterministe=True):
		if self.get_alphabet() == aut2.get_alphabet():
			# On travaille sur des automates deterministes
			if deterministe and not aut2.est_deterministe():
				aut2.determinisation()

			if deterministe and not self.est_deterministe():
				self.determinisation()
			
			# On travaille sur des automates complet
			if not aut2.est_complet():
				aut2.completer()

			if not self.est_complet():
				self.completer()

			"""
				création de l'automate des couples
			"""
			return self
		else:
			return None

	def intersection(self, aut2, deterministe=True):
		# Il faut vérifier que les deux automates ont le même alphabet
		if self.get_alphabet() == aut2.get_alphabet():
			# On travaille sur des automates deterministes
			if deterministe and not aut2.est_deterministe():
				aut2.determinisation()

			if deterministe and not self.est_deterministe():
				self.determinisation()
			
			# On travaille sur des automates complet
			if not aut2.est_complet():
				aut2.completer()

			if not self.est_complet():
				self.completer()

			"""
				création de l'automate des couples
			"""
			return self
		else:
			return None

	def complement(self):
		return self

if __name__ == "__main__":
	alphabet = ['a', 'b', '0']
	epsilons = ['0']
	a = startautomaton(
		alphabet,
		epsilons,
    	states = [5], initials = [0,1], finals = [3,4],
    	transitions=[(0,'a',1), (1,'b',2), (2,'b',2), (2,'b',3), (3,'a',4)]
	)
	b = startautomaton(
		alphabet,
		epsilons,
    	states = [], initials = [1], finals = [4,5],
    	transitions=[(1,'a',2), (6,'b',2), (2,'b',3), (4,'0',6), (3,'a',4), (4,'b',5)]
	)
#a.display("Avant union", False)
a.display("Avant union", False)
a.union(b)
#a.display("Apres completer")
