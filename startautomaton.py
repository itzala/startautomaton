from automaton import *
from queue import *
	

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

	def lister_etats_indetermines(self, etat):
		liste = []
		for l in self.get_alphabet():
			tmp = self._delta(l, [etat])
			if (len(tmp) > 1):
				for e in tmp:
					liste.append(e)
		return liste


	def regrouper_etats(self, liste_etats):
		nouvel_etat = self.get_maximal_id() + 1

		# # Les etats sont-ils initiaux ou finaux ?
		# # Si oui alors on ajoute le nouvel etat dans les correspondants et on supprime le parent des correspondants
		# for e in liste_etats: 
		# 	if (e in self.get_initial_states()):
		# 		self.add_initial_state(nouvel_etat)
		# 		remove_initial_state(e)
		# 	if (e in self.get_final_states()):
		# 		self.add_final_state(nouvel_etat)
		# 		remove_final_state(e)

		for e in self.get_states():
			for a in self.get_alphabet():
				if(e in liste_etats):
					for fin in self._delta(a, [e]):
						if(not fin in liste_etats):
							self.add_transition((nouvel_etat, a, fin))
						else:
							self.add_transition((nouvel_etat, a, nouvel_etat))
						self.remove_transition((e,a,fin))

				tmp = self._delta(a, [e])
				for successeur in tmp:
					if (successeur in liste_etats):
						self.add_transition( (e, a, nouvel_etat) )
						self.remove_transition( (e,a, successeur) )
		return nouvel_etat


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

	def has_epsilon_transition_etat(self, etat):

		for espi in self.get_epsilons():
			if not self._delta(espi, [etat]) == pretty_set():
				return True

		return False			

	def suppression_epsilon_transition(self):
		for e in self.get_states():
			self.suppression_epsilon_transition_etat(e)
			

	def suppression_epsilon_transition_etat(self, etat):
		for l in self.get_alphabet():
			for suc in self._delta(l, [etat]):
				for ep in self.get_epsilons():
					for petit_fils in self._delta(ep, [suc]):
						add_transition(etat, l, petit_fils)
						remove_transition( (suc, ep, petit_fils) )
	
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
		erase_q1 = True
		q1,lettre,q2 = transition
		if((q1, lettre) in self._adjacence):
			if q2 in self._adjacence[(q1, lettre)]:
				self._adjacence[(q1, lettre)].remove(q2)
		for a in self.get_alphabet():
			if(erase_q1 and self._delta(a, [q1]) != set()):
				erase_q1 = False
			if(not(erase_q1)):
				break
		if(erase_q1):
			self._states.remove(q1)

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

		# for a in self.get_alphabet():
		#	 print(a)
		#	 print(self.delta(a))

		for e in self.get_states() :
			for a in self.get_alphabet() :
				if self._delta(a, [e]) != pretty_set():
					self.add_transition( (e, a, etat_puit) )

		return self

	def minimiser(self):
		return self

	def determinisation(self):
		"""
		1/ récupérer les états initiaux en un ensemble
		2/ déterminiser cet ensemble et enfiler les nouveaux états
		3/ récursif tant que file non vide


		"""
		liste_initiaux = []
		for e in self.get_initial_states():
			liste_initiaux.append(e)

		file_etats = Queue()
		initial = self.regrouper_etats(liste_initiaux)
		self.add_initial_state(initial)
		file_etats.put(initial)
		etats_finaux = self.get_final_states()
		while not file_etats.empty():
			etat_courant = file_etats.get()									# Je recupere letat a traiter
			etats_indetermines = self.lister_etats_indetermines(etat_courant)	# Je recupere les liste des etats suivants a regrouper
			final = False
			for e in etats_indetermines :									# Je definis si letat obtenu de la fusion doit etre final
				if e in etats_finaux:
					final = True
					break
			tmp = self.regrouper_etats(etats_indetermines)
			if final:
				self.add_final_state(tmp)

			for l in self.get_alphabet():									# Je rajoute les etats suivants au traitement
				for e in self._delta(l, [etat_courant]):
					if e != etat_courant:
						file_etats.put(e)
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
			self.regrouper_etats([0,1,2])

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

	def express_to_auto(self):
		return self

# Main pour tester

if __name__ == "__main__":
	alphabet = ['a', 'b']
	epsilons = []
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
a.display("Avant regroup", False)
a.determinisation()
a.display("Apres regroup1")

"""
print("L'automate a est déterministe : " + str(a.est_deterministe()))
print("L'automate a est complet : " + str(a.est_complet()))
print("L'automate b est déterministe : " + str(b.est_deterministe()))
print("L'automate b est complet : " + str(b.est_complet()))
"""
