"""
Model testing module for tuatara

---

Classes
-------

    WatchList
    Scan(egg, from_file, stdout, **kwargs)
"""

import logging
import pickle
from functools import wraps
from os import path, remove

from flashtext import KeywordProcessor

from . import Editor, Scanner, _ask_spy_file
from ..nest import get_path

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

DIR = path.dirname(path.realpath(__file__))
PATH = path.join(DIR, "watchlist.tua")
tmp_path = path.join(DIR, "watchlist.txt")


class WatchList:

    """
    The watchlist is a list of unwanted items to look for in a .spy file.

    The list can be edited and a new list can be defined.


    Methods
    -------

    str_watchlist(watchlist):
        Return a string representation of the watchlist.
    open_watchlist():
        Returns the watchlist as a list.
    close_watchlist(watchlist):
        Saves watchlist to file.
    
    Class methods
    -------------
    tidy():
        Removes duplicates from the watchlist and orders the items alphabetically.
    edit():
        Opens editor window to edit the watchlist
    commit():
        Commit changes made in editor window to watchlist
    dump(items):
        Add list of items to watchlist
    dumps(item):
        Add string item to watchlist
    drop(items):
        Remove list of items from watchlist
    drops(item):
        Remove string item from watchlist
    wipe():
        Clear the watchlist
    from_file(fp, replace=False):
        Add items to watchlist from a text file or replace existing watchlist.
    """

    def __len__(self):
        return len(self.open_watchlist())
    
    def __repr__(self):
        return "tua.WatchList.edit()"
    
    def str_watchlist(self, watchlist : list) -> str: return "\n".join(watchlist)

    
    def open_watchlist(self) -> list:
        """Returns the watchlist as a list."""
        with open(PATH, 'rb') as filehandle:
            watchlist = pickle.load(filehandle)
        return watchlist

    
    def close_watchlist(self, watchlist: list):
        """Saves watchlist to file."""
        with open(PATH, 'wb') as filehandle:
            pickle.dump(watchlist, filehandle)


    def _make_tmp_file(self, swlt):
        """
        Creates a temporary text file of the watchlist for editor window. 
        Takes string formatted watchlist as argument.
        """
        with open(tmp_path, 'w', encoding='utf-8') as tmp:
            tmp.write(swlt)
        return tmp_path


    @classmethod
    def tidy(cls):
        """Removes duplicates from the watchlist and orders the items alphabetically."""
        watchlist = cls.open_watchlist(cls)
        watchlist = list(set(watchlist))
        watchlist.sort()
        cls.close_watchlist(cls, watchlist)


    @classmethod
    def edit(cls):
        """Opens editor window to edit the watchlist. Save changes in the editor window and commit them to WatchList using commit method."""
        watchlist = cls.open_watchlist(cls)
        swlt = cls.str_watchlist(cls, watchlist)
        tmp_path = cls._make_tmp_file(cls, swlt)
        Editor(filename=tmp_path)


    @classmethod
    def commit(cls):
        """Commit changes made in editor window to watchlist"""
        # TODO: remove comment when development complete 
        log.info("Committing changes...")
        watchlist = []
        for line in open(tmp_path, 'r').readlines():
            line = line.strip()
            if line:
                watchlist.append(line)
        cls.close_watchlist(cls, watchlist)
        # remove(tmp_path)
        log.info("Changes have been made.")
        log.debug(f"{tmp_path} has been removed.")


    @classmethod
    def dump(cls, items : list):
        """Add list of items to watchlist"""
        watchlist = cls.open_watchlist(cls)
        watchlist += items
        cls.close_watchlist(cls, watchlist)
    

    @classmethod
    def dumps(cls, item : str):
        """Add string item to watchlist"""
        cls.dump([item])


    @classmethod
    def drop(cls, items : list):
        """"Remove list of items from watchlist"""
        watchlist = cls.open_watchlist(cls)
        for item in items:
            watchlist.drop(item)
        cls.close_watchlist(cls, watchlist)


    @classmethod
    def drops(cls, item : str):
        """"Remove string item from watchlist"""
        cls.drop([item])
        

    @classmethod
    def wipe(cls):
        """"Clear the watchlist"""
        watchlist = []
        cls.close_watchlist(cls, watchlist)
        log.info("Watchlist has been wiped")

    
    @classmethod
    def from_file(cls, fp, replace=False):
        """"
        Add items to watchlist from a text file or replace existing watchlist.
        
            Parameters:
                fp (str) : file path
                replace (bool) : replace existing watchlist with file
        """
        new_items = []
        for line in open(fp).readlines():
            line = line.strip()
            if line:
                new_items.append(line)
        if replace:
            cls.close_watchlist(cls, new_items)
        else:
            cls.dump(new_items)


def helper(cls):
    @wraps(cls)
    def wrapper(*args, debug=False, **kwargs):
        if debug:
            log.info(f"Calling {cls.__name__}")
        c = cls.__new__(cls)
        return c(*args, **kwargs)
    return wrapper


@helper
class scan(WatchList):

    """
    Scan .spy file for unwanted items. Launches a table showing line, matches and reaction.


        Parameters:
            egg (str) : egg ID
            from_file (bool) : input own file through a file explorer
            file_path (str) : provide file path for .spy file
            stdout (bool) : print results
    """


    def __call__(self, egg=False, from_file=False, file_path=None, stdout=False, **kwargs):
        watchlist = self.open_watchlist()

        keyword_processor = KeywordProcessor()
        keyword_processor.add_keywords_from_list(watchlist)

        if egg:
            egg_path = get_path(egg)
        elif from_file:
            egg_path = _ask_spy_file()
        elif file_path:
            egg_path = file_path
        else:
            raise ValueError("Expected egg, from_file or file_path argument.")

        gui = Scanner(egg if egg else egg_path)

        for line, reaction in enumerate(open(egg_path).readlines(), start=1):
            if reaction and not reaction.startswith('#'):
                match = keyword_processor.extract_keywords(reaction)
                if match:
                    matches = ', '.join(match)
                    reaction = reaction.strip()
                    gui.insert_data(line, matches, reaction)

                    if stdout:
                        log.info(f"Line {line}: {', '.join(match)} \n{reaction}")

        


