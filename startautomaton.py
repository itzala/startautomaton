from automaton import *
from collections import deque
	

def get_origine_trans(transition):
	"""
	Fonction qui retourne l'état d'origine de la transition

	Exemple 
	>>>	get_origine_trans((0, 'a', 1)) == "0"
	>>>	True
	"""
	origin, lettre, fin = transition
	return origin


def get_fin_trans(transition):
	"""
	Fonction qui retourne l'état sur lequel arrive la transition

	Exemple 
	>>>	get_fin_trans((0, 'a', 1)) == "1"
	>>>	True
	"""
	origin, lettre, fin = transition
	return fin


def renverser_tuple(transition):	
	"""
	Fonction qui permet de renverser une transition. L'état d'origine devient l'état qui reçoit la transition et vice-versa.

	Exemple 
	>>>	renverser_tuple((0, 'a', 1)) == (1, 'a', 0)
	>>>	True
	"""
	origin, lettre, fin = transition
	return (fin, lettre, origin)


class startautomaton(automaton):
	"""
	Cette classe hérite de la classe automaton définie dans la bibliothèque automaton.py. Elle ajoute plusieurs fonctionnalités
	parmi lesquelles la complétion, la déterminisation, la minimisation, l'union, l'intersection. L'héritage nous permet de bénéficier
	de toutes les fonctionnalités développées dans la bibliothèque
	"""

# Constructeur

	def __init__(self, alphabet=None, epsilons=None, states=None, initials=None, finals=None, 
		transitions=None, deterministe=False, complet=False):
		"""
		Construit l'automate et permet de définir deux champs _est_complet et _est_deterministe.
		Ces deux attributs permettent de savoir à tout moment si l'automate est complet ou déterministe. Il sont mis à jour par
		les méthodes modifiant l'automate
		"""
		automaton.__init__(self, alphabet, epsilons, states, initials, finals, transitions)
		self._est_complet = complet
		self._est_deterministe = deterministe

	def reconstruction(self, aut2):
		"""
		Reconstruit l'automate à partir d'un deuxième
		"""
		self.__init__(aut2.get_alphabet(), aut2.get_epsilons(),
				aut2.get_states(), aut2.get_initial_states(),
				aut2.get_final_states(), aut2.get_transitions(),
				aut2._est_deterministe, aut2._est_complet)


# Fonctions utilitaires

	def print_alphabet(self):
		"""
		Affiche l'alphabet de l'automate
		"""
		print("Affichage de l'alphabet : ")
		print(self.get_alphabet())			

	def print_transitions(self):
		"""
		Affiche l'ensemble des transitions de l'automate
		"""
		print("Liste des transitions de l'automate : ")
		print(self.get_transitions())

	def print_etats(self):
		"""
		Affiche les différents états de l'automate
		"""
		print("Liste des etats de l'automate : ")
		print(self.get_states())

	def print_epsilons(self):
		"""
		Affiche les caractères représentant une epsilon transition
		"""
		print("Liste des caracteres representant une epsilon transition : ")
		print(self.get_epsilons())

	def print_etats_finaux(self):
		"""
		Affiche les états finaux de l'automate
		"""
		print("Liste des etats finaux de l'automate : ")
		print(self.get_final_states())

	def print_etats_initiaux(self):
		"""
		Affiche les états initiaux de l'automate
		"""
		print("Liste des etats initiaux de l'automate : ")
		print(self.get_initial_states())

	def get_epsilon_transitions(self):
		"""
		Retourne la liste des epsilon transitions de l'automate
		"""
		liste = []
		for e in self.get_states():								# Pour tous les etats
			for eps in self.get_epsilons():						# Pour tous les caracteres representant epsilon
				if (e, eps) in self._adjacence:					# Il nous faut une transition
					for dest in self._adjacence[(e, eps)]:
						liste.append((e, eps, dest))
		return liste


	def est_deterministe(self):
		"""
		Renvoie Vrai si l'automate est déterministe et Faux sinon. Met à jour l'attribut _est_deterministe		
		"""
		res = True
		for e in self.get_states():				
			for l in self.get_alphabet():				
				if len(self._delta(l, [e])) > 1:
					res = False
					break
			if not res:
				break

		self._est_deterministe = res

		return res

	def est_complet(self):
		"""
		Renvoie Vrai si l'automate est complet et Faux sinon. Met à jour l'attribut _est_complet
		"""	
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
		"""
		Supprime les epsilon transitions de l'automate. Les transitions adéquates sont ajoutées pour conserver le même langage
		"""
		for origin in self.get_states():
			for l in self.get_alphabet():
				for e in self.delta(l, [origin]):
					self.add_transition((origin, l, e))
		for e in self.get_states():
			for removable in self.get_epsilon_transitions():
				self.remove_transition(removable)
	
	def remove_initial_states(self):
		"""
		Supprime les états initiaux
		"""
		self._initial_states = set()

	def remove_final_states(self):
		"""
		Supprime les états finaux
		"""
		self._final_states = set()

	def remove_transitions(self):
		"""
		Supprime l'ensemble des transitions d'un automate
		"""
		self._adjacence.clear()

	def remove_initial_state(self, state):
		"""
		Supprime de l'automate l'état initial passé en paramètre
		"""
		self._initial_states.remove(state)

	def remove_final_state(self, state):
		"""
		Supprime de l'automate l'état final passé en paramètre
		"""
		self._final_states.remove(state)

	def remove_transition(self, transition):
		"""
		Supprime de l'automate la transition passée en paramètre
		"""
		q1,lettre,q2 = transition
		if (q1, lettre) in self._adjacence:
			if q2 in self._adjacence[(q1, lettre)]:
				self._adjacence[(q1, lettre)].remove(q2)

	def remove_epsilons(self):
		"""
		Supprime les caractères encodant les epsilon transitions.
		"""
		super(startautomaton, self).remove_epsilon_transitions()

# Fonctions pour gérer les différentes actions sur l'automate

	def completer(self, destructif=False):
		"""
		Renvoie l'automate complete. Le paramètre "destructif" rend destructive la méthode.
		Par défaut, la méthode ne modifie pas l'automate
		"""
		automate_tmp = self.clone()

		# Ajout de l etat puit
		etat_puit = pretty_set([self.get_maximal_id() + 1])
		automate_tmp.add_state(etat_puit)

		for e in self.get_states() :
			for a in self.get_alphabet() :
				if not a in self.get_epsilons() and self._delta(a, [e]) == pretty_set():
					automate_tmp.add_transition( (e, a, etat_puit) )

		self._est_complet = True
		self.est_deterministe()

		if destructif:
			automate_clone.reconstruction(automate_tmp)
			

		return automate_tmp

	def minimiser(self, destructif=False):
		"""
		Renvoie l'automate minimal. Le paramètre "destructif" rend destructive la méthode.
		Par défaut, la méthode ne modifie pas l'automate
		"""

		if destructif:
			automate_tmp = self
		else:
			automate_tmp = self.clone()

		return automate_tmp.miroir().determinisation(True).miroir().determinisation(True)

	def determinisation(self, destructif=False):
		"""
		Renvoie l'automate déterministe. Le paramètre "destructif" rend destructive la méthode.
		Par défaut, la méthode ne modifie pas l'automate
		"""		
		automate_tmp = startautomaton(
		alphabet = self.get_alphabet(),
		epsilons = self.get_epsilons())

		if destructif:
			automate_clone = self.clone()
		else:
			automate_clone = self

		automate_clone.remove_epsilon_transitions()
		finaux = automate_clone.get_final_states()											# On récupère les etats finaux

		automate_tmp.add_initial_state(pretty_set(automate_clone.get_initial_states()))		# On ajoute les etats initiaux de l'automate d'orgine

		file_etats = deque(automate_tmp.get_initial_states())						# On créé une file avec les etats initiaux

		while len(file_etats) > 0:									# Tant qu'on a des etats rajoutés a l'automate deterministe
			etat_courant = file_etats.popleft()							# On récupère l'etat a traiter

			if not isinstance(etat_courant, pretty_set):				# On en fait un set, si s'en pas déjà un (juste pour simplifier l'implémentation)
				etat_courant = set(etat_courant)

			if not etat_courant == set():								# Si ce n'est pas un etat vide
				for l in automate_clone.get_alphabet():								# Pour chaque lettre de l'alphabet
					if not l in automate_clone.get_epsilons():						# On recupere l'etat accessible par cette lettre
						nouveau = automate_clone._delta(l, etat_courant)
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
			automate_clone.reconstruction(automate_tmp)

		return automate_tmp

	def miroir(self, destructif=False):
		"""
		Renvoie l'automate miroir. Le paramètre "destructif" rend destructive la méthode.
		Par défaut, la méthode ne modifie pas l'automate
		"""	
		# Echange des etats finaux et initiaux
		automate_tmp = startautomaton(
			alphabet = self.get_alphabet(),
			epsilons = self.get_epsilons(),
			initials = self.get_final_states(),
			finals = self.get_initial_states()
		)

		# Inversion de toutes les transitions		
		for trans in self.get_transitions():
			automate_tmp.add_transition(renverser_tuple(trans))

		automate_tmp.est_deterministe()
		automate_tmp.est_complet()

		if destructif:
			self.reconstruction(automate_tmp)
			
		return automate_tmp
	
	def union(self, aut2, destructif=False):
		"""
		Calcule l'union de deux automates. Le paramètre "destructif" rend destructive la méthode sur le premier automate.
		Par défaut, la méthode ne modifie pas le premier automate
		"""
		
		assert self.get_alphabet() == aut2.get_alphabet(), "Les deux automates n'ont pas le meme alphabet"
		assert self.get_epsilons() == aut2.get_epsilons(), "Les epsilons ne sont pas encodees par les memes caracteres"

		# On travaille sur des automates deterministes
		if not aut2.est_deterministe():
			aut2 = aut2.determinisation()
			
		if not self.est_deterministe():
			self.determinisation(destructif)
		
		# On travaille sur des automates complet
		if not aut2.est_complet():
			aut2 = aut2.completer()

		if not self.est_complet():
			self.completer(destructif)		

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
						nouveau = set()
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

		if destructif:
			self.reconstruction(automate_tmp)

		return automate_tmp

	def intersection(self, aut2, destructif=False):
		"""
		Calcule l'intersection de deux automates. Le paramètre "destructif" rend destructive la méthode sur le premier automate.
		Par défaut, la méthode ne modifie pas le premier automate
		"""
		assert self.get_alphabet() == aut2.get_alphabet(), "Les deux automates n'ont pas le meme alphabet"
		assert self.get_epsilons() == aut2.get_epsilons(), "Les epsilons ne sont pas encodees par les memes caracteres"

		# On travaille sur des automates deterministes
		if not aut2.est_deterministe():
			aut2 = aut2.determinisation()
			
		if not self.est_deterministe():
			self.determinisation(destructif)
		
		# On travaille sur des automates complet
		if not aut2.est_complet():
			aut2 = aut2.completer()

		if not self.est_complet():
			self.completer(destructif)		

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
						nouveau = set()
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
		if destructif:
			self.reconstruction(automate_tmp)

		return automate_tmp

	def complement(self, destructif=False):
		"""
		Calcule le complement d'un automate. Le paramètre "destructif" rend destructive la méthode sur l'automate.
		Par défaut, la méthode ne modifie pas l'automate
		"""
		automate_tmp = self.clone()
		automate_tmp.completer()
		automate_tmp.determinisation(True)
		finaux = automate_tmp.get_states() - automate_tmp.get_final_states()

		automate_tmp.remove_final_states()
		automate_tmp.add_final_states(finaux)
		if destructif:
			self.reconstruction(automate_tmp)

		return automate_tmp

	def traiter_ou_transition(self, expression, etat_ini):
		"""
		Traite l'expression comme les paramètres d'une union :
		elle crée chacune des transitions en paramètre en reliant l'état d'origine de chaque
		nouvelle transition à l'état initial passé en paramètre.
		La fonction retourne tous les états finaux des transitions créées
		"""
		operateurs = [".", "+", "*"]
		liste_etat_finaux_sous_automate = []
		if not isinstance(expression, list):														# Si les paramètres d'une ou transition ne sont pas dans un liste
			print("Erreur : expression mal formée au niveau d'un \"+\"")							# On renvoie une erreur
			return []
		if expression[0] in operateurs:																# Si le premier élément de la liste est +, * ou .
			liste_etat_finaux_sous_automate = self.traitement_expression(expression[1], etat_ini)			# On appelle traitement_expression pour l'etat courant et la liste
		else:																						# Sinon
			for lettre in expression:																# On prend chaque élément de la liste des paramètres
				if not isinstance(lettre, list):														# Si ce n'est pas une liste
					if lettre in operateurs:														# Si c'est un +, * ou .
						print("Erreur : expression mal formée au niveau d'un \"+\"")							#On renvoie un erreur
						return []	
					etat_max = self.get_maximal_id() + 1													# Sinon
					self.add_transition((etat_ini, lettre, etat_max))											# On fait une transition depuis l'etat courant vers un nouvel etat par la lettre traitée
					liste_etat_finaux_sous_automate += [etat_max] 												# Et on ajoute ce nouvel etat à la liste des etats finaux de ce sous-automate
				else:																					# Sinon
					liste_etat_finaux_sous_automate += self.traitement_expression(lettre, etat_ini)			# On appelle traitement_expression pour l'état courant avec la liste à traiter
																											# Et on ajoute les etats renvoyés par celle-ci aux etats finaux du sous-automate		
		return liste_etat_finaux_sous_automate 														# On retourne les etats finaux du sous-automate

	def traiter_etoile_transition(self, expression, etat_ini):
		"""
		Traite l'expression comme les paramètres d'une répétition :
		elle crée chacune des transitions en paramètre en reliant l'état d'arrivée de chaque
		nouvelle transition à l'état initial passé en paramètre.
		La fonction retourne l'état initial
		"""
		operateurs = [".", "+", "*"]
		liste_etat_finaux_sous_automate = []
		if not isinstance(expression, list):															# Si les paramètres ne sont pas dans une liste
			if expression in operateurs:																	# Si le paramètre est un  +, * ou .
				print("Erreur : expression mal formée au niveau d'un \"*\"")									# On renvoie une erreur
				return []
			print((etat_ini, expression, etat_ini))
			self.add_transition((etat_ini, expression, etat_ini))											# Sinon on créé une boucle sur l'état courant
			liste_etat_finaux_sous_automate = [etat_ini]													# Et on défini cet état comme l'état final du sous-automate
		else:																							# Sinon (on a une liste)
			if expression[0] in operateurs:																	# Si le premier élément est un  +, * ou .
				liste_etat_finaux_sous_automate = self.traitement_expression(expression, etat_ini)				# On stocke les états finaux du sous-automate créé dans cette liste
			else:																							# Sinon
				for lettre in expression:																		# Pour chaque élément de la liste
					if isinstance(lettre, list):																	# Si c'est une liste
						liste_etat_finaux_sous_automate += self.traitement_expression(lettre, etat_ini)					# On stocke les etat finaux du sous-automate de cette liste
					else:																							# Sinon
						if lettre in operateurs:																# Si c'est un +, * ou .
							print("Erreur : expression mal formée au niveau d'un \"+\"")									#On renvoie un erreur
							return []
						self.add_transition((etat_ini, lettre, etat_ini))												# Sinon on crée une boucle sur l'état courant avec la lettre obtenue
			for etat in liste_etat_finaux_sous_automate:													# Pour chaque état final
				self.add_transition((etat, "etoile", etat_ini))													# On ajoute une epsilon transition vers l'etat courant
		return [etat_ini]																				# On retourne l'état traité					

	def traiter_concat_transition(self, expression, etat_ini):
		"""
		Traite l'expression comme les paramètres d'une concaténation :
		elle crée chacune des transitions en paramètre en reliant l'état d'origine de chaque(s)
		nouvelle(s) transition(s) à l'état d'arrivée de(s) la précedente(s).
		La première transition se fait de l'état initial passé en paramère vers un nouvel état.
		La fonction renvoie les états finaux de(s) la transition(s) ainsi créés
		"""
		liste_etat_finaux_sous_automate = [etat_ini]
		if not isinstance(expression, list):															# Si il n'y a qu'un seul paramètre
			print("Erreur : expression mal formée au niveau d'un \"*\"")									# On renvoie une erreur
			return []
		for param in expression:																		# Pour chacun des paramètres
			if not isinstance(expression, list):															# Si le paramètre n'est pas une liste
				print("Erreur : expression mal formée au niveau d'un \"*\"")									# On renvoie une erreur
				return []
			etats_courants = liste_etat_finaux_sous_automate
			liste_etat_finaux_sous_automate = []															# On stocke les précédents états traités
			for courant in etats_courants:																	# Pour tous les états stockés
				liste_etat_finaux_sous_automate += self.traitement_expression(param, courant)					# On appelle traitement_expr, pour concaténer le paramètre suivant à tous les états traités
																												# On ajoute les états renvoyés par traitement_expression
		return liste_etat_finaux_sous_automate 															# On retourne les derniers états créés


	def traitement_expression(self, expression, etat_ini=0):
		"""
		Détecte les opérateurs dans une expression et appelle les méthodes nécessaires 
		pour traiter les paramètres de cet opérateur.
		Pour chaque élément de la liste qui n'est pas un opérateur ou un paramètre d'opérateur,
		cette méthode ajoute une transition de l'etat initial passé en paramètre vers un nouvel
		état, par l'élément lu
		"""
		liste_etat_finaux_sous_automate = []
		etat_max = self.get_maximal_id() + 1
		if not isinstance(expression, list):
			self.add_transition((etat_ini, expression, etat_max))
			liste_etat_finaux_sous_automate = [etat_max]
		elif expression[0] == "+":
			if len(expression) > 2:
				print("Erreur : expression \"+\" mal formée")
				return []
			self.add_transition((etat_ini, "plus", etat_max))
			liste_etat_finaux_sous_automate = self.traiter_ou_transition(expression[1], etat_max)
		elif expression[0] == "*":
			if len(expression) > 2:
				print("Erreur : expression \"*\" mal formée")
				return []
			liste_etat_finaux_sous_automate = self.traiter_etoile_transition(expression[1], etat_ini)
		elif expression[0] == ".":
			self.add_transition((etat_ini, "concat", etat_max))
			liste_etat_finaux_sous_automate = self.traiter_concat_transition(expression[1:], etat_max)
		else:
			for e in expression:
				if isinstance(e, list):
					liste_etat_finaux_sous_automate += self.traitement_expression(e, etat_ini)
				else:
					self.add_transition((etat_ini, e, etat_max))
					liste_etat_finaux_sous_automate += [etat_max]
					etat_max = self.get_maximal_id() + 1
		return liste_etat_finaux_sous_automate
	
	@staticmethod
	def express_to_auto(expression):
		"""
		Construit correspondant à l'expression préfixée passée en paramètre
		"""
		transitions_operateurs = ["concat", "plus", "etoile"]
		automate_tmp = startautomaton(
			initials =[0],
			epsilons = transitions_operateurs
			)
		automate_tmp.add_final_states(automate_tmp.traitement_expression(expression))
		automate_tmp.reconstruction(automate_tmp.minimiser(True))
		automate_tmp.renumber_the_states()
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

a.display("Voici l'automate A", False)
a.print_alphabet()
a.print_epsilons()
a.print_etats()
a.print_etats_initiaux()
a.print_etats_finaux()
a.print_transitions()

print("L'automate a est-il deterministe ?\n", a.est_deterministe())

print("L'automate A est-il complet ?\n", a.est_complet())

tmp = a.clone()
tmp.remove_epsilons()
tmp.print_epsilons()
tmp.display("L'automate A sans caracteres epsilon")

tmp = a.clone()
tmp.remove_initial_states()
tmp.print_etats_initiaux()
tmp.display("L'automate A sans etats initiaux")

tmp = a.clone()
tmp.remove_final_states()
tmp.print_etats_finaux()
tmp.display("L'automate A sans etats finaux")

tmp = a.clone()
tmp.remove_transitions()
tmp.print_transitions()
tmp.display("L'automate A sans transitions")

tmp = a.clone()
tmp.remove_epsilon_transitions()
tmp.print_epsilons()
tmp.display("L'automate A sans transitions epsilon")


a.completer(False).display("L'automate A complet", False)
a.determinisation(False).display("L'automate A determinise")
a.miroir(False).display("Le miroir de l'automate A", False)
a.minimiser(False).display("L'automate A minimise")
a.complement(False).display("Complement de A")

a.display("Revoici l'automate A", False)
b.display("Voici l'automate B", False)

a.union(b, False).display("Voici l'union de A et B")
a.display("Revoici l'automate A", False)
b.display("Revoici l'automate B", False)
a.intersection(b, False).display("Voici l'intersection de A et B")

expression = "aa(a + ab)* b"
expression_prefixee = [".", 
				["a"], 
				["a"], 
				["*",  
					["+", 
						[ "a", 	[".", 
									["a"], 
									["b"] 
								] 
						] 
					] 
				], 
				["b"] 
			]

print("Et pour finir, l'automate minimal de l'expression : ", expression)
startautomaton.express_to_auto(expression_prefixee).display()

print("FIN !")