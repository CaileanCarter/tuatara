"""
Nest building module for tuatara.



"""

# TODO: add logging
# TODO: Write docstring
# TODO: direct logging to register
# TODO: conflict reactions should be commented (or left to user to deal with?)


import csv
import logging
import mmap
import re
import sys
from collections import namedtuple
from os import devnull, getcwd, listdir, path

import numpy as np
import pandas as pd
from ScrumPy.Bioinf import PyoCyc
from ..tools.utils import (    
                    remove_suffix,
                    split_reaction, 
                    list_identical, 
                    str_identical, 
                    add_prefix,
                    HidePrints,
                    str_len
                    )
from ..nest import DIR

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class _ToNest:
    """
    A context manager class for building .spy files for an egg.
    All material passed to _Writer is written to file upon exiting context manager.

    Use:
    -----------
    
    with _ToNest(egg) as tnt:
        ***code block***
    

    Methods
    -------
    zero_flux(reactions)
    zero_flux_unidentified(reactions)
    add_reactions(reactions)
    add_conflicts(self, conflicts)

    """

    def __init__(self, egg):

        self._name          = egg
        self._file          = None
        self._entry         =   (   "# This file was made with the tuatara package and should not be\n"
                                    "# directly added to a ScrumPy model. Use the tools provided by\n"
                                    "# tuatara to add to interact with model. \n\n\n")
        self._zero_flux     = "########################### REACTIONS WITH ZERO FLUX ###########################\n"
        self._unidentified  = "###################### REACTIONS NOT FOUND IN MODEL FILES ######################\n"
        self._reactions     = "########################### REACTIONS ADDED TO MODEL ###########################\n"
        self._conflicts     = "########################### REACTIONS WITH CONFLICTS ###########################\n"
        # statements are flanked with a single space, uppercase and centered using .center(80, "#")

    def __enter__(self):
        self._file = open(f"{DIR}/{self._name}.spy", "w+")

        self._file.write(self._entry)
        self._file.write(f"# Egg ID: {self._name}\n\n")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        "Writes to .spy file for egg upon exiting context manager"
        self._file.write("\n\n\n".join([
                                    self._conflicts,
                                    self._unidentified,
                                    self._zero_flux,
                                    self._reactions
                                    ]))
        self._file.close()

    def zero_flux(self, reactions: list):
        """Add reactions to be zero flux"""
        self._zero_flux += "\n\n".join(reactions)

    def zero_flux_unidentified(self, reactions: list):
        """Same as zero_flux but for reactions not found in model"""
        self._unidentified += "\n\n".join(reactions)

    def add_reactions(self, reactions: list):
        """Add reactions to .spy file"""
        self._reactions += "\n\n".join(reactions)

    def add_conflicts(self, conflicts: list):
        """Add a reaction but flag as having confliction between databases"""
        for conflict in conflicts:
            for rUID, reactions in conflict.items():
                self._conflicts += f"\n# Conflict found for reaction: {rUID}\n"
                for order, reaction in enumerate(reactions, start=1):
                    self._conflicts += f"# Conflict {order}\n {reaction}\n"


class BuildNest:

    """
    A class for creating .spy files for each egg.

    ...
    Parameters:
        inputs (obj) : A class object containing all necessary inputs.

    
    Attributes
    ----------
    model : str
        Name of organism used as model as stated in roary files

    databases : list
        List of database organism IDs

    db : dict
        key : database organism ID
        value : database file path

    samples : list
        List of eggs found in roary gene presence/absence file (excluding database organisms)

    names : list
        List of all eggs found in roary gene presence/absence file

    Methods
    -------
    No methods

    """

    def __init__(self, inputs):

        # private imported attributes from inputs
        self._db =          inputs._db_fp
        self._dbs =         inputs.databases
        self._rename =      inputs._rename
        self._col_drop =    inputs._drop_columns
        self._model =       inputs.model
        self._gpa_fp =      inputs.gpafile
        self._locustags =   inputs.locustags
        self._annots =      inputs.annotations
        
        # private class attributes
        self._hashtable =        None
        self._reaction_master =  {}
        self._conflicts =        {}
        self._accessory =        None

        # public class attributes
        self.eggs = {}

        # method calls
        self._log_inputs()
        self.__call__()


    def __call__(self):

        gpa = pd.read_table(self._gpa_fp, index_col=0)                                               # read gene presence/absence file
        if self._rename:
            gpa = gpa.rename(columns=self._rename)
        if self._col_drop:
            gpa = gpa.drop(self._col_drop, axis=1)

        log.info("Number of genes present in roary file: " + str_len(gpa))
        gpa = self._merge_duplicate_genes(gpa)                                                       # Merge duplicated genes
        log.info("Number of genes after flattening: " + str_len(gpa))

        gpa = gpa.replace(0, np.NaN)                                                                # Replace 0 with NaN so they're not seen as values
        self._accessory = gpa[~gpa.notna().all(axis=1)]                                              # Remove core genes nothing needs to be done.

        log.info("Size of accessory genome (databases included): " + str_len(self._accessory))
        self._calc_coverage()

        self._accessory = self._accessory[~self._accessory[self._dbs].isna().all(axis="columns")]      # Get only genes present in a database
        self._hashtable = self._build_reference_table()

        self._reaction_master = {gene : {} for gene in self._accessory.index}
        log.info("Loading databases... this may take a moment.")
        for dname in self._dbs:
            self._buildMasterReaction(dname)
        self._log_reactions()

        for egg in self._accessory[self._accessory.columns.difference(self._dbs)].columns:
            with _ToNest(egg) as tnt:
                egg_df = self._accessory[[self._model, egg]]

                inmodel, notinmodel = self._verify_in_model(
                    egg_df[egg][egg_df[self._model].notna() & egg_df[egg].isna()].index
                    )
                tnt.zero_flux(inmodel)
                tnt.zero_flux_unidentified(notinmodel)

                reacs_to_add, reacs_with_conflicts = self._reactions_to_add(
                    egg_df[egg][egg_df[self._model].isna() & egg_df[egg].notna()].index
                )
                tnt.add_reactions(reacs_to_add)
                tnt.add_conflicts(reacs_with_conflicts)

                statement = "\n".join([
                                    "Egg ID: "                                                              + egg,
                                    "Reactions with conflicts: "                                            + str_len(reacs_with_conflicts),
                                    "Number of reactions absent in egg but were not found in model files: " + str_len(notinmodel),
                                    "Number of reactions absent in egg: "                                   + str_len(inmodel),
                                    "Number of reactions added: "                                           + str_len(reacs_to_add)
                                    ])

                self.eggs[egg] = statement
                                            

    #---------------------------------------------
    #internal logging
    def _log_inputs(self):
        log.debug("Model: "                     + self._model)
        log.debug("Database organisms: "        + ", ".join(self._dbs))
        log.debug("Database filepaths:\n\t"     + "\t\n".join([f"{db} : {fp}" for db, fp in self._db.items()]))
        log.debug("Roary file: "                + self._gpa_fp)
        log.debug("Locustags: "                 + self._locustags)
        log.debug("Annotations: "               + self._annots)
        log.debug("Rename: \n\t"                + "\t\n".join([f"{db} : {fp}" for db, fp in self._rename.items()]))
        log.debug("Drop columns: "              + ", ".join(self._col_drop))


    def _calc_coverage(self):
        "Calculates database coverage of all genes present"
        notindb = self._accessory[self._accessory[self._dbs].isna().all(axis="columns")].index
        indb = self._accessory[~self._accessory.index.isin(notindb)].index

        missing = len(notindb)
        per_coverage = 100 - (len(notindb)/len(indb))*100

        log.info("Percent gene coverage from databases: {:.2f}%".format(per_coverage))
        log.info("Number of genes not covered: " + str(missing))


    def _log_reactions(self):
        number_of_reactions = sum([len(reaction) for reaction in self._reaction_master.values()])
        number_of_conflicts = len(self._conflicts)
        log.info("Total number of reactions collected from databases: " + str(number_of_reactions))
        log.info("                           of which have conflicts: " + str(number_of_conflicts))


    #--------------------------------------------
    #core methods
    def _merge_duplicate_genes(self, gpa):
        # While there is a way of doing this using pandas, it is considerably slower (~14 seconds)
        """Takes gpa DataFrame and merges rows with duplicated gene names. Returns DataFrame."""
        gpa_filtered = {}
        for row in gpa.itertuples():
            gene = remove_suffix(row[0])
            if gene in gpa_filtered.keys():
                gpa_filtered[gene] = np.maximum(gpa_filtered[gene], row[1:])
            else:
                gpa_filtered[gene] = row[1:]

        gpafil = pd.DataFrame.from_dict(gpa_filtered, orient='index', columns=gpa.columns)
        return gpafil


    def _map_tag_db(self):
        """
        Finds the locus tags for each database egg and returns dictionary.
        Returns:
            keys   : locus tag
            values : database organism
        """
        dbtags = {}
        for db in self._dbs:
            dbfile = open(path.join(self._annots, f"{db}.tabular")).readlines()[1]
            tag, *_ = dbfile.split("\t")
            puretag = remove_suffix(tag)
            dbtags.update({puretag : db})
        return dbtags


    def _build_reference_table(self):
        # This is a very long function...
        """
        A method for building a DataFrame where the common gene name from
        Roary gene presence/absence file is translated to the
        respective common gene name in each database. (hashtable)

        ...

        Process:
            1. Retrieve the locus tags for each database organism (map_tag_db())
            2. Database tags are given an order (index) so genes can be allocates to their respective database in a list format
            3. Iterate over the locustag file so for each gene:
                - search for tags relating to database organisms
                - save the database organism locus ID for that gene in an ordered list
            4. Transform into a DataFrame and convert empty strings to np.NaN
            5. For each database organism:
                - open their respective annotation file
                - build a dictionary of locus ID : gene pairs
                - rename the locus IDs in DataFrame for given database organism to their given gene name
        """
        dbtags = self._map_tag_db()
        order = {tag : index for index, tag in enumerate(dbtags.keys())}

        gene_regex = r"^\w+[^_\-\d:]"
        tag_regex = "|".join([item + r"_\d+" for item in dbtags.keys()])

        # reads the roary file and gets the tags for each gene
        tidy_locusid = {}
        for line in open(self._locustags).readlines():

            gene = re.match(gene_regex, line)
            values = re.findall(tag_regex , line)
            gene = gene.group(0)

            if gene != "group" and gene in self._accessory.index:
                row = [''] * len(dbtags) if gene not in tidy_locusid.keys() else tidy_locusid[gene]
                for locus in values:
                    idtag = remove_suffix(locus)
                    index = order[idtag]
                    if row[index]: 
                        row[index] += ", " + locus
                    else:
                        row[index] = locus
                tidy_locusid.update({gene : row})

        self._hashtable = pd.DataFrame.from_dict(tidy_locusid, orient='index', columns=dbtags.values())
        self._hashtable = self._hashtable.replace('', np.NaN)

        # reads the annotation file for each database and renames the locus tags in the main df to the corresponding gene name
        for db in self._dbs:
            with open(path.join(self._annots, f"{db}.tabular"), newline='') as f:
                f_csv = csv.reader(f, delimiter='\t')
                headings = next(f_csv)
                Row = namedtuple('Row', headings)

                name_reference = {}
                for r in f_csv:
                    row = Row(*r)
                    if row.gene: # if gene present for locus tag
                        gene = remove_suffix(row.gene)
                        name_reference.update({row.locus_tag : gene})
                    else:
                        name_reference.update({row.locus_tag : np.NaN})

            def rename(x):
                LIDs = x.split(", ")
                names = ""
                for LID in LIDs:
                    gene_name = name_reference[LID]
                    if isinstance(gene_name, float):
                        pass
                    elif not names:
                        names = gene_name
                    elif gene_name not in names:
                        names += ", " + gene_name
                return names if names else np.NaN

            gene_present = self._hashtable[db].notna()
            self._hashtable.loc[gene_present, db] = self._hashtable.loc[gene_present, db].apply(rename)

        return self._hashtable

    #--------------------------------------------
    #reactions handling
    def _getDBreacs(self, DBname):
        """
        Given a database organism, this function gets all the functions from its database and returns a dictionary.

            Parameters:
                DBname (str) : name of database organism

            Returns:
                reaction_map (dict) : 
                    keys (str) : common gene name
                    values (dict) : 
                        keys (str) : reaction unique ID
                        values (str) : reaction as ScrumPy
        """
        
        fp = self._db[DBname]
        reaction_map = {}
        with HidePrints():
            db = PyoCyc.Organism(data="data", Path=fp)
     
        UIDs = [gene['UNIQUE-ID'][0] for gene in db.dbs['GENE'].values()]
        for UID in UIDs:
            try:
                gene = db.dbs['GENE'][UID]['COMMON-NAME'][0]
            except:
                gene = False
            
            if gene:
                try:
                    reactions = db.dbs['GENE'][UID].GetReactions()
                except:
                    reactions = False
                
                if reactions:
                    r = {reac.UID : reac.AsScrumPy() for reac in reactions if "!" not in reac.AsScrumPy()}
                    if r:
                        reaction_map[gene] = r
        
        return reaction_map
  

    def _buildMasterReaction(self, dname):
        """Merges all the genes with reactions from databases, takes database organism name."""
        reaction_map = self._getDBreacs(dname)
        genes_present = self._hashtable[dname].notna()
        dbseries = self._hashtable.loc[genes_present, dname]
        for index, value in dbseries.items():
            try:
                reactions = reaction_map[value]
            except KeyError:
                continue
            
            for UID, reaction in reactions.items():
                if UID in self._reaction_master[index]:

                    if reaction != self._reaction_master[index][UID]:

                        reac_a = split_reaction(self._reaction_master[index][UID])
                        reac_b = split_reaction(reaction)

                        subs = list_identical(reac_a.substrates, reac_b.substrates)
                        dirs = str_identical(reac_a.direction, reac_b.direction)
                        prods = list_identical(reac_a.products, reac_b.products)

                        if not all([subs, dirs, prods]):
                            self._add_conflict(index, UID, self._reaction_master[index][UID], reaction)
                else:
                    self._reaction_master[index].update({UID : reaction})
 

    def _add_conflict(self, gene, rUID, reac_a, reac_b):
        """
        Adds two reactions to the conflict dictionary when identified 
        as having conflicting reaction stoichiometry.

        Parameters:
            gene (str) : common gene name
            rUID (str) : reaction unique ID
            reac_a (str) : reaction A in ScrumPy
            reac_b (str) : reaction B in ScrumPy
        """

        try:
            conflict = self._conflicts[gene]
        except:
            self._conflicts[gene] = {rUID : [reac_a, reac_b]}
            return

        if rUID in conflict.keys():
            conflict[rUID] += [reaction for reaction in [reac_a, reac_b] if reaction not in conflict[rUID]]
        else:
            conflict[rUID] = [reac_a, reac_b]
        
        self._conflicts[gene].update(conflict)


        # if gene in self._conflicts.keys():
        #     if rUID in self._conflicts[gene].keys():
        #         for reaction in [reac_a, reac_b]:
        #             if reaction not in self._conflicts[gene][rUID]:
        #                 self._conflicts[gene][rUID].append(reaction)
        #     else:
        #         self._conflicts[gene].update({rUID : [reac_a, reac_b]})
        # else:
        #     self._conflicts[gene] = {rUID : [reac_a, reac_b]}


    #--------------------------------------------
    #egg and model handling
    def _egg_reactions(self, series):
        "From an egg's series (from inmodel), this generates a dict of reactions which are absent in egg."
        reactions = {}
        for gene in series:
            reacs = self._reaction_master[gene]
            if reacs:
                reactions.update(reacs)
        return reactions


    def _verify_in_model(self, series):
        """
        Input: pd.Series.index of egg with genes present but absent in model.
        Returns: Two lists of ScrumPy formatted reactions; [0]reactions in model files, [1]reactions not in model files
        """
        cwd = getcwd()
        reactions = self._egg_reactions(series)
        spy_files = filter(lambda x : x.endswith(".spy"), listdir(cwd))
        in_model_files = []

        for spy_file in spy_files:
            open_spy = path.join(cwd, spy_file)

            with open(open_spy, 'rb', 0) as fspy, \
                    mmap.mmap(fspy.fileno(), 0, access=mmap.ACCESS_READ) as search_file:
                
                for rUID, reaction in reactions.items():
                    if search_file.find(bytes(rUID, encoding='utf8')) != -1 and reaction not in in_model_files:
                        in_model_files.append(reaction)
        
        notin_model_files   = [add_prefix(reaction) for reaction in reactions.values() if reaction not in in_model_files]
        model_reactions     = [add_prefix(reaction) for reaction in in_model_files]
        return model_reactions, notin_model_files


    def _reactions_to_add(self, series):
        reacs_to_add = []
        reacs_with_conflicts = []

        for gene in series:
            if gene in self._conflicts.keys():
                reacs_with_conflicts.append(self._conflicts[gene])
            elif self._reaction_master[gene]:
                for reaction in self._reaction_master[gene].values():
                    reacs_to_add.append(reaction)
        return reacs_to_add, reacs_with_conflicts

    #--------------------------------------------
    #attributes
    
    @property
    def names(self):
        return list(self._accessory.columns)

    @names.setter
    def names(self, value):
        raise AttributeError("Can't set attribute.")

    @names.deleter
    def names(self):
        raise AttributeError("Can't delete attribute")


    @property
    def databases(self):
        return self._dbs

    @databases.setter
    def databases(self, db):
        raise AttributeError("Can't set attribute.")
      

    @databases.deleter
    def databases(self):
        raise AttributeError("Can't delete attribute")


    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, *args):
        raise AttributeError("Can't set attribute.")

    @db.deleter
    def db(self):
        raise AttributeError("Cant delete attribute.")


    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        raise AttributeError("Can't set attribute.")

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

### END ###
