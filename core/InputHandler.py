"""
Input module for tuatara.

...

Classes:

    Inputs(roary=None, model=None, databases=None, fp=None, annots=None, locustags=None)

Functions:

    read_yaml(fp)
    read_json(fp)
    
"""


import re
from os import listdir, path


class _AllIsolates:

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            all_isolates = self.func(instance)
            setattr(instance, self.func.__name__, all_isolates)
            return all_isolates


class Inputs:

    """
    A class for inputting all requirements for building a nest.

    ...

    Parameters
    ----------
    roary : str
        File path for roary "Gene Presence Absence file in Rtab format".

    locustags : str
        File path for roary "Clustered proteins file".

    databases : dict
        Declare which isolates in Roary files have BioCyc databases available.
        key (str) : database organism in roary file
        value (str) : directory name for location of database (excluding version number subdirectory)
        Example: {"UTI89" : "EcoliUTI89"}
        
    fp : str
        Shared path for database directories.

    model : str
        Name of organism used as model as stated in roary files
    
    annots : str
        File path for directory containing Prokka annotation files of database organism genomes in tabular format.
        The Galaxy output is normally titled: "Prokka on [input]: tsv"
        Ensure file name is the same name as given in the roary files.
        Format: organism_name.tabular


    Attributes
    ----------
    model : str
        Name of organism used as model as stated in roary files

    databases : list
        List of database organism IDs

    db_fp : dict
        key : database organism ID
        value : database file path

    samples : list
        List of isolates found in roary gene presence/absence file (excluding database organisms)

    gpafile : str
        File path for roary "Gene Presence Absence file in Rtab format".

    annotations : str
        File path for directory containing Prokka annotation files of database organism genomes in tabular format.

    drop_columns : list
        A list of organisms to be ignored from the Roary file.

    rename : dict
        Rename an isolate in the roary file. 
        key (str) : original name of isolate
        value (str) : new name for isolate


    Methods
    -------
    drop(*isolates):
        Remove an isolate from the list.
    rename(pair):
        Rename an isolate.


    """

    def __init__(self, roary=None, model=None, databases=None, fp=None, annots=None, locustags=None):
        self.fp                 = fp
        self._db_fp             = {}
        self.databases          = databases
        self.gpafile            = roary
        self.locustags          = locustags
        self.model              = model
        self.annotations        = annots
        self._drop_columns      = []
        self._rename            = {}


    def __repr__(self):
        statement = f"Model: {self.model}\nDatabases: {', '.join(self.databases)}\nSamples: {', '.join(self.samples)}\nAll: {', '.join(self.names)}"
        return statement
    

    def __len__(self):
        return len(self.names)


    def drop(self, *isolates):
        """
        Drop an isolate from the list of samples.

            Parameters:
                *isolates : str
        """
        for isolate in isolates:
            self.names.remove(isolate)
            self._drop_columns.append(isolate)


    def rename(self, pair):
        """
        Remame an isolate. 

            Parameters:
                pair : dict
                    keys   (str)  : current name
                    values (str)  : new name
        """
        self._rename.update(pair)
        for key, value in pair.items():
            self.names = [name.replace(key, value) for name in self.names]


    @_AllIsolates
    def names(self):
        with open(self.gpafile, encoding='utf-8') as f:
            first_line = f.readline()
        all_isolates = first_line.split("\t")[1:]
        all_isolates[-1] = all_isolates[-1].strip()
        return all_isolates


    @property
    def databases(self):
        return list(self._db_fp.keys())

    @databases.setter
    def databases(self, db):
        if not isinstance(db, dict):
            raise TypeError("Expected a dictionary.")
        self._db_fp.update({name : self._findDBpath(dirname, self.fp) for name, dirname in db.items()})

    @databases.deleter
    def databases(self):
        raise AttributeError("Can't delete attribute")


    @property
    def db_fp(self):
        return self._db_fp

    @db_fp.setter
    def db_fp(self, *args):
        raise AttributeError("Can't set attribute")

    @db_fp.deleter
    def db_fp(self):
        raise AttributeError("Cant delete attribute")

    def _findDBpath(self, organismDB, db_path):
        "Retrieves the full path of an organisms database"
        fp = path.join(db_path, organismDB)
        db_folders = listdir(fp)
        for folder in db_folders:
            matched = re.match(r"\d+\.\d+", folder)
            if matched:
                full_path = path.join(fp, matched[0]) + "//"
                return full_path


    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        if not isinstance(value, str):
            raise TypeError("Expected a string.")
        self._model = value

    @model.deleter
    def model(self):
        raise AttributeError("Can't delete attribute.")


    @property
    def samples(self):
        samples = [sample for sample in self.names if sample not in self.databases]
        return samples
    
    @samples.setter
    def samples(self, value):
        raise AttributeError("Attribute cannot be set.")

    @samples.deleter
    def samples(self):
        raise AttributeError("Can't delete attribute")


def read_yaml(fp):

    """
    Input parameters with YAML
    
    Parameters:
        fp (str) : file path for YAML file.
    Returns:
        Inputs (obj) : Class object of all inputs and attributes of Inputs class.
    """

    import yaml

    with open(fp, 'r') as f:
        yaml_inputs = yaml.safe_load(f.read())

    inputs = Inputs(
        roary=yaml_inputs["roary"],
        model=yaml_inputs["model"],
        databases=yaml_inputs["databases"],
        fp=yaml_inputs["fp"],
        annots=yaml_inputs["annots"],
        locustags=yaml_inputs["locustags"]
    )
    if yaml_inputs["rename"]:
        inputs.rename(yaml_inputs["rename"])
    if yaml_inputs["drop_columns"]:
        inputs.drop(yaml_inputs["drop_columns"])
    
    return inputs


def read_json(fp):
    """
    Input parameters with JSON.

    Parameters:
        fp (str) : file path for JSON file.
    Returns:
        Inputs (obj) : Class object of all inputs and attributes of Inputs class.
    """
    import json

    with open(fp, 'r') as f:
        json_inputs = json.load(f)

    inputs = Inputs(
        roary=json_inputs["roary"],
        model=json_inputs["model"],
        databases=json_inputs["databases"],
        fp=json_inputs["fp"],
        annots=json_inputs["annots"],
        locustags=json_inputs["locustags"]
    )
    try:
        inputs.rename(json_inputs["rename"])
    except: pass
    try:
        inputs.drop(json_inputs["drop_columns"])
    except: pass
    
    return inputs
    
    