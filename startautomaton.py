from automaton import *
from collections import deque
	

def get_origine_trans(transition):
	origin, lettre, fin = transition
	return origin

def get_fin_trans(transition):
	origin, lettre, fin = transition
	return fin

def renverser_tuple(transition):	
	origin, lettre, fin = transition
	return (fin, lettre, origin)

class startautomaton(automaton):

# Constructeur

	def __init__(self, alphabet=None, epsilons=None, states=None, initials=None, finals=None, 
		transitions=None):
		automaton.__init__(self, alphabet, epsilons, states, initials, finals, transitions)	

# Fonctions utilitaires

	def print_alphabet(self):
		print("Affichage de l'alphabet : ")
		for l in self.get_alphabet():
			print(l)

	def get_epsilon_transitions(self):
		liste = []
		for e in self.get_states():	# Pour tous les etats
			for eps in self.get_epsilons():	# Pour tous les caracteres representant epsilon
				if (e, eps) in self._adjacence:	# Il nous faut une transition
					for dest in self._adjacence[(e, eps)]:
						liste.append((e, eps, dest))
		return liste


	def est_deterministe(self):
		res = True
		for e in self.get_states():
			for l in self.get_alphabet():				
				if len(self._delta(l, [e])) > 1:
					res = False
					break
			if not res:
				break

		return res

	def est_complet(self):		
		res = True
		for e in self.get_states():
			for l in self.get_alphabet():				
				if self._delta(l, [e]) == pretty_set():
					res = False
					break
			if not res:
				break
		return res
	
	def remove_epsilon_transitions(self):
		for origin in self.get_states():
			for l in self.get_alphabet():
				for e in self.delta(l, [origin]):
					self.add_transition((origin, l, e))
		for e in self.get_states():
			for removable in self.get_epsilon_transitions():
				self.remove_transition(removable)
	
	def remove_initial_states(self):
		self._initial_states = set()

	def remove_final_states(self):
		self._final_states = set()

	def remove_transitions(self):
		self._adjacence.clear()

	def remove_initial_state(self, state):
		self._initial_states.remove(state)

	def remove_final_state(self, state):
		self._final_states.remove(state)

	def remove_transition(self, transition):
		q1,lettre,q2 = transition
		if (q1, lettre) in self._adjacence:
			if q2 in self._adjacence[(q1, lettre)]:
				self._adjacence[(q1, lettre)].remove(q2)

	def echanger_etats_ini_fin(self):

		ei = self._initial_states
		self.remove_initial_states()
		self.add_initial_states(self._final_states)
		self.remove_final_states()
		self.add_final_states(ei)

# Fonctions pour gérer les différentes actions sur l'automate

	def completer(self):	
		# Ajout de l etat puit :)
		etat_puit = self.get_maximal_id() + 1
		self.add_state(etat_puit)

		for e in self.get_states() :
			for a in self.get_alphabet() :
				if not a in self.get_epsilons() and self._delta(a, [e]) == pretty_set():
					self.add_transition( (e, a, etat_puit) )

		return self

	def minimiser(self):
		return self

	def determinisation(self, destructif=False):		
		automate_tmp = startautomaton(
		alphabet = self.get_alphabet(),
		epsilons = self.get_epsilons())

		self.remove_epsilon_transitions()
		finaux = self.get_final_states()

		automate_tmp.add_initial_state(pretty_set(self.get_initial_states()))

		file_etats = deque(automate_tmp.get_initial_states())

		while len(file_etats) > 0:
			etat_courant = file_etats.popleft()

			if not isinstance(etat_courant, pretty_set):
				etat_courant = set(etat_courant)

			if not etat_courant == set():
				for l in self.get_alphabet():
					if not l in self.get_epsilons():
						nouveau = self._delta(l, etat_courant)
						if not nouveau == set():
							if not nouveau in automate_tmp.get_states():
								file_etats.append(nouveau)
							for e in nouveau:								
								if e in finaux:
									automate_tmp.add_final_state(nouveau)
									break

							automate_tmp.add_transition((etat_courant, l, nouveau))

		if automate_tmp.get_final_states() == set():
			print("ERREUR : l'automate n'a pas d'état final déterminisable")
			return self

		if destructif:
			self.__init__(automate_tmp.get_alphabet(), automate_tmp.get_epsilons(),
				automate_tmp.get_states(), automate_tmp.get_initial_states(),
				automate_tmp.get_final_states(), automate_tmp.get_transitions())

		return automate_tmp

	def miroir(self):
		# Echange des etats finaux et initiaux
		self.echanger_etats_ini_fin()

		# Inversion de toutes les transitions
		tmp = self.get_transitions()
		self.remove_transitions()
		for trans in tmp:
			self.add_transition(renverser_tuple(trans))
			
		return self
	
	def union(self, aut2):

		if self.get_alphabet() == aut2.get_alphabet():
			# On travaille sur des automates deterministes
			if not aut2.est_deterministe():
				aut2.determinisation()
				aut2.renumber_the_states()

			if not self.est_deterministe():
				self.determinisation()
				self.renumber_the_states()
			
			# On travaille sur des automates complet
			if not aut2.est_complet():
				aut2.completer()

			if not self.est_complet():
				self.completer()		

			automate_tmp = startautomaton(
			alphabet = self.get_alphabet(),
			epsilons = self.get_epsilons())

			# Création états initiaux de l'automate de l'union


			etat = pretty_set((self.get_initial_states(), aut2.get_initial_states()))
			automate_tmp.add_initial_state(etat)

			# Création de l'automate des couples (automate de l'union)
			
			return automate_tmp
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

	def express_to_auto(self):
		return self

# Main pour tester

if __name__ == "__main__":
	alphabet = ['a', 'b']
	epsilons = ['0']
	a = startautomaton(
		alphabet,
		epsilons,
		states = [], initials = [0,1], finals = [3,4],
		transitions=[(0,'a',1), (1,'b',2), (2,'b',2), (2,'b',3), (3,'a',4), (4, 'a', 5), (4, 'a', 1)]
	)

	b = startautomaton(
		alphabet,
		epsilons,
		states = [], initials = [0], finals = [4],
		transitions=[(0,'a',1), (1,'b',2), (2,'b',2), (3,'b',2), (3,'b',4), (2, 'a', 5), (4, 'a', 2)]
	)

"""
	Si problème avec l'affichage des labels
	=> http://superuser.com/questions/334625/dotty-shows-all-labels-as-dots-period-instead-of-text
"""
a.display("A", False)
b.display("B", False)
b.determinisation(False).display("B deterministe")

#a.union(b).display("Apres")

"""
(0 'a' {1,2}) (5 'a' 2) ==> (0 'a' {1,2}) (5 'a' {1,2}) ?
"""