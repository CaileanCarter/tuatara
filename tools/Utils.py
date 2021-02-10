"""
Utilities module for tuatara.

...

Classes:

    HidePrints

Functions:

    remove_suffix(value)                -> str
    list_identical(list_a, list_b)      -> bool
    str_identical(str_a, str_b)         -> bool
    split_reaction(reaction)            -> namedtuple
    add_prefix(reaction, prefix='tua_') -> str
    remove_prefix(reaction)             -> str
    str_len(value)                      -> str
    is_quoted(s)                        -> bool
    dequote(s)                          -> str
"""

import re
import sys
from collections import namedtuple
from os import devnull


def remove_suffix(value: str) -> str:
    """
    Takes a string and returns same string without numbers and '-' or '_' at the end.

        Parameters:
            value (str)

        Returns:
            result (str)
    """
    regex = r"^\w+[^_\-\d:]"
    result = re.match(regex, value)
    return result.group(0)


def list_identical(list_a, list_b) -> bool: return sorted(list_a) == sorted(list_b)


def str_identical(str_a, str_b) -> bool: return str_a == str_b


def split_reaction(reaction):
    """
    Returns the substrates, direction and products of a ScrumPy reaction.

        Parameters:
            Reaction (str) : A ScrumPy reaction

        Returns:
            Reaction (namedtuple): 
                (list)      substrates
                (string)    direction
                (list)      products
    """
    #                         <|°_°|>
    directions = re.compile("->|<>|<-")
    headings = ['substrates', 'direction', 'products']
    Reaction = namedtuple('Reaction', headings)

    _, trimmed = reaction[:-1].split(":")
    trimmed = trimmed.strip()

    trim_split = directions.split(trimmed)
    direction = directions.search(trimmed)

    substrates = [substrate.strip() for substrate in trim_split[0].split("+")]
    products = [product.strip() for product in trim_split[1].split("+")]

    return Reaction(substrates, direction[0], products)


def add_prefix(reaction: str, prefix="rm_") -> str:
    """
    Adds the prefix notation for tuatara reactions.

    Parameters:
        reaction (str) : A ScrumPy reaction.
    Returns:
        reaction (str) : A ScrumPy reaction with tuatara annotations.
    """
    return reaction[:1] + prefix + reaction[1:]


def remove_prefix(reaction: str) -> str:
    """
    Removes the prefix notation for tuatara reactions.

    Parameters:
        reaction (str) : A ScrumPy reaction with tuatara annotations.
    Returns:
        reaction (str) : A ScrumPy reaction.
    """
    # if reaction[1:5] == "tua_":
    index = 5
    if reaction[1:4] == "rm_":
        index = 4
    head = reaction[:1]
    tail = reaction[index:]
    return head + tail


def str_len(value: iter) -> str: return str(len(value))


def is_quoted(s: str) -> bool: return len(s)>2 and (s[0] == s[-1] == '"')


def dequote(s : str) -> str: return s[1:-1] if is_quoted(s) else s


class HidePrints:

    """
    A context manager class for hiding print statements.

    ...

    Usage
    ------
    with HidePrints():
        *Code block containing print statements wishing to hide.*
    """

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


class SetUtils:

    @staticmethod
    def complement(a, b): return [el for el in a if el not in b]
 
    @staticmethod
    def intersects(setlist): 
        """ pre: setl is a list of sets, len(setl) > 1
        post: the intersection of all sets in setl """
        rv = setlist[0]
        for s in setlist[1:]:
            rv = SetUtils.intersect(rv,s)
        return rv

    @staticmethod
    def intersect(a, b): return [el for el in a if el in b]
 
    @staticmethod
    def union(a, b): return [el for el in b if el not in a]

    @staticmethod
    def does_intersect(a, b): return any([el in b for el in a])

    @staticmethod
    def merge(SetList, __first=True):
        """ Pre: SetList is a list of sets, __first is private
        Post: Merge(SetList) == list of of sets, such that intersection in SetList are mereged,
                e.g. Merge([[1,2],[2,3],[4,5]]) => [[1,2,3],[4,5]]
        """

        if __first:
            SetList = SetList[:]
            __first = False

        Seen = 0   # not a set, so won't be in SetList from User
        lensets = len(SetList)
        rv = []
        for idx1 in range(lensets):
            if SetList[idx1] != Seen:
                newset = SetList[idx1]
                SetList[idx1] = Seen
                for idx2 in range(idx1+1, lensets):
                    s2 = SetList[idx2]
                    if s2 != Seen and SetUtils.does_intersect(newset, s2):
                        newset = SetUtils.union(newset,s2)
                        SetList[idx2] = Seen
                rv.append(newset)
        if len(rv) < lensets:
            return SetUtils.merge(rv, __first)
        else:
            return rv




#---------------------------------------------------
#dev tools

import time
from functools import wraps
from contextlib import contextmanager

def _timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
        return r
    return wrapper

@contextmanager
def _timeblock(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print('{} : {}'.format(label, end-start))
    