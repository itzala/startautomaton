from automaton import *
from collections import deque
from operator import itemgetter
	

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
		transitions=None, deterministe=False, complet=False):
		automaton.__init__(self, alphabet, epsilons, states, initials, finals, transitions)
		self._est_complet = complet
		self._est_deterministe = deterministe

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

		self._est_complet = res

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

		self._est_complet = True

		return self

	def minimiser(self, destructif=False):
		automate_tmp = startautomaton(
		alphabet = self.get_alphabet(),
		epsilons = self.get_epsilons())

		"""
		Si aucun etat n'est accessible ou si plusieurs etats sont accessibles, alors il y a un pb dans l'algo !
		"""


		if not self.est_deterministe():						# On vérifie que l'automate est deterministe
			self.determinisation(True)
		if not self.est_complet():							# Et complet
			self.completer()

		if self._est_deterministe:
			liste_etats = {}												# On cree un dictionnaire de listes avec comme clef un etat de l'automate
			alphabet_courant = self.get_alphabet() - self.get_epsilons()
			n_etat, code_etat = 0											# La liste aura deux éléments : le numero de l'etat et l'entier qui code son numero et ses transitions (voir algo)
			for e in self.get_states():										# On commence par initialiser tous les numeros d'etat à 1 ou 0 si ils sont finaux ou pas
				n_etat = 0
				if e in self.get_final_states():
					n_etat += 1
				liste_etats[e] = [n_etat, n_etat]
			for e in self.get_states:											# Ensuite on s'occupe de l'encodage
				code_etat = liste_etats[e][0]									# On initialise l'entier avec la valeur de l'etat
				for l in alphabet_courant:
					for delta in self._delta(l, e):
						code_etat *= pow(10, len(str(liste_etats[delta][0])))	# On ajoute le numero de l'etat accessible pour chaque transition
						code_etat += liste_etats[delta][0]
				liste_etats[e][1] = code_etat									# On sauvegarde l'entier


			stabilise = False
			while not stabilise:
				stabilise = True

				liste_triee = []												# On trie la liste des codes des etats
				for etat, (numero, code) in liste_etats.items():
					liste_triee.append(etat, code)
				liste_triee = sorted(liste_triee, key=itemgetter(1), reverse=True)

				for i in len(liste_triee):										# On change le numéro des etats pour leur affecter leur ordre lexicographique
					liste_etats[liste_triee[i][0]][0] = i+1

				for e in self.get_states:											# Ensuite on s'occupe de l'encodage
					code_etat = liste_etats[e][0]									# On initialise l'entier avec la valeur de l'etat
					for l in alphabet_courant:
						for delta in self._delta(l, e):
							code_etat *= pow(10, len(str(liste_etats[delta][0])))	# On ajoute le numero de l'etat accessible pour chaque transition
							code_etat += liste_etats[delta][0]
					if code_etat != liste_etats[e][1]: 								# Si l'entier est le même que le précedement calculé, on continue l'algo
						stabilise = False
						liste_etats[e][1] = code_etat								# Et on sauvegarde le nouvel entier



			"""
			Construction de l'automate a partir du resultat de l'ago precedent
			"""


			return automate_tmp 							# Si tout c'est bien passe on renvoie l'automate minimisé
		else:
			return self 									# Sinon on retourne l'automate d'origine

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
			self._est_deterministe = False
			return self

		automate_tmp.est_complet()

		automate_tmp._est_deterministe = True

		if destructif:
			self.__init__(automate_tmp.get_alphabet(), automate_tmp.get_epsilons(),
				automate_tmp.get_states(), automate_tmp.get_initial_states(),
				automate_tmp.get_final_states(), automate_tmp.get_transitions(),
				automate_tmp._est_deterministe, automate_tmp._est_complet)

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
				aut2.determinisation(True).display("aut2 = B deterministe", False)
				assert aut2._est_deterministe, "aut2 = B n'est pas deterministe"
				
			if not self.est_deterministe():
				self.determinisation(True).display("A deterministe", False)
				assert self._est_deterministe, "A n'est pas deterministe"
			
			# On travaille sur des automates complet
			if not aut2.est_complet():
				aut2.completer()

			if not self.est_complet():
				self.completer()		

			automate_tmp = startautomaton(
				alphabet = self.get_alphabet(),
				epsilons = self.get_epsilons())
			finaux = (self.get_final_states()).union(aut2.get_final_states())
			
			# Création états initiaux de l'automate de l'union

			pile_etats = []

			etat_1 , etat_2 = 0 , 0
			for ini_1 in self.get_initial_states():
				for ini_2 in aut2.get_initial_states():
					etat = (ini_1, ini_2)
					etat_1 = ini_1
					etat_2 = ini_2
					automate_tmp.add_initial_state(etat)
					pile_etats.append(etat)

			# Création de l'automate des couples (automate de l'union)
			while len(pile_etats) > 0:
				etat_courant = pile_etats.pop()
				if not etat_courant == set():
					etat_1, etat_2 = etat_courant
					for l in self.get_alphabet():
						if not l in self.get_epsilons():
							delta_etat_1 = self._delta(l, [etat_1])
							delta_etat_2 =  aut2._delta(l, [etat_2])
							for e1 in delta_etat_1:
								for e2 in delta_etat_2:
									nouveau = (e1,e2)
							
							if not nouveau == set():
								if not nouveau in automate_tmp.get_states():
									pile_etats.append(nouveau)
								for e in nouveau:								
									if e in finaux:
										automate_tmp.add_final_state(nouveau)
										break

								automate_tmp.add_transition((etat_courant, l, nouveau))


			return automate_tmp
		else:
			return None

	def intersection(self, aut2):

		if self.get_alphabet() == aut2.get_alphabet():
			# On travaille sur des automates deterministes
			if not aut2.est_deterministe():
				aut2.determinisation(True).display("aut2 = B deterministe", False)
				assert aut2._est_deterministe, "aut2 = B n'est pas deterministe"
				
			if not self.est_deterministe():
				self.determinisation(True).display("A deterministe", False)
				assert self._est_deterministe, "A n'est pas deterministe"
			
			# On travaille sur des automates complet
			if not aut2.est_complet():
				aut2.completer()

			if not self.est_complet():
				self.completer()		

			automate_tmp = startautomaton(
				alphabet = self.get_alphabet(),
				epsilons = self.get_epsilons())
			finaux = (self.get_final_states()).union(aut2.get_final_states())
			
			# Création états initiaux de l'automate de l'union

			pile_etats = []

			etat_1 , etat_2 = 0 , 0
			for ini_1 in self.get_initial_states():
				for ini_2 in aut2.get_initial_states():
					etat = (ini_1, ini_2)
					etat_1 = ini_1
					etat_2 = ini_2
					automate_tmp.add_initial_state(etat)
					pile_etats.append(etat)

			# Création de l'automate des couples (automate de l'union)
			while len(pile_etats) > 0:
				etat_courant = pile_etats.pop()
				if not etat_courant == set():
					etat_1, etat_2 = etat_courant
					for l in self.get_alphabet():
						if not l in self.get_epsilons():
							delta_etat_1 = self._delta(l, [etat_1])
							delta_etat_2 =  aut2._delta(l, [etat_2])
							for e1 in delta_etat_1:
								for e2 in delta_etat_2:
									nouveau = (e1,e2)
							
							if not nouveau == set():
								if not nouveau in automate_tmp.get_states():
									pile_etats.append(nouveau)
								final = True
								for e in nouveau:								
									if not e in finaux:
										final = False
										break
								if final:
									automate_tmp.add_final_state(nouveau)
								automate_tmp.add_transition((etat_courant, l, nouveau))


			return automate_tmp
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
		transitions=[(0,'a',1), (1,'b',2), (2,'b',2), (5, 'a',3), (3,'b',2), (3,'b',4), (2, 'a', 5), (4, 'a', 2)]
	)

"""
	Si problème avec l'affichage des labels
	=> http://superuser.com/questions/334625/dotty-shows-all-labels-as-dots-period-instead-of-text

(0 'a' {1,2}) (5 'a' 2) ==> (0 'a' {1,2}) (5 'a' {1,2}) ?
"""

"""
	DONE !
"""

#a.completer()
#a.miroir()
#a.remove_epsilon_transitions()
#a.determiniser()
#a.union(b)
#a.intersection(b)

"""
	TO DO
"""

a.minimiser()
#a.complement()
#express_to_auto()