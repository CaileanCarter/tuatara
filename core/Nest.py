
from collections import namedtuple
import logging
# import pickle
from ..nest.hatcher import hatch
from ..tools.utils import flatten, dedupe
from ScrumPy import Model as ScrumPyModel
# from ..nest.keeper import check_egg_exists

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Nest(dict):


    def __init__(self, *models, names=None):
        if names:
            self.__dict__.update({name : {"Model" : model} for name, model in zip(names, models)})
        else:
            self.__dict__.update({index : {"Model" : model} for index, model in enumerate(models)})


    def __getitem__(self, attr):
        if isinstance(attr, list): 
            return [self.__dict__[model]["Model"] for model in attr]
        # elif isinstance(attr, slice): 
        #     return [self.__dict__[model]["Model"] for model in list(self.__dict__.keys())[attr]]
        elif isinstance(attr, slice):
            return [self.__dict__[model]["Model"] for model in list(self.__dict__.keys())][attr]
        else: 
            return self.__dict__[attr]["Model"]


    def __setitem__(self, index, values):
        #FIXME: not for adding model but including data.

        if isinstance(index, (str, int)):

            if isinstance(values, (str, int)):
                for key in self.__dict__.keys():
                    self.__dict__[key][index] = values

            elif isinstance(values, (list, tuple, set)):
                for key, value in zip(self.__dict__.keys(), values):
                    self.__dict__[key][index] = value

            else:
                raise TypeError(f"Unexpected type: {type(values)}.")

        if isinstance(index, list):
            # model selection
            pass


    def __len__(self):
        return len(self.__dict__.keys())

    def __repr__(self):
        return  "Nest dict: [" + ", ".join(self.__dict__.keys()) + "]"


    def __delitem__(self, key):
        self.drop(egg=key)


    def __iter__(self):

        pass

    def __contains__(self, item):
        pass


    #--------------------------------------------------
    # Properties (are methods)

    def columns(self):
        cols = [list(row.keys()) for row in self.__dict__.values()]
        flat = flatten(cols)
        return list(dedupe(flat))

    
    def keys(self):
        return self.__dict__.keys()
        

    def items(self):
        for key, value in self.__dict__.items():
            yield key, value
        

    def values(self):
        for value in self.__dict__.values():
            yield value


    def index(self):
        return self.keys()


    def _next_col(self):
        col_index = [col for col in self.columns() if isinstance(col, int)]
        return max(col_index) + 1

    
    def _next_index(self):
        indexes = [index for index in self.keys() if isinstance(index, int)]
        next_index = max(indexes) + 1
        return next_index


    #--------------------------------------------------
    #Methods

    @classmethod
    def from_file(cls, model=None, files=None, names=None):
        # TODO: accept str, list and dict
        m = ScrumPyModel(model)

        if isinstance(files, dict):
            names = list(files.keys())
            files = list(files.values())
        
        elif isinstance(files, str):
            files = [files]
        
        nest = [hatch(m, fromspy=egg) for egg in files]
        nest.insert(0, m)
        names.insert(0, 0)
        return cls(*nest, names=names)


    @classmethod
    def from_nest(cls, model=None, eggs=None):
        m = ScrumPyModel(model)

        nest = [hatch(m, egg) for egg in eggs]
        nest.insert(0, m)
        names = eggs
        names.insert(0, 0)
        return cls(*nest, names=names)


    def insert(self, egg, name=None):
        if not name:
            name = self._next_index()
        self.__dict__.update({name : {"Model" : egg}})


    def drop(self, egg=None):
        del self.__dict__[egg]


    def apply(self, func, *args, index=None, **kwargs):
        pass


    def iter(self):
        pass


    def serialise(self, file=None, **kwargs):
        # TODO: output to pickle
        pass


    def describe(self):
        pass
    
    
