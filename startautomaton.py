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
		etat_puit = pretty_set([self.get_maximal_id() + 1])
		self.add_state(etat_puit)

		for e in self.get_states() :
			for a in self.get_alphabet() :
				if not a in self.get_epsilons() and self._delta(a, [e]) == pretty_set():
					self.add_transition( (e, a, etat_puit) )

		self._est_complet = True

		return self

	def minimiser(self, destructif=False):
		if destructif:
			automate_tmp = self
		else:
			automate_tmp = self.clone()

		return automate_tmp.miroir().determinisation(True).miroir().determinisation(True)



	def determinisation(self, destructif=False):		
		automate_tmp = startautomaton(
		alphabet = self.get_alphabet(),
		epsilons = self.get_epsilons())

		self.remove_epsilon_transitions()
		finaux = self.get_final_states()											# On récupère les etats finaux

		automate_tmp.add_initial_state(pretty_set(self.get_initial_states()))		# On ajoute les etats initiaux de l'automate d'orgine

		file_etats = deque(automate_tmp.get_initial_states())						# On créé une file avec les etats initiaux

		while len(file_etats) > 0:									# Tant qu'on a des etats rajoutés a l'automate deterministe
			etat_courant = file_etats.popleft()							# On récupère l'etat a traiter

			if not isinstance(etat_courant, pretty_set):				# On en fait un set, si s'en pas déjà un (juste pour simplifier l'implémentation)
				etat_courant = set(etat_courant)

			if not etat_courant == set():								# Si ce n'est pas un etat vide
				for l in self.get_alphabet():								# Pour chaque lettre de l'alphabet
					if not l in self.get_epsilons():						# On recupere l'etat accessible par cette lettre
						nouveau = self._delta(l, etat_courant)
						if not nouveau == set():
							if not nouveau in automate_tmp.get_states():			# Si l'etat n'a pas encore ete rajoute a l'automate deterministe, on l'enfile
								file_etats.append(nouveau)
							for e in nouveau:								
								if e in finaux:										# Si l'etat	est final dans l'automate original, alors je l'ajoute aux finaux de l'automate deterministe
									automate_tmp.add_final_state(nouveau)
									break

							automate_tmp.add_transition((etat_courant, l, nouveau))	# On rajoute l'etat et la transition depuis l'etat traite

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

	def complement(self, destructif=False):
		automate_tmp = self.clone()
		automate_tmp.completer()
		automate_tmp.determinisation(True)
		finaux = automate_tmp.get_states() - automate_tmp.get_final_states()

		automate_tmp.remove_final_states()
		automate_tmp.add_final_states(finaux)
		if destructif:
			self.automaton(automate_tmp.get_alphabet(), automate_tmp.get_epsilons(), 
				automate_tmp.get_states(), automate_tmp.get_initial_states(), automate_tmp.get_final_states(),
				automate_tmp.get_transitions())

		return automate_tmp

	def traiter_ou_transition(self, expression, etat_ini):
		etat_max = self.get_maximal_id() + 1
		liste_etat_finaux_sous_automate = []
		if isinstance(expression, list):
			if expression[0] == "+":
				if len(expression) > 2:
					print("Erreur : un \"+\" doit être suivi d'une liste et d'une seule")
					return None
				lettre = "plus"
				liste_etat_finaux_sous_automate += self.traiter_ou_transition(expression[1], etat_max)
				self.add_transition((etat_ini, lettre, etat_max))
				print((etat_ini, lettre, etat_max))

			elif expression[0] == "*":
				if len(expression) > 2:
					print("Erreur : un \"*\" doit être suivi d'une liste et d'une seule")
					return None
				lettre = "etoile"
				liste_etat_finaux_sous_automate += self.traiter_etoile_transition(expression[1], etat_max)
				self.add_transition((etat_ini, lettre, etat_max))
				print((etat_ini, lettre, etat_max))

			elif expression[0] == ".":
				lettre = "concat"
				liste_etat_finaux_sous_automate += self.traiter_concat_transition(expression[1:], etat_max)
				self.add_transition((etat_ini, lettre, etat_max))
				print((etat_ini, lettre, etat_max))

			else:
				for e in expression:
					etat_max = self.get_maximal_id()+1
					if isinstance(e, list):
						tmp = self.traitement_expression(e, etat_ini)
						liste_etat_finaux_sous_automate += [tmp]
						self.add_final_states(tmp)
					elif not e in self.get_epsilons():
						lettre = e
						self.add_transition((etat_ini, lettre, etat_max))
						print((etat_ini, lettre, etat_max))
						self.add_final_state(etat_max)
						liste_etat_finaux_sous_automate += [etat_max]
					else:
						print("Erreur : la liste de paramètres du \"+\" est mal formée")



		else:
			print("Erreur : un \"+\" doit être suivi d'une liste")
		return liste_etat_finaux_sous_automate

	def traiter_etoile_transition(self, expression, etat_ini):
		etat_max = self.get_maximal_id() + 1
		liste_etat_finaux_sous_automate = []
		if isinstance(expression, list):
			if expression[0] == "+":
				if len(expression) > 2:
					print("Erreur : un \"+\" doit être suivi d'une liste et d'une seule")
					return None
				lettre = "plus"
				liste_etat_finaux_sous_automate += self.traiter_ou_transition(expression[1], etat_max)
				self.add_transition((etat_ini, lettre, etat_max))
				print((etat_ini, lettre, etat_max))


			elif expression[0] == "*":
				if len(expression) > 2:
					print("Erreur : un \"*\" doit être suivi d'une liste et d'une seule")
					return None
				lettre = "etoile"
				liste_etat_finaux_sous_automate += self.traiter_etoile_transition(expression[1], etat_max)
				self.add_transition((etat_ini, lettre, etat_max))
				print((etat_ini, lettre, etat_max))

			elif expression[0] == ".":
				lettre = "concat"
				liste_etat_finaux_sous_automate += self.traiter_concat_transition(expression[1:], etat_max)
				self.add_transition((etat_ini, lettre, etat_max))
				print((etat_ini, lettre, etat_max))

			else:
				for e in expression:
					if isinstance(e, list):
						tmp = self.traitement_expression(e, etat_ini)
						liste_etat_finaux_sous_automate += tmp
						self.add_final_states(tmp)
					elif not e in self.get_epsilons():
						lettre = e
						self.add_transition((etat_ini, lettre, etat_ini))
						print((etat_ini, lettre, etat_max))
					else:
						print("Erreur : la liste de paramètres du \"*\" est mal formée")
						return None
				for e in liste_etat_finaux_sous_automate:
					self.add_transition((e, "etoile", etat_ini))
					print((etat_ini, "etoile", etat_max))
		elif expression in self.get_epsilons():
			print("Erreur : un \"*\" doit être suivi d'une liste")
			return None
		else:
			self.add_transition((etat_ini, expression, etat_ini))
			print((etat_ini, expression, etat_ini))
		return [etat_ini]
		

	def traiter_concat_transition(self, expression, etat_ini):
		liste_etat_finaux_sous_automate = [etat_ini]
		if isinstance(expression, list):
			for e in expression:
				if isinstance(e, list):
					for etat in liste_etat_finaux_sous_automate:
						liste_etat_finaux_sous_automate = self.traitement_expression(e, etat)
				else:
					print("Erreur : la liste de paramètres du \".\" est mal formée")
					return None
		else:
			print("Erreur : l'expression \".\" est mal formée")
			return None
		return liste_etat_finaux_sous_automate

	def traitement_expression(self, expression, etat_ini=0):
		liste_etat_finaux_sous_automate = []
		if isinstance(expression, list):
			if expression[0] in self.get_epsilons():
				if expression[0] == "+":
					if len(expression) > 2:
						print("Erreur : un \"+\" doit être suivi d'une liste et d'une seule")
						return None
					tmp = self.get_maximal_id() + 1
					self.add_transition((etat_ini, "plus", tmp))
					print((etat_ini, "plus", tmp))
					liste_etat_finaux_sous_automate += self.traiter_ou_transition(expression[1], tmp)


				elif expression[0] == "*":
					if len(expression) > 2:
						print("Erreur : un \"*\" doit être suivi d'une liste et d'une seule")
						return None
					tmp = self.get_maximal_id() + 1
					self.add_transition((etat_ini, "etoile", tmp))
					print((etat_ini, "etoile", tmp))
					liste_etat_finaux_sous_automate = self.traiter_etoile_transition(expression[1], tmp)
					for e in liste_etat_finaux_sous_automate:
						self.add_transition((e, "etoile", etat_ini))
						print((e, "etoile", etat_ini))

				elif expression[0] == ".":
					tmp = self.get_maximal_id() + 1
					self.add_transition((etat_ini, "concat", tmp))
					print((etat_ini, "concat", tmp))
					liste_etat_finaux_sous_automate = self.traiter_concat_transition(expression[1:], tmp)

				
			else:
				for e in expression:
					if not isinstance(e, list):
						tmp = self.get_maximal_id() + 1
						self.add_transition((etat_ini, e, tmp))
						print((etat_ini, e, tmp))
						liste_etat_finaux_sous_automate += [tmp]
					else:
						self.traitement_expression(e, etat_ini)
			return liste_etat_finaux_sous_automate

		else:
			print("Erreur : expression mal formée")
			return None
		"""
		Traitement des deux autres operateurs

		/!\ finaux de ou = tous les finaux créés
		/!\ finaux de concat = les finaux du dernier traitement
		/!\ finaux de étoile = l'etat d'origine
		"""

	@staticmethod
	def express_to_auto(expression):
		operateurs = [".", "concat", "+", "plus", "*", "etoile"]
		automate_tmp = startautomaton(
			initials =[0],
			epsilons = operateurs
			)

		automate_tmp.traitement_expression(expression)





		"""
		traiter(expr, etat_ini):
			if e not list:
				dernier_etat += 1
				add_transition((etat_ini, e, dernier_etat))
				etats_finaux = dernier_etat
			elif e == '+':
				etat_courant = dernier_etat +1
				etats_finaux = triter(expr[1], etat_courant)				
				add_transition((etat_ini, '+', etat_courant))


		


			return etats_finaux

		"""
		
		return automate_tmp

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
#a.determinisation()
#a.union(b)
#a.intersection(b)
#a.minimiser()
#a.complement()

"""
	TO DO
"""
expression_humain = ""
expression = ["*", ["+", ["a", [".", ["*","b"], ["a"]]]]]


startautomaton.express_to_auto(expression).display("Automate", False)
startautomaton.express_to_auto(expression).minimiser(True).display("Automate", False)