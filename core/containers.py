"""
Containers module for tuatara.

"""
#TODO: write docstring

import sys
import io
import logging
from abc import ABC, abstractclassmethod
from itertools import chain, zip_longest

import pandas as pd
from ScrumPy import Model as ScrumPyModel

# import pickle
from ..nest.hatcher import hatch
from ..tools.utils import dedupe, flatten
from ..tools.tuakit import LP

# from ..nest.keeper import check_egg_exists

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def open_model(model):
    try:
        m = ScrumPyModel(model)
    except TypeError:
        if Nest._check_model(model):
            m = model
    finally:
        return m


class Constructors(ABC):

    @abstractclassmethod
    def from_nest(self):
        pass

    @abstractclassmethod
    def from_file(self):
        pass

    @abstractclassmethod
    def from_BuildNest(self):
        pass


class Nest(dict, Constructors):


    def __init__(self, *models, names=None):
        if names:
            self.__dict__.update({name : {"Model" : model} for name, model in zip(names, models) if self._check_model(model)})
        else:
            self.__dict__.update({index : {"Model" : model} for index, model in enumerate(models) if self._check_model(model)})


    @staticmethod
    def _check_model(model):
        """Type checking for models"""
        assert hasattr(model, "sm"), f"Nest accepts model object, not {type(model)}"
        return True


    def __getitem__(self, attr):
        if isinstance(attr, list): 
            return [self.__dict__[model]["Model"] for model in attr]
        elif isinstance(attr, slice):
            return [self.__dict__[model]["Model"] for model in list(self.__dict__.keys())][attr]
        else: 
            return self.__dict__[attr]["Model"]


    def __setitem__(self, index, values):
        #TODO: tidy and sort.

        # def TE(value): raise TypeError(f"Unexpected type: {type(value)}.")

        if isinstance(index, (str, int)):

            if isinstance(values, (str, int, float)):
                for key in self.__dict__.keys():
                    self.__dict__[key][index] = values

            elif isinstance(values, (list, tuple, set)):
                for key, value in zip_longest(self.__dict__.keys(), values, fillvalue=None):
                    self.__dict__[key][index] = value

            # else: TE(values)
        

        elif isinstance(index, (list, tuple, set)):
            col_name = index[0]

            if isinstance(values, (str, int, float)):
                for i in self.__dict__.keys():
                    if i not in index[1]:
                        self.__dict__[i][col_name] = None
                    else:
                        self.__dict__[i][col_name] = values

            elif isinstance(values, (list, tuple, set)):

                for i, v in zip(index[1], values):
                    self.__dict__[i][col_name] = v

                for i in self.__dict__.keys():
                    if i not in index[1]:
                        self.__dict__[i][col_name] = None

        #     else: TE(values)
        # else: TE(index)


    def __len__(self):
        return len(self.__dict__.keys())


    def __repr__(self):
        return  f"Nest dict keys: {len(self.columns())}x{len(self)} [{', '.join([str(key) for key in self.__dict__.keys()])}]"


    def __delitem__(self, key):
        self.drop(egg=key)


    def __iter__(self):
        for row in self.__dict__.items():
            yield row


    def __contains__(self, item):
        """Is item in columns or keys"""
        for element in chain.from_iterable(self.columns(), self.keys()):
            if item in element:
                return True
        return False


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

    
    def col(self, columns):

        if isinstance(columns, (int, str)): return [item[columns] for item in self.__dict__.values()]

        elif isinstance(columns, (list, tuple, set)):
            c = {}
            for column in columns:
                c.update({column : [item[column] for item in self.__dict__.values()]})
            return c

        else:
            raise TypeError(f"Unexpect type: {type(columns)}")


    def _next_col(self):
        col_index = [col for col in self.columns() if isinstance(col, int)]
        return max(col_index) + 1

    
    def _next_index(self):
        indexes = [index for index in self.keys() if isinstance(index, int)]
        next_index = max(indexes) + 1
        return next_index

    #------------------------------------------------------------------------
    #Constructors
  
    @classmethod
    def from_file(cls, model, files=None, names=None):
        m = open_model(model)

        if isinstance(files, dict):
            names, files = zip(*files.items())

        elif isinstance(files, str):
            files = [files]
        
        nest = [hatch(m, fromspy=egg) for egg in files]
        nest.insert(0, m)
        names.insert(0, "model")
        return cls(*nest, names=names)


    @classmethod
    def from_nest(cls, model, eggs=None):
        m = open_model(model)

        nest = [hatch(m, egg) for egg in eggs]
        nest.insert(0, m)
        names = eggs
        names.insert(0, "model")
        return cls(*nest, names=names)


    @classmethod
    def from_BuildNest(cls, model, BuildNest):
        return cls.from_nest(model, eggs=BuildNest.samples)


    #--------------------------------------------------
    #Methods

    def insert(self, egg, name=None):
        if not name:
            name = self._next_index()
        assert self._check_model(egg)
        self.__dict__.update({name : {"Model" : egg}})
        if len(self.columns()) != 1:
            self.__dict__.update({name : {column : None for column in self.columns() if column != "Model"}})

    
    def insert_hatch(self, model, egg, name=None):
        m = open_model(model)
        new_egg = hatch(m, egg)
        self.insert(new_egg, name=name)


    def drop(self, egg=None, col=None):
        if egg: del self.__dict__[egg]
        elif col:
            for item in self.__dict__.values():
                del item[col]
    
    
    def select(self, sel):
        row = sel[0]
        column = sel[1]
        return self.__dict__[row][column]

    
    def Hide(self): self['model'].Hide()


    def Show(self): self['model'].Show()


    def apply(self, func, *args, index=None, **kwargs):
        pass


    def iter(self, axis=0):
        if axis in (0, "row"):
            return iter(self)

        if axis in (1, "col"):
            cols = [{"index" : list(self.index())}]
            for c in self.columns():
                cols.append(self.col(c))

            for column in cols:
                yield column
            

    def iter_models(self):
        for key, value in self.__dict__.items():
            yield key, value["Model"]


    def fetchLP(self, models="model", func=LP.build, **kwargs):
        def run_LP(model):
            lp = func(model, **kwargs)
            if isinstance(lp, dict): return lp #already solved
            lp.Solve()
            return lp.GetPrimSol()
        return [run_LP(model) for _, model in self.iter_models()]


    def serialise(self, file, **kwargs):
        # TODO: output to pickle?
        pass


    def describe(self):
        desc = []
        for name, model in self.iter_models():
            name = str(name).upper()
            reacs = len([reac for reac in model.sm.cnames if not reac.endswith("_tx")])
            trans = len([t for t in model.sm.cnames if t.endswith("_tx")])
            mets = len(model.sm.rnames)
        
            model_statement = f"\t{name}\n\tReactions:\t{reacs}\n\tTransporters:\t{trans}\n\tMetabolites:\t{mets}"
            desc.append(model_statement)
        model_desc = "\n\n".join(desc)
        statement = f"""
        tuatara - Nest summary

        MAIN
        Models:     {len(self)}
        Columns:    {len(self.columns())}
        \n{model_desc}
        
        END"""

        print(statement)

    
    def to_community(self):
        #TODO: write me.
        pass


    def to_dict(self): return self.__dict__


class Community(pd.DataFrame, Constructors):


    def __init__(self, *models, index=None, columns=None, **kwargs):

        if len(models) == 1 and isinstance(models[0], dict):
            arguments = models[0]
        else:
            arguments = {"model" : [model for model in models if Nest._check_model(model)]}

        if columns:
            arguments = {**arguments, **columns}
    
        super().__init__(arguments, index=index, **kwargs)


    #----------------------------------------------
    #Constructors

    @classmethod
    def from_nest(cls, model, eggs=None, index=None, columns=None, **kwargs):
        m = open_model(model)

        # try:
        models = {"model" : [hatch(m, egg) for egg in eggs]}
        # except FileNotFoundError:
        #     models = {"model" : [hatch(m, egg[:-4]) for egg in eggs]} #try removing ".spy"

        models["model"].insert(0, m)
        if index and index[0] != "model": #should check are equal length?
            index.insert(0, "model")

        if columns:
            arguments = {**models, **columns}
        else:
            arguments = models

        return cls(arguments, index=index, **kwargs)
        

    @classmethod
    def from_file(cls, model, files=None):
        #TODO: write me.
        pass


    @classmethod
    def read_file(cls, model, file, delimiter="\n", **kwargs):
        m = open_model(model)
        models = [m]

        if delimiter == "\n":
            eggs = [line.strip() for line in open(file).readlines()]
        else:
            eggs = []
            for line in open(file).readlines():
                eggs += [item.strip() for item in line.split(delimiter)]

        for egg in eggs:
            if not egg:
                continue
            elif egg.endswith(".spy"):
                models.append(hatch(m, fromspy=egg))
            else:
                models.append(hatch(m, egg))

        return cls(*models, **kwargs)


    @classmethod
    def from_BuildNest(cls, model, BuildNest, columns=None):
        return cls.from_nest(model, eggs=BuildNest.samples, columns=columns)


    #-----------------------------------------------
    #Methods

    def Hide(self): self.iloc[0]["model"].Hide()


    def Show(self): self.iloc[0]["model"].Show()


    def iter_models(self, column="model"):
        for model in self[column].values:
            yield model


    def fetchLP(self, models="model", func=LP.build, stdout=True, **kwargs):

        def run_LP(model):
            lp = func(model, **kwargs)
            if isinstance(lp, dict): 
                return lp #already solved
            lp.Solve()
            return lp.GetPrimSol()

        if not stdout:
            old_output = sys.stdout
            redirection = io.StringIO()
            sys.stdout = redirection

        result = self[models].map(run_LP)

        if not stdout:
            out = redirection.getvalue()
            sys.stdout = old_output

            lp_output = []
            LPresult = iter(out.split("\n"))
            for i in LPresult:
                if not i:
                    continue
                elif i.startswith("biomass"):
                    text = "\n".join([i, next(LPresult)])
                    lp_output.append(text)
                else:
                    lp_output.append(i)
            result = pd.concat([result, pd.Series(data=lp_output, index=result.index)], axis=1)

        return result

    
    def _debug(self, column):
        return self[column].map(lambda x : len(x))
