"""
Graphical user interface module for tuatara.


Classes
-------

    Editor(*args, **kwargs)
    Scanner(egg)

Functions
---------

    pick(egg)

    
"""


from idlelib import pyshell
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename

from ..nest import get_path, DIR


class Editor(pyshell.EditorWindow):

    """
    Class for handling GUI.
    """

    def __init__(self, *args, **kwargs):
        self.root = tk.Tk()
        self.root.withdraw()
        pyshell.EditorWindow.__init__(self, root=self.root, *args, **kwargs)


class Table(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()
        self.id = 0
        self.iid = 0
        try:
            self.initialiseUI()
        except:
            raise NameError
        

class Scanner(Table):
    
    def __init__(self, egg):
        self.egg = egg
        super().__init__()
    

    def initialiseUI(self):
        self.root.title(f"Scan results - {self.egg}")

        self.tree = ttk.Treeview(self.root, columns=("Matches", "Reactions"))
        self.tree.pack(expand=True, side='left', fill='both')
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.heading("#0", text="Line")
        self.tree.heading("#1", text="Matches")
        self.tree.heading("#2", text="Reaction")

        self.tree.column('#0', width=100, stretch=tk.NO)

        self.treeview = self.tree

        
    def insert_data(self, line, matches, reaction):
        self.treeview.insert('', self.id, iid=self.iid, text=f"Line {line}", values=(matches, reaction))
        self.id += 1
        self.iid += 1


class LPTable(Table):

    def __init__(self):
        super().__init__()
        
    def initialiseUI(self):
        self.root.title(f"LP results")

        self.tree = ttk.Treeview(self.root, columns=("Name", "Reaction", "From", "To"))
        self.tree.pack(expand=True, side='left', fill='both')
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.heading("#0", text="Flux")
        self.tree.heading("#1", text="Name")
        self.tree.heading("#2", text="Reaction")
        self.tree.heading("#3", text="From")
        self.tree.heading("#4", text="To")

        self.tree.column('#0', width=100, stretch=tk.NO)
        self.treeview = self.tree


    def insert_data(self, flux, name, reaction, From, to):
            self.treeview.insert('', self.id, iid=self.iid, text=f"{flux}", values=(name, reaction, From, to))
            self.id += 1
            self.iid += 1


def _ask_spy_file():
    egg_path = askopenfilename(
                title='tuatara - Please select a .spy file.',
                filetypes=[('ScrumPy Files', "*.spy")],
                initialdir=DIR
                )
    return egg_path


def pick(egg):
    """
    Load an egg into the editor window.
    """
    egg_path = get_path(egg)
    Editor(filename=egg_path)
    

