"""
Nest keeper module for tuatara
---
Performs maintenance of the nest, attribute management and core nest functions.


"""

import logging
import pickle
from datetime import datetime
from os import path, listdir, remove

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

DIR = path.join(
    path.dirname(path.realpath(__file__)),
    "eggs")


def get_path(egg : str) -> str:
    """Takes egg ID and returns its filepath"""
    egg_path = path.join(DIR, f"{egg}.spy")
    return egg_path


def check_eggsdir_exists() -> bool: return path.isdir(DIR)

def check_egg_exists(egg:str) -> bool: return path.isfile(path.join(DIR, f"{egg}.spy"))


class RegisterManager:

    def __init__(self):
        self._regPATH = path.join(
            path.dirname(path.realpath(__file__)),
            "register.tua")
        
    def __enter__(self):
        self._register = self._open_register()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with open(self._regPATH, 'wb') as filehandle:
        #     pickle.dump(self._register, filehandle)
        self._close_register()

    def _open_register(self):
        with open(self._regPATH, 'rb') as filehandle:
            _register = pickle.load(filehandle)
        return _register
    
    def _close_register(self, updated_register=None):
        with open(self._regPATH, 'wb') as filehandle:
            if updated_register:
                pickle.dump(updated_register, filehandle)
            else:
                pickle.dump(self._register, filehandle)


    def _date_stamp(self):
        date = datetime.now()
        strdate = date.strftime("%d/%m/%Y %H:%M")
        return strdate


    def _record(self, *args, egg=None, **kwargs):
        #TODO tidy me.
        """Record items to the register"""
        CLASSMETHOD = False
        try:
            _register = self._register              # get register from instance if called from context manager
        except:
            _register = self._open_register()       # else open register
            CLASSMETHOD = True

        try:
            egg_record = _register[egg]
        except:
            log.info(f"No record of {egg} exists, starting new record.")
            egg_record = {
                "name" : egg,
                "active" : True,
                "renamed" : False,
                "file" : f"{egg}.spy",
                "date deleted" : None,
                "checked" : False,
                "contents" : {}
            }
            

        for arg in args:
            if arg == "date created":
                egg_record.update({arg : self._date_stamp()})
            else:
                log.warning(f"Unexpected argument: {arg}")

        for key, value in kwargs.items():

            if key == "contents":
                egg_record[key].update({"last checked" : self._date_stamp()})
                egg_record[key].update({subkey : subvalue for subkey, subvalue in value.items()})

            else:
                egg_record.update({key : value})


        _register[egg].update(egg_record)
        if CLASSMETHOD:
            self._close_register(updated_register=_register)
        else:
            self._register = _register


    @classmethod     
    def _single_update(cls, *args, egg=None, **kwargs):
        """This is a single use method same as _record, not to be used under context manager."""
        cls._record(cls, *args, egg=egg, **kwargs)

    def _rename(self, pairs: dict):
        #TODO write me.
        pass


class nest(RegisterManager):

    def __init__(self):
        super().__init__()

        self.eggs = [egg for egg in listdir(DIR) if egg.endswith(".spy")]


    def __len__(self):
        return len(self.eggs)

    def __iter__(self):
        return iter(self.eggs)

    @classmethod
    def rename(cls, pairs: dict):
        """
        Rename an egg.

            Parameters:
                pairs (dict) : {old name : new name}
        """
        for index, (oldname, newname) in enumerate(pairs.items(), start=1):
            log.info(f"{index}. {oldname} has been renamed to {newname}.")
        cls._rename(cls, pairs)

    @classmethod
    def crack(egg : str):
        #TODO work with register
        """
        Remove an egg from the nest.

        WARNING: This cannot be undone. 

            Parameters:
                egg (str) : egg ID
        """
        log.warning("User is requesting to delete an egg.")
        _statement = f"Are you sure you want to delete {egg}?\nThis cannot be undone (y/n): "

        answer = input(_statement)
        if answer == "y":
            egg_path = get_path(egg)
            remove(egg_path)
            log.info(f"{egg} has been cracked.")
