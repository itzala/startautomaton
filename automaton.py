"""
This is the "automaton" module.

This module offers a simple automaton class.

This module is not optimized and is designed for educational purposes.

"""

# Copyright (C) 2013 Adrien Boussicault, University of Bordeaux 1, France
#
#   This Library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This Library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this Library.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import tempfile
import copy
import os
import platform
import threading
import xml.etree.ElementTree as ET


class pretty_set(frozenset):
    """
    This class implements a frozen set with pretty printing function.
    """
    def __repr__(self):
        elems = list(self)
        if len(elems) == 0 :
            return "{}"
        result = "{" + str(elems[0])
        for e in elems[1:]:
            result += ", " + str(e)
        result += "}"
        return result

def _translate( obj, nb ):
    """
    This function translates recursively all the numbers contained in 
    a iterable object.

    Keyword arguments:
    obj -- the object to translate
    nb -- the translation number

    Example:

    >>> _translate( 3, 7 )
    10
    >>> _translate( (2,4), 5 )
    (7, 9)
    >>> _translate( [(1,2),[3,(4,5),set([6,7])]], 3 ) == [(4, 5), [6, (7, 8), set([9, 10])]]
    True
    >>> type( _translate( pretty_set([1,3,5]), 3 ) )
    <class '__main__.pretty_set'>
    >>> _translate( pretty_set([1,3,5]), 3 ) == pretty_set([4,6,8])
    True

    """
    def _tran( l ):
        if type(l) == int:
            return l+nb
        if type(l) == str:
            return l
        return type(l)(map( _tran, l ))
    return _tran( obj )


def _extract_maximal_id( obj ):
    """
    This function extracts recursively the maximal integer contained inside an 
    iterable object.

    Example:

    >>> _extract_maximal_id( 3 )
    3
    >>> _extract_maximal_id( (2,4) )
    4
    >>> _extract_maximal_id( [(1,2),[3,(4,5),set([6,7])]] )
    7
    >>> class A:
    ...     pass
    >>> _extract_maximal_id( A() )
    >>> _extract_maximal_id(( pretty_set([1,(9,1),5]) ))
    9

    """
    if type(obj) == int:
        return obj
    try:
        maximum = None
        for i in obj:
            val = _extract_maximal_id(i)
            if maximum == None :
                maximum = val
            elif val > maximum:
                maximum = val
        return maximum
    except:
        return None

def _extract_minimal_id( obj ):
    """
    This function extracts recursively the minimal integer contained inside an 
    iterable object.

    Example:

    >>> _extract_minimal_id( 3 )
    3
    >>> _extract_minimal_id( (2,4) )
    2
    >>> _extract_minimal_id( [(1,2),[3,(4,5),set([6,7])]] )
    1
    >>> class A:
    ...     pass
    >>> _extract_minimal_id( A() )
    >>> _extract_minimal_id(( pretty_set([1,(9,1),5]) ))
    1

    """
    if type(obj) == int:
        return obj
    try:
        minimum = None
        for i in obj:
            val = _extract_minimal_id(i)
            if minimum == None :
                minimum = val
            elif val < minimum:
                minimum = val
        return minimum
    except:
        return None


class _object_to_id:
    """
    This class is used to map objects to integers going for 1 to n.

    Example:

    >>> a = _object_to_id( )
    >>> a.add_object( (1,1) )
    >>> a.add_object( (1,2) )
    >>> a.add_object( (1,3) )
    >>> a.id( (1,3) )
    3

    """
    def __init__( self ):
        self._map = {}
        self._nb = 1
    def add_object( self, obj ):
        if not obj in self._map:
            self._map[ obj ] = self._nb
            self._nb += 1
    def id( self, obj ):
        if not obj in self._map:
            return None
        return self._map[ obj ]

def _test_is_hashable( obj, name ):
        try:
            pretty_set( [obj] )
        except:
            msg = "In automaton module, " + name + " have to be hashable."
            if type( obj ) is set:
                msg += " Use automaton.pretty_set or frozenset instead of set."
            if type( obj ) is list:
                msg += " Use tuple instead of list. For example (1,3) instead of [1,3]."
            raise Exception( msg )

class automaton:
    """
    This class implements an automaton without epsilon transition
    
    This automaton is defined by the 6-uple <A, E, Q, I, F, T> where 
    A is an alphabet;
    E is a subset of A containing all the epsilon transitions 
    Q is the set of states;
    I is a subset of Q and is the set of initial states;
    F is a subset of Q and is the set of final states;
    T is a subset of Q X A X Q, and is the set of transitions.
    """
    def __init__(
        self, alphabet=None, epsilons=None, states=None, initials=None, finals=None, 
        transitions=None
    ):
        """
        The constructor of the automaton class

        During the construction, if a state (resp. a character) doesn't exist,
        the state (resp. character) is automatically added in the list of 
        states (resp. alphabet).
        
        Keyword arguments:
        alphabet -- the alphabet [default=None]
                    this argument has to contain a set of hashable objects
        epsilon characters -- the list of epsilon characters [default=None]
                              this argument has to contain a list of hashable 
                              objects
        states -- the list of states  [default=None]
                  this argument has to contain a list of hashable objects
        initals -- the list of initial states [default = None]
                   this argument has to contain a list of hashable objects
        finals -- the list of final states [default = None]
                   this argument has to contain a list of hashable objects
        transitions -- the list of transitions. [default = None]
                       a transition has to be encoded by a tuple (q1, c, q2)
                       where q1 and q2 are states and c is a character. 

        Example:

        >>> a = automaton(
        ...     alphabet = ['d'], states  = [4],
        ...     initials = [0,2], finals = [1,3],
        ...     transitions = [ (0,'a',0), (0,'b',1), (1,'c',1) ]
        ... )
        >>> a.get_alphabet() == set(['a', 'b', 'c', 'd'])
        True
        >>> a.get_states() == set( [0,1,2,3,4] )
        True
        >>> a.get_initial_states() == set( [0,2] )
        True
        >>> a.get_final_states() == set( [1,3] )
        True
        >>> a.get_transitions() == set( [(0,'a',0), (0,'b',1), (1,'c',1)] )
        True
        >>> b = automaton(
        ...     transitions = [
        ...         ( (1,2), 'a', (1,3) ),
        ...         ( (1,2), 'b', (4,5) ),
        ...         ( (4,5), 'a', (1,3) )
        ...     ]
        ... )
        >>> b.get_states() == set( [(1,2), (4,5), (1,3)] )
        True
        """
        self._epsilons = set()
        self._states = set( )
        self._adjacence = {}
        self._initial_states = set( )
        self._final_states = set( )
        self._alphabet = set( )
        if alphabet != None:
            self.add_characters( alphabet )
        if epsilons != None :
            self.add_epsilon_characters( epsilons )
        if states != None:
            self.add_states( states )
        if transitions != None:
            self.add_transitions( transitions )
        if initials != None:
            self.add_initial_states( initials )
        if finals != None:
            self.add_final_states( finals )



    def get_maximal_id( self ):
        """
        Returns the maximal integer present among all the states
        
        Example:

        >>> b = automaton(
        ...     transitions = [
        ...         ( (pretty_set([-1,11]), 2), 'a', (1,9) ),
        ...         ( (pretty_set([-1,11]), 2), 'b', (4,5) ),
        ...         ( (4,5), 'a', (1,9) )
        ...     ]
        ... )
        >>> b.get_maximal_id()
        11
        """
        return _extract_maximal_id(self._states)

    def get_minimal_id( self ):
        """
        Returns the minimal integer present among all the states
        
        Example:

        >>> b = automaton(
        ...     transitions = [
        ...         ( (pretty_set([-1,11]), 2), 'a', (1,9) ),
        ...         ( (pretty_set([-1,11]), 2), 'b', (4,5) ),
        ...         ( (4,5), 'a', (1,9) )
        ...     ]
        ... )
        >>> b.get_minimal_id()
        -1
        """
        return _extract_minimal_id(self._states)
    def has_epsilon_characters( self ):
        """
        Returns True if automaton has epsilon character.

        Example:

        >>> automaton().has_epsilon_characters()
        False
        >>> automaton( epsilons=['0'] ).has_epsilon_characters()
        True
        """
        return len( self._epsilons ) > 0

    def get_epsilons( self ):
        """
        Returns the set of epsilon characters

        Example:

        >>> automaton().get_epsilons()
        {}
        """
        return pretty_set( self._epsilons )

    def translate( self, nb ):
        """
        Recursively translates all integers present in the states by ``nb``

        Example:

        >>> b = automaton(
        ...     transitions = [
        ...         ( (pretty_set([-1,11]), 2), 'a', (1,'a') ),
        ...         ( (pretty_set([-1,11]), 2), 'b', (4,5) ),
        ...         ( (4,5), 'a', (1,'a') )
        ...     ]
        ... )
        >>> b.translate( 3 )
        >>> b.get_states() == set( [
        ...     (pretty_set([2,14]), 5),
        ...     (4,'a'),
        ...     (7,8) 
        ... ] )
        True

        """
        self._states = _translate( self._states, nb )
        tmp = {}
        for e in self._adjacence:
            tmp[ _translate(e,nb) ] = _translate(
                self._adjacence[e], nb
            )
        self._adjacence = tmp
        self._final_states = _translate(
            self._final_states, nb
        )
        self._initial_states = _translate(
            self._initial_states, nb
        )

    def map( self, f ):
        """
        For each state s, this function subtitutes s by f(s) in the automaton.

        Keyword arguments:
        f -- a map from the set of states to itself.

        Example:
        >>> def parity( obj ):
        ...    return obj%2
        >>> a = automaton(
        ...     initials = [3], finals=[4], transitions = [ 
        ...         (0,'a',1), (0,'b',1), (1,'a',2), (2,'a',3), (4,'c',3)
        ...     ]
        ... )
        >>> a.map( parity )
        >>> a == automaton(
        ...     initials=[1], finals=[0], transitions=[
        ...         (0,'a',1), (0,'b',1), (1,'a',0), (0,'c',1)
        ...     ]
        ... )
        True
        """
        def _f( state ):
            _test_is_hashable( state, "The images of f" )
            return f( state )
        self._states = set( map( _f, self._states ) )
        tmp = {}
        for e in self._adjacence:
            origin = _f( e[0] )
            tmp[ (origin, e[1]) ] = set( map( _f,self._adjacence[e] ) )
        self._adjacence = tmp
        self._final_states = set(
            map( _f, self._final_states )
        )
        self._initial_states = set(
            map( _f, self._initial_states )
        )
    def __eq__( self, a ):
        """
        Tests whether two automata are equals.
        
        More precisely, that function test if the 6-uplet
        <A, E, Q, I, F, T> of the two automata are equals.

        Example:
        >>> a = automaton(
        ...     alphabet = ['c'], epsilons = ['0'],
        ...     states = [5], initials = [0,1], finals = [3,4],
        ...     transitions=[
        ...         (0,'a',1), (1,'b',2), (2,'b',2), (2,'a',3), (3,'a',4)
        ...     ]
        ... )
        >>> b = a.clone()
        >>> a == b
        True
        >>> c = automaton(
        ...     alphabet = ['c'], epsilons = ['0'],
        ...     states = [5], initials = [0,1], finals = [3,4],
        ...     transitions=[
        ...         (0,'a',1), (1,'b',2), (2,'b',2), (2,'a',3), (3,'a',4)
        ...     ]
        ... )
        >>> a == c
        True
        >>> d = automaton(
        ...     epsilons = ['0'],
        ...     states = [5], initials = [0,1], finals = [3,4],
        ...     transitions=[
        ...         (0,'a',1), (1,'b',2), (2,'b',2), (2,'a',3), (3,'a',4)
        ...     ]
        ... )
        >>> a == d
        False
        """
        return (
            self.get_alphabet() == a.get_alphabet() and
            self.get_epsilons() == a.get_epsilons() and
            self.get_states() == a.get_states() and
            self.get_initial_states() == a.get_initial_states() and
            self.get_final_states() == a.get_final_states() and
            self.get_transitions() == a.get_transitions()
        )

    def clone( self ):
        """
        Returns a deep copy of the automaton.

        Example:

        >>> a = automaton( transitions = [ (0,'a',0), (0,'a',1) ] )
        >>> b = a.clone()
        >>> b is a
        False
        >>> b == a
        True
        """
        return copy.deepcopy( self )

    def get_renumbered_automaton( self ):
        """
        Returns a copy of the automaton with a new numbering for the states:
        now the states of the copy are integer going from 1 to n (n is the number
        of states of the automaton).

        Example:

        >>> a = automaton(
        ...     transitions = [
        ...         ( (1,2), 'a', (1,3) ),
        ...         ( (1,2), 'b', (4,5) ),
        ...         ( (4,5), 'a', (1,3) )
        ...     ]
        ... )
        >>> b = a.get_renumbered_automaton()
        >>> a is b
        False
        >>> b.get_states() == set( [1,2,3] )
        True
        """
        result = self.clone()
        result.renumber_the_states()
        return result

    def renumber_the_states( self ):
        """
        Renumbers all states of the automaton from 1 to n, where n 
        is the number of automaton states.

        Example:

        >>> b = automaton(
        ...     transitions = [
        ...         ( (1,2), 'a', (1,3) ),
        ...         ( (1,2), 'b', (4,5) ),
        ...         ( (4,5), 'a', (1,3) )
        ...     ]
        ... )
        >>> b.renumber_the_states()
        >>> b.get_states() == set( [1,2,3] )
        True
        """
        state_to_id = _object_to_id()
        for state in self._states:
            state_to_id.add_object( state )
        states = set()
        for state in self._states:
            states.add( state_to_id.id( state ) )
        initials = set()
        for state in self._initial_states:
            initials.add( state_to_id.id( state ) )
        finals = set()
        for state in self._final_states:
            finals.add( state_to_id.id( state ) )
        transitions = {}
        def renum( obj ):
            return state_to_id.id(obj)
        for o in self._adjacence:
            transitions[ ( state_to_id.id(o[0]), o[1]) ] = set(
                map( renum, self._adjacence[o] )
            )
        self._initial_states = initials
        self._states = states
        self._final_states = finals
        self._adjacence = transitions

    def add_initial_state( self, state ):
        """
        Adds an initial state

        Example:

        >>> a = automaton( )
        >>> a.get_states() == set()
        True
        >>> a.add_initial_state( 2 )
        >>> a.get_states() == set( [2] )
        True
        >>> a.get_initial_states() == set( [2] )
        True
        """
        self.add_state( state )
        self._initial_states.add( state ) 

    def add_initial_states( self, list_of_states ):
        """
        Adds a list of initial states

        Example:

        >>> a = automaton( )
        >>> a.get_states() == set() and a.get_initial_states() == set()
        True
        >>> a.add_initial_states( [ 1,2,3 ] )
        >>> a.get_states() == set( [1,2,3] )
        True
        >>> a.get_initial_states() == set( [1,2,3] )
        True
        """
        for state in list_of_states:
            self.add_initial_state( state )

    def add_final_state( self, state ):
        """
        Adds a final state

        Example:

        >>> a = automaton( )
        >>> a.get_states() == set()
        True
        >>> a.add_final_state( 2 )
        >>> a.get_states() == set( [2] )
        True
        >>> a.get_final_states() == set( [2] )
        True
        """
        self.add_state( state )
        self._final_states.add( state ) 

    def add_final_states( self, list_of_states ):
        """
        Adds a list of final states

        Example:

        >>> a = automaton( )
        >>> a.get_states() == set() and a.get_final_states() == set()
        True
        >>> a.add_final_states( [ 1,2,3 ] )
        >>> a.get_states() == set( [1,2,3] )
        True
        >>> a.get_final_states() == set( [1,2,3] )
        True
        """
        for state in list_of_states:
            self.add_final_state( state )

    def add_state( self, state ):
        """
        Adds a state.
        The state have to be hashable.
        That's why you have to use:
            automaton.pretty_set or frozenset   instead of    set
            tuple                               instead of    list

        Example:

        >>> a = automaton( )
        >>> a.get_states() == set()
        True
        >>> a.add_state( 2 )
        >>> a.get_states() == set( [2] )
        True
        >>> a.add_state( (1,3) )
        >>> a.get_states() == set( [2, (1,3)] )
        True

        We get an error if we try to use a set to code a state:

        >>> a.add_state( set([1,2,5]) )
        Traceback (most recent call last):
            ...
        Exception: In automaton module, States have to be hashable. Use automaton.pretty_set or frozenset instead of set.

        The solution is to use automaton.pretty_set:

        >>> a.add_state( pretty_set([1,2,5]) )

        We get an error if we try to use a list to code a state:

        >>> a.add_state( [1,2,5] )
        Traceback (most recent call last):
            ...
        Exception: In automaton module, States have to be hashable. Use tuple instead of list. For example (1,3) instead of [1,3].

        The solution is to use a tuple:

        >>> a.add_state( (1,2,5) )
        
        """
        _test_is_hashable( state, "States" )
        self._states.add( state )

    def add_states( self, list_of_states ):
        """
        Adds a list of states.

        Example:

        >>> a = automaton( )
        >>> a.add_states( [1,2,6] )
        >>> a.get_states() == set( [1,2,6] )
        True
        """
        for state in list_of_states:
            self.add_state( state )

    def add_character( self, character ):
        """
        Adds a character in the alphabet of the automaton.

        Characters have to be hashable.
        That's why you have to use:
            automaton.pretty_set or frozenset   instead of    set
            tuple                               instead of    list

        Example:

        >>> a = automaton( )
        >>> a.add_character( 'a' )
        >>> a.get_alphabet() == set( ['a'] )
        True

        We get an error if we try to use a set to code a character:

        >>> a.add_character( set([1,2,5]) )
        Traceback (most recent call last):
            ...
        Exception: In automaton module, Characters have to be hashable. Use automaton.pretty_set or frozenset instead of set.

        The solution is to use automaton.pretty_set:

        >>> a.add_character( pretty_set([1,2,5]) )

        We get an error if we try to use a list to code a character:

        >>> a.add_character( [1,2,5] )
        Traceback (most recent call last):
            ...
        Exception: In automaton module, Characters have to be hashable. Use tuple instead of list. For example (1,3) instead of [1,3].

        The solution is to use a tuple:

        >>> a.add_character( (1,2,5) )
        """
        _test_is_hashable( character, "Characters" )
        self._alphabet.add( character )

    def add_characters( self, list_of_characters ):
        """
        Adds all the characters of a list in the alphabet of the automaton.

        Example:

        >>> a = automaton( )
        >>> a.add_characters( ['a','b'] )
        >>> a.get_alphabet() == set( ['a','b'] )
        True
        """
        for character in list_of_characters:
            self.add_character( character )

    def add_epsilon_character( self, character ):
        """
        Defines an epsilon character and adds that character in       
        the alphabet.

        Characters have to be hashable.
        That's why you have to use:
            automaton.pretty_set or frozenset   instead of    set
            tuple                               instead of    list

        Example:

        >>> a = automaton( )
        >>> a.add_epsilon_character( '0' )
        >>> a.get_epsilons() == set( ['0'] )
        True

        We get an error if we try to use a set to code an epsilon character:

        >>> a.add_epsilon_character( set([1,2,5]) )
        Traceback (most recent call last):
            ...
        Exception: In automaton module, Epsilon characters have to be hashable. Use automaton.pretty_set or frozenset instead of set.

        The solution is to use automaton.pretty_set:

        >>> a.add_epsilon_character( pretty_set([1,2,5]) )

        We get an error if we try to use a list to code an epsilon character:

        >>> a.add_epsilon_character( [1,2,5] )
        Traceback (most recent call last):
            ...
        Exception: In automaton module, Epsilon characters have to be hashable. Use tuple instead of list. For example (1,3) instead of [1,3].

        The solution is to use a tuple:

        >>> a.add_epsilon_character( (1,2,5) )
        """
        _test_is_hashable( character, "Epsilon characters" )
        self.add_character( character )
        self._epsilons.add( character )

    def add_epsilon_characters( self, list_of_characters ):
        """
        Defines all the characters of a list as epsilon characters.

        Example:

        >>> a = automaton( )
        >>> a.add_epsilon_characters( ['a','b'] )
        >>> a.get_epsilons() == set( ['a','b'] )
        True
        """
        for character in list_of_characters:
            self.add_epsilon_character( character )

    def add_transition( self, transition ):
        """
        Adds a transition. The transition has to be a tuple (q1, c, q2)
        where q1 and q2 are states, and c is a character.

        Example:
        
        >>> a = automaton()
        >>> a.add_transition( (1,'a',2) )
        >>> a.get_transitions() == set( [ (1,'a',2) ] )
        True
        """
        _test_is_hashable( transition, "Transition" )
        ( q1, lettre, q2 ) = transition
        self.add_state( q1 )
        self.add_state( q2 )
        self.add_character( lettre )
        if( not (q1,lettre) in self._adjacence ):
            self._adjacence[ (q1, lettre) ] = set( )
        self._adjacence[ (q1, lettre) ].add( q2 )

    def add_transitions( self, list_of_transitions ):
        """
        Adds a list of transitions. The transitions have to be a tuple (q1, c, q2)
        where q1 and q2 are states, and c is a character.

        Example:
        
        >>> a = automaton()
        >>> a.add_transitions( [ (1,'a',2), (1,'b',1) ] )
        >>> a.get_transitions() == set( [ (1,'a',2), (1,'b',1) ] )
        True
        """
        for transition in list_of_transitions:
            self.add_transition( transition )

    def has_character( self, character ):
        """
        Tests whether a character is in the alphabet.

        Example:
        
        >>> a = automaton( alphabet=['a','b'])
        >>> a.has_character( 'a' ) and a.has_character( 'b' )
        True
        >>> a.has_character( 'c' )
        False
        """
        return character in self._alphabet

    def has_state( self, state ):
        """
        Tests whether a state is in the automaton.

        Example:
        
        >>> a = automaton( states=[1, (1,2)] )
        >>> a.has_state( 1 ) and a.has_state( (1,2) )
        True
        >>> a.has_state( 2 )
        False
        """
        return state in self._states
    def state_is_initial( self, state ):
        """
        Tests whether a state is initial.

        Example:
        
        >>> a = automaton( states= [1,2,3,4], initials=[1, 3] )
        >>> a.state_is_initial( 1 ) and a.state_is_initial( 3 )
        True
        >>> not( a.state_is_initial( 2 ) ) and not( a.state_is_initial( 4 ) )
        True
        """
        return state in self._initial_states

    def get_states( self ):
        """
        Returns the list of states.

        Example:
        
        >>> a = automaton( states= [1,2,3,4] )
        >>> a.get_states() == set( [1,2,3,4] )
        True
        """
        return pretty_set(self._states)
    def get_transitions( self ):
        """
        Returns the list of transitions.

        Example:
        
        >>> a = automaton( transitions= [ (0,'a',1), (1,'b',1), (1,'a',0) ] )
        >>> a.get_transitions() == set( [ (0,'a',1), (1,'b',1), (1,'a',0) ] )
        True
        """
        transitions = set()
        for key in self._adjacence:
            for end in self._adjacence[key]:
                transitions.add( (key[0], key[1], end) )
        return pretty_set(transitions)
    def state_is_final( self, state ):
        """
        Tests whether a state is final.

        Example:
        
        >>> a = automaton( states= [1,2,3,4], finals=[1, 3] )
        >>> a.state_is_final( 1 ) and a.state_is_final( 3 )
        True
        >>> not( a.state_is_final( 2 ) ) and not( a.state_is_initial( 4 ) )
        True
        """
        return state in self._final_states
    def get_initial_states( self ):
        """
        Returns the list of initial states.

        Example:
        
        >>> a = automaton( states=[1,2,3,4], initials=[ 1,3 ] )
        >>> a.get_initial_states() == set( [ 1, 3 ] )
        True
        """
        return pretty_set(self._initial_states)
    def get_final_states( self ):
        """
        Returns the list of final states.

        Example:
        
        >>> a = automaton( states=[1,2,3,4], finals=[ 1,3 ] )
        >>> a.get_final_states() == set( [ 1, 3 ] )
        True
        """
        return pretty_set(self._final_states)
    def get_alphabet( self ):
        """
        Returns the alphabet.

        Example:
        
        >>> a = automaton( alphabet=['a','c'] )
        >>> a.get_alphabet() == set( [ 'a', 'c' ] )
        True
        """
        return pretty_set(self._alphabet)

    def _delta( self, character, states ):
        result = set()
        for state in states:
            if (state,character) in self._adjacence:
                result.update( self._adjacence[ (state,character) ] )
        return pretty_set( result )

    def _expand_epsilons( self, states):
        old = pretty_set( )
        result = pretty_set( states )
        while( old != result ):
            old = result
            for eps in self._epsilons:
                result = result.union(
                    self._delta( eps, result )
                )
        return pretty_set(result)

    def remove_epsilon_transitions( self ):
        """
        Removes all the epsilon transition

        Example:
        
        >>> a = automaton( epsilons=['0','1'])
        >>> a.get_alphabet() == set( ['0','1'] ) and a.get_epsilons() == set( ['0','1'] )
        True
        >>> a.remove_epsilon_transitions()
        >>> a.get_alphabet() == set( ['0','1'] ) and a.get_epsilons() == set( )
        True
        """
        self._epsilons = set()

    def delta( self, character, states=None, ignore_epsilons=False ):
        """
        Returns the accessible states from some states by reading a character.

        Let ``states`` be the input set of state. Let``character`` be the
        input character.

        if ``character`` is an epsilon character, then the output is all the 
            states connected with ``states`` by using a path of epsilon 
            transitions.
        if ``character`` is not an epsilon character,
            The output is the set of vertices connected to ``state`` by using a 
            path containing exactly one transition labeled by ``character`` and
            any number of epsilon transitions.

        Keyword Arguments:

        states    -- A set of states [default= the inital states of the automaton]
        character -- a character
        ignore_epsilons -- if set to True, all the epsilon charaters will be 
                           considerated as usal character ( The input character 
                           will be considerated as usual character )

        Example:

        An exemple without epsilon transitions:
        >>> a = automaton(
        ...     initials=[0], finals=[1],
        ...     transitions=[
        ...         (0,'a',1), (0,'a',2),(1,'b',2),(2,'a',1)
        ...     ]
        ... )
        >>> a.delta( 'a' ) == a.delta( 'a', a.get_initial_states() )
        True
        >>> a.delta( 'a' ) == set( [1,2] )
        True
        >>> a.delta( 'b' ) == set( )
        True
        >>> a.delta( 'a', [2] ) == set( [1] )
        True
        >>> a.delta( 'a', [1,2] ) == set( [1] )
        True

        An exemple with epsilon transitions:
        >>> a = automaton(
        ...     epsilons=['0'],
        ...     initials=[0], finals=[3],
        ...     transitions=[
        ...         (0,'0',1), (1,'a',2), (1,'b',3), (2,'0',3), (3,'b',2), 
        ...         (3,'a',0)
        ...     ]
        ... )
        >>> a.delta( 'a' ) == a.delta( 'a', a.get_initial_states() )
        True
        >>> a.delta( 'a' ) == set( [2,3] )
        True
        >>> a.delta( 'b' ) == set( [3] )
        True
        >>> a.delta( '0' ) == set( [0,1] )
        True
        >>> a.delta( 'a', [1,2] ) == set( [0,1,2,3] )
        True
        >>> a.delta( 'b', [1,2] ) == set( [2,3] )
        True
        >>> a.delta( '0', [1,2] ) == set( [1,2,3] )
        True

        If we want to ignore the epsilon transitions:
        >>> a.delta( 'a', ignore_epsilons=True ) == set()
        True
        >>> a.delta( 'b', ignore_epsilons=True ) == set()
        True
        >>> a.delta( '0', ignore_epsilons=True ) == set( [1] )
        True
        >>> a.delta( 'a', [1,2], True ) == set( [2] )
        True
        >>> a.delta( 'b', [1,2], True ) == set( [3] )
        True
        >>> a.delta( '0', [1,2], True ) == set( [3] )
        True
        """
        if states==None:
            states = self.get_initial_states()
        if( ignore_epsilons or not( self.has_epsilon_characters() ) ):
            return self._delta( character, states )
        else:
            result = self._expand_epsilons( states )
            if( character in self._epsilons ):
                return result
            result = self._delta( character, result )
            return self._expand_epsilons( result )

    def delta_star( self, word, states=None, ignore_epsilons=False ):
        """
        if len(word)>0  return delta_star( word[1:], delta( word[0], states ) )
        else            return the set of epsilon accessible states from 
                        the input states ``states``.

        Keyword Arguments:

        states    -- A set of states [default= the inital states of the automaton]
        character -- a character
        ignore_epsilons -- if set to True, all the epsilon charaters will be
                           considerated as usal characters ( the input characters 
                           will be considated as usual characters )

        Example:
        >>> a = automaton(
        ...     initials=[0], finals=[1],
        ...     transitions=[
        ...         (0,'a',1), (0,'a',2),(1,'b',2),(2,'a',1)
        ...     ]
        ... )
        >>> a.delta_star( [ 'a', 'b', 'a' ] ) == set( [1] )
        True
        >>> a.delta_star( [ 'b', 'a' ] ) == set( )
        True
        >>> a.delta_star( [ ] ) == set( [0] )
        True
        >>> a.delta_star( [ 'a', 'b', 'a' ], [1] ) == set()
        True
        >>> a.delta_star( [ 'b', 'a' ], [0,1] ) == set( [1] )
        True
        >>> a.delta_star( [], [1] ) == set( [1] )
        True

        An exemple with epsilon transitions:
        >>> a = automaton(
        ...     epsilons=['0'],
        ...     initials=[0], finals=[3],
        ...     transitions=[
        ...         (0,'0',1), (1,'a',2), (1,'b',3), (2,'0',3), (3,'b',2), 
        ...         (3,'a',0)
        ...     ]
        ... )
        >>> a.delta_star( [ 'b', 'a', 'a' ] ) == set( [2,3] )
        True
        >>> a.delta_star( [ '0', 'b', '0', 'a', '0' ] ) == a.delta_star( [ 'b', 'a' ] )
        True
        >>> a.delta_star( [ 'b', '0', 'a' ] ) == set( [0,1] )
        True

        If we want to ignore the epsilon transitions:
        >>> a.delta_star( [ 'b', 'a', 'a' ], ignore_epsilons=True ) == set()
        True
        >>> a.delta_star( [ '0', 'b', 'a', '0', 'a' ], ignore_epsilons=True ) == set( [2] )
        True
        >>> a.delta_star( [ 'b', 'a' ], ignore_epsilons=True ) == set( )
        True
        
        """
        if states==None:
            states = self.get_initial_states()
        if( ignore_epsilons or not( self.has_epsilon_characters() ) ):
            result = states
            for character in word:
                result = self._delta( character, result )
            return pretty_set(result)
        else:
            result = self._expand_epsilons( states )
            for character in word:
                result = self.delta( character, result )
            return pretty_set(result)

    def word_is_recognized(
        self, word, initial_states=None, ignore_epsilons=False
    ):
        """
        Returns True if the word is recognized by the automaton.
        
        Epsilon characters are considerated to be the same neutral element
        of the free monoide of the words on the set of non-epsilon characters.

        Keyword arguments:
        world -- a list of character
        initial_states -- a alternative set of initial state 
                          [default=the initial set of the automaton]
        ignore_epsilons -- if set to True, all the epsilon charaters will be 
                           considerated as usal characters ( the characters of 
                           the input world will be considated as usual characters )
        
        Example:

        An exemple without epsilon transitions:
        >>> a = automaton(
        ...     initials=[0], finals=[1],
        ...     transitions=[
        ...         (0,'a',1), (0,'a',2),(1,'b',2),(2,'a',1)
        ...     ]
        ... )
        >>> a.word_is_recognized( [ 'a', 'b', 'a' ] )
        True
        >>> a.word_is_recognized( [ 'b', 'a' ] )
        False
        >>> a.word_is_recognized( [ ] )
        False
        >>> a.word_is_recognized( [ 'a', 'b', 'a' ], [1] )
        False
        >>> a.word_is_recognized( [ 'b', 'a' ], [0,1] )
        True
        >>> a.word_is_recognized( [ ], [1] )
        True

        An exemple with epsilon transitions:
        >>> a = automaton(
        ...     epsilons=['0'],
        ...     initials=[0], finals=[3],
        ...     transitions=[
        ...         (0,'0',1), (1,'a',2), (1,'b',3), (2,'0',3), (3,'b',2), 
        ...         (3,'a',0)
        ...     ]
        ... )
        >>> a.word_is_recognized( [ 'b', 'a', 'a' ] )
        True
        >>> a.word_is_recognized( [ '0', 'b', '0', 'a', '0' ] ) == a.word_is_recognized( [ 'b', 'a' ] )
        True
        >>> a.word_is_recognized( [ 'b', '0', 'a' ] )
        False

        If we want to ignore the epsilon transitions:
        >>> a.word_is_recognized( [ 'b', 'a', 'a' ], ignore_epsilons=True )
        False
        >>> a.word_is_recognized( [ '0', 'b', 'a', '0', 'a' ], ignore_epsilons=True )
        False
        >>> a.word_is_recognized( [ 'b', 'a' ], ignore_epsilons=True )
        False
        
        """
        ending_states = self.delta_star(
            word, initial_states, ignore_epsilons
        )
        for state in ending_states:
            if self.state_is_final( state ):
                return True
        return False

    def to_dot( self, title=None ):
        """
        Returns the string containing the dot format of the automaton.

        Example:

        >>> a = automaton()
        >>> print( a.to_dot() )
        <BLANKLINE>
        digraph G {
        }
        
        """
        state_to_id = _object_to_id()
        for state in self._states:
            state_to_id.add_object( state )
        result = ""
        result += '\ndigraph G {'
        if( title != None ):
            result += '\n\t// title'
            result += '\n\tlabelloc="t";'
            result += '\n\tlabel="' + str(title) + '";'
        for origin in self._states:
            for character in self._alphabet:
                if( (origin,character) in self._adjacence ):
                    for end in self._adjacence[ (origin, character) ]:
                        result += (
                            '\n\t' + str(state_to_id.id(origin)) + '->' + 
                            str(state_to_id.id(end)) + ' [label=' +
                            str(character) + ', shape=normal]'
                        )
        for state in self._states:
            if state in self._final_states and state in self._initial_states:
                result += (
                    '\n\t' + str(state_to_id.id(state)) + 
                    ' [margin=0.0, shape=diamond, peripheries=2, label="' +
                    str(state) + '"];'
                )
            elif state in self._final_states:
                result += (
                    '\n\t' + str(state_to_id.id(state)) + 
                    ' [margin=0.0, shape=oval, peripheries=2, label="' +
                    str(state) + '"];'
                )
            elif state in self._initial_states:
                result += (
                    '\n\t' + str(state_to_id.id(state)) + 
                    ' [margin=0.0, shape=diamond, label="' + str(state) + '"];'
                )
            else:
                result += (
                    '\n\t' + str(state_to_id.id(state)) + 
                    ' [margin=0.0, shape=oval, label="' + str(state) + '"];'
                )
        result += '\n}'
        return result
    def display( self, title=None, wait=True ):
        """
        Displays the automaton on the screen.
        
        Keyword Arguments:
        title -- The title of the figure [default=None]
        wait -- If set to True, display(...) interupt the program, display the 
                automaton and the program will continue if the user close the 
                automaton window.
                Tf set to False, display(...) display the automaton, but doesn't
                block the execution of the main program.

        Bug:
        On Windows, display never dosen't block the execution of the main program.
        On Windows, temporary files are not freed.
        """ 
        f=tempfile.NamedTemporaryFile(delete=False)
        f.write( self.to_dot( title ).encode( 'utf-8' ) )
        f.close()
        def render_with_dotty():
            process=subprocess.call(
                'dotty ' + f.name,
                shell=True
            )
            # A HACK
            if not( platform.system()=='Windows' ):
                os.remove(f.name)
        if wait :
            render_with_dotty()
        else:
            a = threading.Thread( target=render_with_dotty )
            a.start()

def xml_to_list_of_automata( xml_path ):
    """
    Converts an xml file to a list of automata.
    
    Keyword arguments:
    xml_path -- the path of the xml file.

    Example:

    We create a temporary file and write in that file the xml code of two 
    automata.
    Then we load that two automata with the xml_to_list_of_automata( ... )
    function.

    >>> f=tempfile.NamedTemporaryFile()
    >>> f.write(
    ...     '''
    ...     <list_of_automata>
    ...
    ...     <automaton>
    ...         <alphabet>   <c>a</c><c>b</c>   </alphabet>
    ...         <states> <s>1</s><s>2</s><s>3</s> </states>
    ...         <initials>   <s>1</s>   </initials>
    ...         <finals>   <s>2</s><s>3</s>   </finals>
    ...         <transitions>
    ...             <t> <o>1</o><c>a</c><e>2</e> </t>
    ...             <t> <o>2</o><c>b</c><e>3</e> </t>
    ...         </transitions>
    ...     </automaton>
    ...
    ...     <automaton>
    ...         <epsilons>   <c>0</c>   </epsilons>
    ...         <initials>   <s>1</s>   </initials>
    ...         <finals>   <s>1</s>   </finals>
    ...         <transitions>
    ...             <t> <o>1</o><c>a</c><e>2</e> </t>
    ...             <t> <o>2</o><c>0</c><e>1</e> </t>
    ...         </transitions>
    ...     </automaton>
    ...
    ...     </list_of_automata>
    ...     '''.encode('utf-8')
    ... ) != 0
    True
    >>> f.flush()
    >>> [automate1, automate2] = xml_to_list_of_automata( f.name )
    >>> f.close()
    """
    tree = ET.parse(xml_path)
    doc = tree.getroot()
    result = []
    for xml_automaton in doc.findall('./automaton'):
        aut = automaton()
        for xml_character in xml_automaton.findall('epsilons/c'):
            aut.add_epsilon_character( str(xml_character.text) )
        for xml_character in xml_automaton.findall('alphabet/c'):
            aut.add_character( str(xml_character.text) )
        for xml_state in xml_automaton.findall('states/s'):
            aut.add_state( int(xml_state.text) )
        for xml_state in xml_automaton.findall('initials/s'):
            aut.add_initial_state( int(xml_state.text) )
        for xml_state in xml_automaton.findall('finals/s'):
            aut.add_final_state( int(xml_state.text) )
        for xml_transition in xml_automaton.findall('transitions/t'):
            aut.add_transition(
                (
                    int(xml_transition.findall('o')[0].text),
                    str(xml_transition.findall('c')[0].text),
                    int(xml_transition.findall('e')[0].text)
                )
            )
        result.append(aut)
    return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
