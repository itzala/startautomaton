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
		for e in self.get_states():					# Pour tous les etats
			for eps in self.get_epsilons():			# Pour tous les caracteres representant epsilon
				if (e, eps) in self._adjacence:		# Il nous faut une transition
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

	def lister_etats_indetermines(self, etat):
		liste = []
		for l in self.get_alphabet():					# pour chaque lettre de l'alphabet
			tmp = self._delta(l, [etat])				
			if (len(tmp) > 1):							# si plusieurs etats sont accessibles
				for e in tmp:
					liste.append(e)						# alors on les rajoute à la liste

		return liste 									# on retourne la liste ainsi formee

	# def copier_regroupement_etats(self, automate_origine, liste_etats):
	# 	nouvel_etat = pretty_set(liste_etats)

	# 	for e in self.get_states():
	# 		for l in self.get_alphabet():
	# 			if automate_origine._delta(l, [e]).symmetric_difference(nouvel_etat) == set():		# Si l'etat traite permet d'acceder a seulement les etats regroupes
	# 				self.add_transition(e, l, nouvel_etat)											# alors on ajoute une transition de cet etat vers l'etat regroupe
	# 				pass
	# 			if e in automate_origine._delta(l, [nouvel_etat])


	# def regrouper_etats(self, liste_etats):
	# 	nouvel_etat = pretty_set(liste_etats)							# On nomme le nouvel etat
	# 	for e in self.get_states():
	# 		for a in self.get_alphabet():
	# 			tmp = self._delta(a, [e])
	# 			if e in liste_etats:									# Pour chacun des etats à regrouper
	# 				for fin in tmp:						
	# 					if not fin in liste_etats:								# On rajoute une transition partant l'etat a regrouper
	# 						self.add_transition((nouvel_etat, a, fin))			# cas : on a (1, 'a', 2) donc ({0,1} , 'a', 2)
	# 					else:
	# 						self.add_transition((nouvel_etat, a, nouvel_etat))	# cas : on a (1, 'a' 0) donc ({0,1}, 'a', {0,1})
	# 																			# cas 2 : on a (1, 'a', 1) donc ({0,1}, 'a', {0,1})

	# 					self.remove_transition((e,a,fin))						# On efface l'ancienne transition
	# 			elif not (nouvel_etat == pretty_set()) and  tmp.issuperset(nouvel_etat):					# si tous les etats regroupes sont accessibles
	# 				print(nouvel_etat)
	# 				print(self._delta(a, [e]))
	# 				print(self._delta(a, [e]).issuperset(nouvel_etat))
	# 				print("toto\n")
	# 				self.add_transition( (e, a, nouvel_etat) )						# alors une transition de cet etat vers le nouvel etat
	# 				for successeur in self._delta(a, [e]):
	# 					self.remove_transition( (e, a, successeur) )					# et on efface les anciennes transitions
		
		# return nouvel_etat

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

	def determinisation_mew(self):				# Fuck la police !
		automate_tmp = startautomaton(
		alphabet = self.get_alphabet(),
		epsilons = self.get_epsilons())

		self.remove_epsilon_transitions()

		automate_tmp.add_initial_state(pretty_set(self.get_initial_states()))

		file_etats = deque(automate_tmp.get_initial_states())

		while len(file_etats) > 0:
			etat_courant = file_etats.popleft()

			if not isinstance(etat_courant, pretty_set):
				etat_courant = set(etat_courant)

			for l in self.get_alphabet():
				if not l in self.get_epsilons():
					nouveau = self._delta(l, etat_courant)
					if not nouveau in automate_tmp.get_states():
						file_etats.append(nouveau)
					automate_tmp.add_transition((etat_courant, l, nouveau))




		



	def determinisation(self):
		self.remove_epsilon_transitions()
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
					if e != etat_courant:	# puisque tu fais le delta, e sera forcement different de etat_courant, non ?
						file_etats.put(e)




		# if not self.est_complet():
		# 	self.completer()
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
	epsilons = ['0']
	a = startautomaton(
		alphabet,
		epsilons,
		states = [], initials = [0,1], finals = [3,4],
		transitions=[(0,'a', 1), (1, 'b', 2), (2, 'b', 2), (2, 'b', 3), (2, 'a', 5), (3, 'a', 1), (3, 'a', 4), (4, 'b', 3), (5, 'b', 4), (5, 'b', 1)]
	)

"""
	Si problème avec l'affichage des labels
	=> http://superuser.com/questions/334625/dotty-shows-all-labels-as-dots-period-instead-of-text
"""
a.display("Avant", False)
a.determinisation()
a.display("Apres", False)

"""
(0 'a' {1,2}) (5 'a' 2) ==> (0 'a' {1,2}) (5 'a' {1,2}) ?
"""