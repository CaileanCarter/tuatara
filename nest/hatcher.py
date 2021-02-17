"""
Egg handling module for tuatara.

...

Functions:

    hatch(m, egg)           -> model

"""


import re
from collections import namedtuple
from itertools import zip_longest
# import copy
from ..tools.utils import dequote, remove_prefix
from ..core.GUI import _ask_spy_file
from .keeper import get_path


def new_egg(obj):
    class Egg(obj.__class__):
        def __init__(self) : 
            for attr, value in vars(obj).copy().items():
                setattr(self, attr, value)
    
    newcopy = Egg()
    newcopy.__class__ = obj.__class__
    
    return newcopy


class _Parser:

    """
    Handles the tuatara .spy files.
    """

    def __init__(self):

        self.headings = ["name", "StoMat", "direction"]
        self.StoDict = namedtuple('StoDict', self.headings)

        self._name = None
        self._StoMat = {}
        self._direction = None

    def to_SD(self, line):

        """
        Converts a ScrumPy reaction into a stoichiometry dictionary. Adds result to _StoMat.

            Parameters:
                line (str) : a line from the .spy file contianing only the reaction equation.
        """

        flux_values = [-1, 1]

        reaction = self.split_reaction(line)
        self._direction = reaction.direction

        for pair in zip_longest(reaction.substrates, reaction.products):
            for index, metabolite in enumerate(pair):
                if metabolite:
                    flux = flux_values[index] 
                    if metabolite[0].isdigit():
                        flux = int(metabolite[0]) if index == 1 else 0 - int(metabolite[0])
                        metabolite = metabolite[1:].strip()
                    self._StoMat.update({metabolite : flux})
                        
    def split_reaction(self, reaction):
        # This version has a slight deviation from the original
        # The reaction input does not include the reaction name
        # So the method has been altered to not include that part
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

        trim_split = directions.split(reaction)
        direction = directions.search(reaction)

        substrates = [dequote(substrate.strip()) for substrate in trim_split[0].split("+")]
        products = [dequote(product.strip()) for product in trim_split[1].split("+")]

        return Reaction(substrates, direction[0], products)

    def return_StoMat(self) -> namedtuple: return self.StoDict(self._name, self._StoMat, self._direction)


def _parse_file(egg_path):
    """Parses the .spy file into usable forms which can be added to or removed from model."""
    egg_reactions = []
    remove_list = []

    parse = _Parser()
    with open(egg_path, 'r') as f:
        try:
            while True:
                line = next(f)
                line = line.strip()
                if line and not line.startswith('#'):
                    if line[1:4] == "rm_":
                        reacID = remove_prefix(line[:-1])
                        reacID = dequote(reacID)
                        remove_list.append(reacID)
                        _ = next(f)
                        _ = next(f)

                    elif ":" in line:
                        parse._name = line[:-1]
                        parse.to_SD(next(f))
                        egg_reactions.append(parse.return_StoMat())
                        _ = next(f)
                        parse.__init__()

        except StopIteration:
            return egg_reactions, remove_list


def hatch(m, egg=None, fromspy=False):
    # FIXME
    """
    Load an egg into the model.

        Parameters:
            m (obj) : model
            egg (str) : egg ID
            fromspy (bool) : open file explorer to select .spy file 

        Returns:
            m (obj) : model of egg
    """
    if egg:
        egg_path = get_path(egg)
    elif fromspy:
        egg_path = _ask_spy_file()
    else:
        raise ValueError("Expected egg or fromspy argument.")

    reactions, removals = _parse_file(egg_path)
    new_model = new_egg(m)
    new_model.DelReactions(removals)
    for reaction in reactions:
        try:
            new_model.sm.NewReaction(reaction.name, reaction.StoMat, reaction.direction)
        except TypeError:
            continue
    m.Init()
    return new_model
