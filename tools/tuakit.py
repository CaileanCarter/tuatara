import logging
import re
from collections import defaultdict, namedtuple
from operator import itemgetter
from os import path

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import numpy as np
import pandas as pd
from flashtext import KeywordProcessor
from ScrumPy.Bioinf import PyoCyc

from ..core.GUI import Editor, LPTable
from .utils import HidePrints, SetUtils, split_reaction

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# TODO: make a standalone gist file out of this module, will need to somehow include dependencies? 
# Or make as a standalone package.

class LP:

    def __init__(self): raise TypeError("Object cannot be initialised.")

    @staticmethod
    def build(
                model,
                reaction=None,
                fluxdict=None,
                flux=1,
                block_uptake=False,
                suffix="_tx",
                obj="min",
                solve=True
                ):
        """
        Build linear programme from model.
        
            Parameters:
                model (obj) : model
                reaction (str) : name of reaction
                fluxdict (dict) : flux dictionary
                flux (int) : flux value for reaction
                block_uptake (bool) : block transporters
                suffix (str) : block transporters with given suffix ('_tx' for all transporters; '_mm_tx' for media transporters)
                obj (str) : linear programme objective ("min")
                solve (bool) : solve LP

            Returns:
                lp (obj) : linear programme of model
        """
        # Does not have capacity to deal with biomass data -> use BuildLP script
        #TODO: implement biomass data
        
        lp = model.GetLP()

        if obj == "min":
            lp.SetObjDirec("Min")
            lp.SetObjective(model.sm.cnames)   # minimise total flux

        if block_uptake:
            lp.SetFixedFlux({tx : 0 for tx in filter(lambda x: x.endswith(suffix), model.sm.cnames)})
        if reaction:
            lp.SetFixedFlux({reaction : flux})
        if fluxdict:
            lp.SetFixedFlux(fluxdict)

        if solve:
            lp.Solve()
            lp = lp.GetPrimSol()

        return lp


    @staticmethod
    def prints(model, lp):
        """Print lp with flux value and reactions. \nParameters: model and lp."""
        for key, value in lp.items():
            print(value, model.smx.ReacToStr(key))


    @staticmethod
    def find(lp, text): return list(filter(lambda x : text in x, lp.keys()))
    #FIXME: what is this even for??


    @staticmethod
    def show(model, lp):
        """
        View LP in an Editor Window. Ideal for LPs with large contents without slowing down shell.

            Parameters:
                model (obj) : model
                lp (obj) : lp
        """
        DIR = path.dirname(path.realpath(__file__))
        PATH = path.join(DIR, "LP.tua")

        with open(PATH, 'w') as LPfile:
            for key, value in lp.items():
                LPfile.write("{:.2f} {}\n".format(value, model.smx.ReacToStr(key)))

        Editor(filename=PATH)


    @staticmethod
    def tabulate(model, lp, output=None, exclude=None, include=None):
        """
        Show LP in a table 

            Parameters:
                model (obj) : model
                lp (obj) : lp
                output (str) : (optional) output to a text file as tab seperated
                exclude (list) : exclude given metabolites
                include(list) : include only given metabolites
            
        """        
        tableGUI = LPTable()

        if exclude == "default":
            exclude = ["NADP", "NAD", "NADPH", "Pi", "PROTON", "WATER", "ADP", "ATP", "NADH", "PPI"]

        def filter_reaction(items):
            if exclude:
                return [item for item in items if item not in exclude]
            elif include:
                return [item for item in items if item in include]
            else:
                return items
        
        if output:
            filehandle = open(output, 'w')
            filehandle.write("Flux\tName\tReaction\tFrom\tTo")
        
        table = {}
        for reaction, flux in lp.items():
            table.update({reaction: {
                                "flux" : "{:.2f}".format(flux),
                                "reaction" : None,
                                "from" : [],
                                "to" : []
                                }})
            
            reac = split_reaction(model.smx.ReacToStr(reaction)[:-2])
            table[reaction]["reaction"] = " + ".join(reac.substrates) + " " + reac.direction + " " + " + ".join(reac.products)

            substrates = filter_reaction(model.smx.Reactants(reaction))
            products = filter_reaction(model.smx.Products(reaction))

            for reaction_b in lp.keys():
                if reaction_b != reaction:
                    substrates_b = filter_reaction(model.smx.Reactants(reaction_b))
                    products_b = filter_reaction(model.smx.Products(reaction_b))

                    if SetUtils.does_intersect(substrates, products_b):
                        table[reaction]["from"].append(reaction_b)
                    if SetUtils.does_intersect(substrates_b, products):
                        table[reaction]["to"].append(reaction_b)

            result = table[reaction]

            if any([result["from"], result["to"]]):
                tableGUI.insert_data(
                                result["flux"],
                                reaction,
                                result["reaction"],
                                ", ".join(result["from"]),
                                ", ".join(result["to"])
            )
            if output:
                filehandle.write("{flux}\t{name}\t{reaction}\t{From}\t{To}".format(
                            flux=result["flux"],
                            name=reaction,
                            reaction=result["reaction"],
                            From=", ".join(result["from"]),
                            To=", ".join(result["to"])
                ))

        if output:
            filehandle.close()


    @staticmethod
    def plot(model, lp, exclude=None, include=None):

        """
        Plot LP as a network graph.

            Parameters:
                model (obj) : model
                lp (obj) : lp
                exclude (list) : a list of metabolites to exclude (or use 'default')
                include (list) : a list of metabolites to only include

        """

        G = nx.Graph()
        G.add_nodes_from([reac for reac in lp.keys()])

        reactions = {reac : {
                                "reactants" : model.smx.Reactants(reac),
                                "products" : model.smx.Products(reac)
                                } for reac in lp.keys()
                                }

        if exclude == "default":
            exclude = ["NADP", "NAD", "NADPH", "Pi", "PROTON", "WATER", "ADP", "ATP", "NADH", "PPI"]

        def filter_reaction(items):
            if exclude:
                return [item for item in items if item not in exclude]
            elif include:
                return [item for item in items if item in include]
            else:
                return items

        for reaction, values in reactions.items():
            products = filter_reaction(values["products"])
            for reaction_b, values_b in reactions.items():
                reactants = filter_reaction(values_b["reactants"])
                if products and reactants and SetUtils.does_intersect(products, reactants):
                    G.add_edge(reaction, reaction_b)
        
        hub = sorted(G.degree(), key=itemgetter(1))[-1][0]
        ego_plot = nx.ego_graph(G, hub)
        nx.draw(ego_plot, with_labels=True, pos=nx.spring_layout(G), edge_color='c')
        plt.show()


    @staticmethod
    def compare(df, core=True):

        try:
            df = df.to_frame()
        except AttributeError:
            pass

        def get_keys(x): return list(x.keys())

        df["AsList"] = df.iloc[:,0].apply(get_keys)

        reactions = set( val for dic in df["AsList"] for val in dic )
        # print(s)

        master = {name : {value : 0 for value in reactions} for name in df.index}
        for name, values in df["AsList"].iteritems():
            for val in values:
                master[name][val] = 1

        df_m = pd.DataFrame.from_dict(master)
        if not core:
            df_m = df_m[(df_m.T != 1).any()]
        sns.clustermap(df_m, cmap="mako")
        plt.show()


class Model:
    #TODO: move to nest scripts?

    def __init__(self): raise TypeError("Object cannot be initialised.")
        
    
    @staticmethod
    def find(model, keyword, types):
        """
        Easily find a metabolite or reaction by a keyword.
        
            Parameters:
                model (obj) : model
                keyword (str) : keyword to search for
                types (str|tuple) : 'met' or 'reac'

            Returns:
                matches (list) : list of matches
        """
        keyword_processor = KeywordProcessor()
        keyword_processor.add_keyword(keyword)

        matches = []

        if "met" in types:
            for met in model.smx.rnames:
                match = keyword_processor.extract_keywords(met)
                if match: matches.append(met)

        if "reac" in types:
            for reac in model.smx.cnames:
                match = keyword_processor.extract_keywords(reac)
                if match: 
                    matches.append(reac)

        return matches


    @staticmethod
    def merge_models(model_a, model_b):
        #TODO: add to api reference
        #FIXME: this would edit the original models, make it so entirely new model is made.
        #FIXME: I doubt this script works anymore, is it worth having?
        model_a.md.Reactions.update(model_b.md.Reactions)
        model_a.md.Metabolites.update(model_b.md.Metabolites)
        for x in model_b.md.xMetabolites:
            if not x in model_a.md.xMetabolites:
                model_a.md.xMetabolites.append(x)
        model_a.md.QuoteMap.update(model_b.md.QuoteMap)
        model_a.__init__(model_a.md)


    @staticmethod
    def check_imbals(m, db, reacs=None):
        #TODO: add to api reference
        """
        Check for imbalances in reactions.

            Parameters:
                m (obj) : model
                db (obj) : database
                reacs (list) : list of reactions

            Returns:
                rv (dict) : reaction imbalances
        """

        rv = {}
        if not reacs:
            reacs = filter(lambda x: not x.endswith("_tx"), m.smx.cnames)
        for reac in reacs:
            stod = m.smx.InvolvedWith(reac)
            imbal = db.dbs['Compound'].AtomImbal(stod)
            if imbal:
                rv[reac] = imbal
        return rv  


    @staticmethod
    def check_biomass_production(model, reactions=None, flux=-1, suffix="_BM_tx", **kwargs):
        #TODO: add to api reference
        """
        Check model's biomass production by .

            Parameters:
                model (obj) : model
                reactions (list) : dictionary of reaction flux
                flux (int) : reaction flux
                suffix (str) : suffix denoting a biomass transporter
                **kwargs : keyword arguments for build LP
            Returns:
                rv (dict) : dictionary of biomass solutions
        """
        rv = {}

        bm = reactions if reactions else filter(lambda x : x.endswith(suffix), model.sm.cnames) 
        
        log.info("Checking biomass production... this may take a minute.")
        for reac in bm:
            with HidePrints():
                sol = LP.build(model, reaction=reac, flux=flux, **kwargs)
            if sol:
                rv[reac] = sol
            else:
                log.info(f"No solution found for {reac}")
        return rv
	

    @staticmethod
    def transporters(model, stdout=None, include=None, only=None):
        """ 
        Get a dictionary of all transporters present in model by suffix.

            Parameters:
                m (obj) : model
                stdout (bool) : print transporters
                include (list) : include suffixes to find in reactions
                only (list) : only show specified suffixes
        
            Returns:
                reactions (dict) : reaction suffix (key) and reactions (values : list)

        Transporter tags:
            _tx        = all
            s_tx       = optional-substrates
            bm_tx      = biomass
            aa_bm_tx   = amino acids
            nt_bm_tx   = nucleotides
            w_bm_tx    = cell wall
            l_bm_tx    = cell lipids
            vit_bm_tx  = biomass specific vitamins
            co_bm_tx   = biomass specific cofactors
            f_tx       = fermentation
            em_tx      = essential micronutrient
            n_tx       = nitrogen source
            sf_tx      = substrate/fermentation (transports met which is both f-product and substrate)
            sup_tx     = supplementary nutrients e.g. vitamins
            hp_tx      = heterologous product
        """

        suffixes = ["_tx","s_tx","bm_tx","aa_bm_tx","nt_bm_tx","w_bm_tx","l_bm_tx",
                    "vit_bm_tx","co_bm_tx","f_tx","em_tx","n_tx","sf_tx","sup_tx","hp_tx"]
        if only:
            suffixes = only
        elif include:
            suffixes += include
        reactions = {suffix : [] for suffix in suffixes}

        for reaction in model.sm.cnames:
            result = set((suffix for suffix in suffixes if reaction.endswith(suffix)))
            if result:
                for transporter in result:
                    reactions[transporter].append(reaction)
        
        if stdout:
            log.info("Suffix \tNumber of reactions\n---------------------------------------------------")
            for suffix, reaction_list in reactions.items():
                log.info("{0:<10} {1:>7.0f}".format(suffix, len(reaction_list)))

        return reactions


    #get metabolites from list of reactions
    @staticmethod
    def reac_to_mets(model, reacs: list): return set((met for met in model.sm.InvolvedWith(reac) for reac in reacs))


    @staticmethod
    def connects(model):
        #TODO: add to api reference
        connected = {met : model.sm.Connectedness(met) for met in model.sm.rnames}
        return sorted(connected.items(), key=lambda c:c[1], reverse=True)


    @staticmethod
    def count_enzsubsets(model):
        #TODO: add to api reference

        subsets_dict = defaultdict(list)
        subsets = model.EnzSubsets()

        for sub, reacs in subsets.items():
            num_reacs = len(reacs)
            if num_reacs <= 5:
                subsets_dict[num_reacs].append(sub)
            else:
                subsets_dict["more"].append(sub)

        return subsets_dict


    @staticmethod
    def summary(model, output=None):
        log.info("Preparing summary... this may take a minute.")
        reacs = len([reac for reac in model.sm.cnames if not reac.endswith("_tx")])
        mets = len(model.sm.rnames)

        transp = Model.transporters(model)

        num_dead = len(model.DeadReactions())
        inPercentD = round(100.0/len(model.sm.cnames)*(len(model.sm.cnames)-num_dead),1)
        
        orph = len(model.OrphanMets())
        inPercentO = round(100.0/len(model.smx.rnames)*(len(model.smx.rnames)-orph),1)
        
        enzsubsets = Model.count_enzsubsets(model)
        connected_metabolites = Model.connects(model)
        cycles = len(model.MaxCycles()) # internal cycles?

        top_ten = "\n\t".join([f"{position} {reac[0]} \twith {reac[1]} connections" for position, reac in enumerate(connected_metabolites[:10], start=1)])

        statement = r"""
        tuatara - summary of model

        MAIN
        Reactions:          {reacs}
        Metabolites:        {mets}
        Dead Reactions:     {num_dead} ({inPercentD}% live)
        Orphan metabolites: {orph} ({inPercentO}% not orphans)
        Internal cycles:    {cycles}

        TRANSPORTERS
        all                                                     {all}
        (s_tx)      optional-substrates                         {stx}
        (bm_tx)     biomass                                     {bmtx}
        (aa_bm_tx)  amino acids                                 {aa_bmtx}
        (nt_bm_tx)  nucleotides                                 {nt_bmtx}
        (w_bm_tx)   cell wall                                   {w_bmtx}
        (l_bm_tx)   cell lipids                                 {l_bmtx}
        (vit_bm_tx) biomass specific vitamins                   {vit_bmtx}
        (co_bm_tx)  biomass specific cofactors                  {co_bmtx}
        (f_tx)      fermentation                                {ftx}
        (em_tx)     essential micronutrient                     {emtx}
        (n_tx)      nitrogen source                             {ntx}
        (sf_tx)     substrate/fermentation                      {sftx}
        (transports metetabolites which is both f-product and substrate)
        (sup)       supplementary nutrients e.g. vitamins       {sup}
        (hp_tx)     heterologous product                        {hptx}
        
        ENZYME SUBSETS (grouped by number of reactions in set)
        One         {one}
        Two         {two}
        Three       {three}
        Four        {four}
        Five        {five}
        More        {more}

        TOP 10 CONNECTED METABOLITES
        {top_ten}

        END
        """.format(
            reacs=reacs,
            mets=mets,
            num_dead=num_dead, inPercentD=inPercentD,
            orph=orph, inPercentO=inPercentO,
            cycles=cycles,
            all=len(transp["_tx"]),
            stx=len(transp["s_tx"]),
            bmtx=len(transp["bm_tx"]),
            aa_bmtx=len(transp["aa_bm_tx"]),
            nt_bmtx=len(transp["nt_bm_tx"]),
            w_bmtx=len(transp["w_bm_tx"]),
            l_bmtx=len(transp["l_bm_tx"]),
            vit_bmtx=len(transp["vit_bm_tx"]),
            co_bmtx=len(transp["co_bm_tx"]),
            ftx=len(transp["f_tx"]),
            emtx=len(transp["em_tx"]),
            ntx=len(transp["n_tx"]),
            sftx=len(transp["sf_tx"]),
            sup=len(transp["sup_tx"]),
            hptx=len(transp["hp_tx"]),
            one=len(enzsubsets[1]),
            two=len(enzsubsets[2]),
            three=len(enzsubsets[3]),
            four=len(enzsubsets[4]),
            five=len(enzsubsets[5]),
            more=len(enzsubsets["more"]),
            top_ten=top_ten
        )
        print(statement)

        if output:
            with open(output, 'w') as out: out.write(statement)


class DataBases:

    #TODO: add to api reference

    def __init__(self): raise TypeError("DataBases object cannot be initialised.")
        

    @staticmethod
    def open_many(*args, common=None, dirs=None, data='data', **kwargs) -> list:

        """
        Given the file path for a database, open that database through ScrumPy.
        Ensure to unpack the returned list (same order as input) before moving on to
        other methods.
        """

        if common:
            args = [path.join(common, directory) + "/" for directory in dirs]
        
        log.info("Opening databases, this may take a while...")
        with HidePrints():
            databases = [PyoCyc.Organism(data=data, Path=pathdir, **kwargs) for pathdir in args]

        return databases

        
    @staticmethod
    def compare(*args, names=None, GeneAsso=True, commons=True, uniques=True, summary=True, **kwargs):

        master = {}

        database_reactions = [GeneAssoc.gene_associated_reactions(database) if GeneAsso 
                                else database.dbs["REACTION"].keys() 
                                for database in args]
        
        common = SetUtils.intersects(database_reactions)

        if commons:
            master.update({"common" : common})

        for index, lst in enumerate(database_reactions):
            reacs = database_reactions.copy()
            reacs.remove(lst)
            unique = SetUtils.complement(lst, SetUtils.merge(reacs)[0])

            try:
                key = names[index]
            except IndexError:
                key = index
            finally:

                if summary:
                    print(f"Database {key} has {len(unique)} unique reactions.")

                if uniques:
                    master.update({key : unique})

        return master


    @staticmethod
    def find_extras(database_a, database_b):
        '''Pre: True
        Post: get information on extra reactions, gene etc from database_b'''

        Extras = namedtuple("Extras", ["reactions", "compounds", "pathways", "enzymes", "proteins", "genes"])

        extra_reac = SetUtils.complement(database_b.dbs['REACTION'].keys(), database_a.dbs['REACTION'].keys())
        extra_enzrn = []
        for r in extra_reac:
            if 'ENZYMATIC-REACTION' in database_b[r]:
                for enzr in database_b[r]['ENZYMATIC-REACTION']:
                    extra_enzrn.append(enzr)

        extra_comp = SetUtils.complement(database_b.dbs['Compound'].keys(), database_a.dbs['Compound'].keys())
        extra_enz = []
        for enzr in extra_enzrn:
            if 'ENZYME' in database_b[enzr]:
                for enz in database_b[enzr]['ENZYME']:
                    extra_enz.append(enz)

        extra_path = SetUtils.complement(database_b.dbs["Pathway"].keys(), database_a.dbs["Pathway"].keys())
        extra_gene = []
        for enz in extra_enz:
            if 'GENE' in database_b[enz]:
                for g in database_b[enz]['GENE']:
                    extra_gene.append(g)

        return Extras(
                    extra_reac,
                    extra_comp,
                    extra_path,
                    SetUtils.complement(extra_enzrn, database_a.dbs["ENZYMATIC-REACTION"].keys()),
                    SetUtils.complement(extra_enz,   database_a.dbs["PROTEIN"].keys()),
                    SetUtils.complement(extra_gene,  database_a.dbs["GENE"].keys())
                    )


    @staticmethod
    def dump(db, filename, data):
        #FIXME
        '''Pre:
        Post: Wites data from db to a file'''

        with open(filename, 'w') as f:
            f.write("\n//\n".join([str(db[info]) for info in data]))
            f.write("//\n")


    @staticmethod
    def complement(database_a, database_b, fp=None):
        """
        Write Extra[Item].dat files for complementary items in a second database.
        
        """

        DIR = path.join(
            path.dirname(path.realpath(__file__)),
            "extras")
        extras = DataBases.find_extras(database_a, database_b)
        DataBases.dump(database_b, f"{DIR}/ExtraReaction.dat",   extras.reactions)
        DataBases.dump(database_b, f"{DIR}/ExtraCompound.dat",   extras.compounds)
        DataBases.dump(database_b, f"{DIR}/ExtraPath.dat",       extras.pathways)
        DataBases.dump(database_b, f"{DIR}/ExtraEnzrn.dat",      extras.enzymes)
        DataBases.dump(database_b, f"{DIR}/ExtraProtein.dat",    extras.proteins)
        DataBases.dump(database_b, f"{DIR}/ExtraGene.dat",       extras.genes)


    @staticmethod
    def update(db, path=".", ExtraCompounds='ExtraCompounds.dat'):
        
        '''
        Update database with extra compounds

            Parameters:
                db (obj) : database
                path (str) : file path to extra compounds .dat file
                ExtraCompounds (str) : name of file

            Returns:
                db (obj) : updated database
        '''
        updatedDB = PyoCyc.Compound.DB(path, ExtraCompounds)
        for met in updatedDB.keys():
            db.dbs['Compound'][met] = updatedDB[met]
        return db


    @staticmethod
    def ReacToGene(db, reactions=None):
        rv = {}
        if not reactions:
            reactions = db.dbs['REACTION'].keys()
        for r in reactions:
            gen = []
            genes = db[r].GetGenes()
            for g in genes:
                if 'COMMON-NAME' in db[g.UID].keys():
                    gen.append(db[g.UID]['COMMON-NAME'][0])
                else:
                    gen.append(g.UID)
            rv[r] = gen
        return rv


class GeneAssoc:


    @staticmethod
    def no_gene_association(db) -> list: 
        return [reaction for reaction in db.dbs["REACTION"].keys() if not db.dbs["REACTION"][reaction].GetGenes()]
    # list of reactions with no genes

    @staticmethod
    def gene_association(db) -> list: 
        return [reaction for reaction in db.dbs["REACTION"].keys() if db.dbs["REACTION"][reaction].GetGenes()]

    @staticmethod
    def gene_associated_reactions(db) -> set: 
        #TODO: check utility
        return SetUtils.complement(db.dbs["REACTION"].keys(), GeneAssoc.no_gene_association(db))
    
    @staticmethod
    def reactions_without_coverage(model, database):
        result = SetUtils.intersect(model.sm.cnames, database.dbs["REACTION"].keys())
        return len(model.sm.cnames) - len(result)


    @staticmethod
    def model_gene_association(model, database, inverse=False):
        result = SetUtils.intersect(model.sm.cnames, database.dbs["REACTION"].keys())
        
        if not inverse:
            return [r for r in result if database.dbs["REACTION"][r].GetGenes()]
        else:
            return [r for r in result if not database.dbs["REACTION"][r].GetGenes()]
        
    
    @staticmethod
    def calculate_gene_association(model, database):
        result = SetUtils.intersect(model.sm.cnames, database.dbs["REACTION"].keys())

        GeneAssoc = [r for r in result if database.dbs["REACTION"][r].GetGenes()]
        
        NoGeneAssoc = [r for r in result if not database.dbs["REACTION"][r].GetGenes()]

        return round((1- len(NoGeneAssoc) / len(GeneAssoc)) * 100, 1)

    
    @staticmethod
    def find_split_reactions(lst: list):
        p = re.compile(r'RXN-\(\w+\)$')
        return [i for i in lst if p.search(i)]


class ATP:

    @staticmethod
    def check_ATP_modes(model, elmodes, ATPase="ATPSynth", summary=True):
        """
        Identify elementary modes producing ATP from nothing.

            Parameters:
                model (obj) : model
                elmodes (obj) : elementary modes
                ATPase (str) : ATPase reaction
                summary (bool) : print summary

            Returns:
                rv (list) : list of elementary modes producing ATP from nothing
        """

        transporters = list(filter(lambda x : x.endswith("_tx"), model.sm.cnames))
        modes = list(elmodes.ModesOf(ATPase).keys())
        rv = [mode for mode in modes if not SetUtils.intersect(transporters, list(elmodes.ReacsOf(mode).keys()))]

        if summary:
            log.info(f"ATP producing modes: {', '.join(rv)}")
        return rv


    @staticmethod
    def Scan(model, low=0, high=100, n=100, lp=None, O2=5.0, ATPase="ATPSynth"):
        # FIXME: final sol value goes nowhere
        Sols = []
        incr = (float(high)-low) / (n-1)             # scan na points between alo and ahi with incr step
        for flux in map(lambda x: low+x*incr, range(n)):
            lp_a = LP.build(model, reaction=ATPase, flux=flux)
            Sols.append(lp_a)

        if O2:
            lp.SetFluxBounds({'O2_tx': (0.0, O2)})

        SetATP = lambda ATP: lp.SetFluxBounds({ATPase : (ATP, None)})
        ranges = np.arange(low, high, (high-low)/(n-1))
        for ATPLim in ranges:
            SetATP(ATPLim)
            lp.Solve()
            if lp.IsStatusOptimal():
                sol = lp.GetPrimSol()
                sol['ObjVal'] = lp.GetObjVal()
                sol["ATPLim"] = ATPLim

        return Sols
    
