
from collections import namedtuple
import pickle


class Nest(dict):


    def __init__(self, *models, names=None):
        if names:
            self.__dict__.update({name : {"Model" : model} for name, model in zip(names, models)})
        else:
            self.__dict__.update({index : {"Model" : model} for index, model in enumerate(models)})
    

    def __getitem__(self, attr):
        if isinstance(attr, list): 
            return [self.__dict__[model]["Model"] for model in attr]
        elif isinstance(attr, slice): 
            return [self.__dict__[model]["Model"] for model in list(self.__dict__.keys())[attr]]
        else: 
            return self.__dict__[attr]["Model"]


    def __setitem__(self, name, model):
        self.__dict__[name]["Model"] = model


    def __len__(self):
        pass

    def __repr__(self):
        pass


    def __delitem__(self, key):
        del self.__dict__[key]


    def apply(self, func, *args, index=None, **kwargs):
        pass


    def iter(self):
        pass

    def __iter__(self):
        pass


    def serialise(self, file=None, **kwargs):
        # TODO: output to pickle
        pass

    def describe(self):
        pass
    
    