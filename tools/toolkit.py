import logging
from collections import namedtuple
from os import path

import numpy as np
import networkx as nx
from operator import itemgetter
import matplotlib.pyplot as plt
from ScrumPy.Bioinf import PyoCyc
from ..core.GUI import Editor
from .utils import SetUtils, HidePrints

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# TODO: fix core functions
# TODO: make a standalone gist file out of this module


class LP:

    @staticmethod
    def build(model, 
                fluxdict=None, 
                reaction=None, 
                flux=1, 
                block_uptake=False, 
                suffix="_tx",  
                obj=None,
                solve=True):
        """
        Build linear programme from model.
        
            Parameters:
                model (obj) : model
                fluxdict (dict) : flux dictionary
                reaction (str) : name of reaction
                flux (int) : flux value for reaction
                block_uptake (bool) : block transporters
                suffix (str) : block transporters with given suffix ('_tx' for all transporters; '_mm_tx' for media transporters)
                obj (str) : linear programme objective
                solve (bool) : solve LP

            Returns:
                lp (obj) : linear programme of model
        """
        
        lp = model.GetLP()
        if block_uptake:
            lp = lp.SetFixedFlux({tx : 0 for tx in filter(lambda x: x.endswith(suffix), model.sm.cnames)})
        
        if reaction:
            lp.SetFixedFlux({reaction : flux})
        if fluxdict:
            lp.SetFixedFlux(fluxdict)

        if obj == "min":
            lp.SetObjective(model.sm.cnames)   # minimise total flux

        if solve:
            lp.Solve()
            lp = lp.GetPrimSol()

        return lp


    @staticmethod
    def prints(model, lp):
        for key, value in lp.items():
            print(value, model.smx.ReacToStr(key))


    @staticmethod
    def scan(lp, suffix="_tx", **kwargs): return list(filter(lambda x : x.endswith(suffix), lp.keys()))
        # FIXME: should work but not tidy.


    @staticmethod
    def show(model, lp):
        DIR = path.dirname(path.realpath(__file__))
        PATH = path.join(DIR, "LP.tua")

        with open(PATH, 'w') as LPfile:
            for key, value in lp.items():
                LPfile.write(f"{value} {model.smx.ReacToStr(key)}\n")

        Editor(filename=PATH)

    @staticmethod
    def plot(model, lp):

        G = nx.Graph()
        G.add_nodes_from([reac for reac in lp.keys()])

        reactions = {reac : {
                                "reactants" : model.smx.Reactants(reac),
                                "products" : model.smx.Products(reac)
                                } for reac in lp.keys()
                                }

        for reaction, values in reactions.items():

            products = values["products"]

            for r, v in reactions.items():

                reactants = v["reactants"]

                if SetUtils.does_intersect(products, reactants):

                    G.add_edge(reaction, r)
        
        hub = sorted(G.degree(), key=itemgetter(1))[-1][0]

        ego_plot = nx.ego_graph(G, hub)

        
        nx.draw(ego_plot, with_labels=True, pos=nx.spring_layout(G), edge_color='c')
        plt.show()



class Model:
    #TODO: move to nest scripts

    def __init__(self): raise TypeError("Object cannot be initialised.")
        
        
    @staticmethod
    def merge_models(model_a, model_b):
        model_a.md.Reactions.update(model_b.md.Reactions)
        model_a.md.Metabolites.update(model_b.md.Metabolites)
        for x in model_b.md.xMetabolites:
            if not x in model_a.md.xMetabolites:
                model_a.md.xMetabolites.append(x)
        model_a.md.QuoteMap.update(model_b.md.QuoteMap)
        model_a.__init__(model_a.md)


    @staticmethod
    def check_imbals(m, db, reacs=None):
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
    def check_biomass_production(model, reactions=None, flux=-1, **kwargs):
        """
        Check model's biomass production.

            Parameters:
                model (obj) : model
                reactions (list) : dictionary of reaction flux
                flux (int) : reaction flux
                **kwargs : keyword arguments for build
            Returns:
                rv (dict) : dictionary of biomass solutions

        pre: True
        post: the lp solution for production of each biomass components
        """
        rv = {}

        bm = reactions if reactions else filter(lambda x : x.endswith('_bm_tx'), model.sm.cnames) 
        
        for reac in bm:
            sol = LP.build(model, reaction=reac, flux=flux, **kwargs)
            if sol:
                rv[reac] = sol
            else:
                log.info(reac)
        return rv
	

    @staticmethod
    def transporters(m):
        # TODO: ensure captures transporters properly
        """ 
        Get a dictionary of all transporters present in model broken down.

            Parameters:
                m (obj) : model
        
            Returns:
                (rv, tx_tags) (tuple) :
                            rv (dict) : reactions
                            tx_tags (dict) :  reaction tag definitions
        """

        tx_tags = {
            'stx'       : "optional-substrates",
            'bmtx'      : "biomass",
            'aa_bmtx'   : "amino acids",
            'nt_bmtx'   : "nucleotides",
            'w_bmtx'    : "cell wall",
            'l_bmtx'    : "cell lipids",
            'vit_bmtx'  : "biomass specific vitamins",
            'co_bmtx'   : "biomass specific cofactors",
            'ftx'       : "fermentation",
            'emtx'      : "essential micronutrient",
            'ntx'       : "nitrogen source",
            'sftx'      : "substrate/fermentation (transports met which is both f-product and substrate)",
            'sup'       : "supplementary nutrients e.g. vitamins",
            'hptx'      : "heterologous product",
            'all'       : "all"
        }

        rv = {}

        rv['stx'] = list(filter(lambda s: "s_tx" in s, m.sm.cnames))            # optional-substrates (carbon/energy sources)
        rv['bmtx'] = list(filter(lambda s: "bm_tx" in s, m.sm.cnames))          # biomass
        rv['aa_bmtx'] = list(filter(lambda s: "aa_bm_tx" in s, m.sm.cnames))    # amino acids
        rv['nt_bmtx'] = list(filter(lambda s: "nt_bm_tx" in s, m.sm.cnames))    # nucleotides
        rv['w_bmtx'] = list(filter(lambda s: "w_bm_tx" in s, m.sm.cnames))      # cell wall
        rv['l_bmtx'] = list(filter(lambda s: "l_bm_tx" in s, m.sm.cnames))      # cell lipids
        rv['vit_bmtx'] = list(filter(lambda s: "vit_bm_tx" in s, m.sm.cnames))  # biomass specific vitamins
        rv['co_bmtx'] = list(filter(lambda s: "co_bm_tx" in s, m.sm.cnames))    # biomass specific cofactors
        rv['ftx'] = list(filter(lambda s: "f_tx" in s, m.sm.cnames))            # fermentation
        rv['emtx'] = list(filter(lambda s: "em_tx" in s, m.sm.cnames))          # essential micronutrient
        rv['ntx'] = list(filter(lambda s: "n_tx" in s, m.sm.cnames))            # nitrogen source
        rv['sftx'] = list(filter(lambda s: "sf_tx" in s, m.sm.cnames))          # substrate/fermentation (transports met which is both f-product and substrate)
        rv['sup'] = list(filter(lambda s: "sup_tx" in s, m.sm.cnames))          # supplementary nutrients e.g. vitamins
        rv['hptx'] = list(filter(lambda s: "hp_tx" in s, m.sm.cnames))          # a heterologous product
        rv['all'] = list(filter(lambda s: "_tx" in s, m.sm.cnames))             # all transporters

        return rv, tx_tags


    @staticmethod
    def transportersLong(m):

        transp, _ = Model.transporters(m)
        print ("*transporters total:  ", len(transp['tx']))
        print ("\t-> substrates:  ", len(transp['stx'])+len(transp['sftx']))
        print ("\t-> essential micronutrients:  ", len(transp['emtx']))
        print ("\t-> nitrogen source:  ", len(transp['ntx']))
        print ("\t-> supplementary substrates (e.g. vitamins):  ", len(transp['sup']))
        print ("\t-> biomass precursors:  ", len(transp['bmtx']))
        print ("\t-> fermentation products:  ", len(transp['ftx']))
        print ("\t-> heterlogous products:  ", len(transp['hptx']))
        print ("\tNote - both substrates and products", transp['sftx'])


    #get metabolites from list of reactions
    @staticmethod
    def get_mets(m, reacs):
        """pre: model, [reacs]
        post: [all mets in sol]"""

        rv = []
        
        for i in reacs:
            for met in m.sm.InvolvedWith(i):
                if met not in rv:
                    rv.append(met)
        return rv


    @staticmethod
    def connects(m):
        connected ={}
        for met in m.sm.rnames:
            connected[met] = m.sm.Connectedness(met)
        rv = sorted(connected.items(), key=lambda c:c[1], reverse=True)
        return rv


    @staticmethod
    def ESubsets(m, returnMore=False):

        one = [] ; two = [] ; three = [] ; four = [] ; five = [] ; more = []
        
        subsets = m.EnzSubsets()
        
        for sub in subsets.keys():
            if len(subsets[sub]) == 1:
                one.append(sub)
            elif len(subsets[sub]) == 2:
                two.append(sub)
            elif len(subsets[sub]) == 3:
                three.append(sub)
            elif len(subsets[sub]) == 4:
                four.append(sub)
            elif len(subsets[sub]) == 5:
                five.append(sub)
            elif len(subsets[sub]) > 5:
                more.append(sub)

        if not returnMore:
            return len(one),len(two),len(three),len(four),len(five),len(more)
        else:
            subsetDic = {}
            subsetDic['one'] = one
            subsetDic['two'] = two
            subsetDic['three'] = three
            subsetDic['four'] = four
            subsetDic['five'] = five
            subsetDic['moreThanFive'] = more
            subsetDic['all'] = subsets
            
            return subsetDic


    @staticmethod
    def ShortSummary(m):

        print ("reactions: ", len(filter(lambda x: "_tx" not in x, m.sm.cnames)))
        print ("metabolites: ", len(m.sm.rnames))
        print ("transporters:", len(filter(lambda x: "_tx" in x, m.sm.cnames)))


    @staticmethod
    def LongSummary(m):

        print ("*reactions:", len(filter(lambda x: "_tx" not in x, m.sm.cnames)))
        print ("*metabolites: ", len(m.sm.rnames) )
        Model.transportersLong(m)

        dead = m.DeadReactions()
        inPercentD = round(100.0/len(m.sm.cnames)*(len(m.sm.cnames)-len(dead)),1)
        
        orph = m.OrphanMets()
        inPercentO = round(100.0/len(m.smx.rnames)*(len(m.smx.rnames)-len(orph)),1)
        
        sSet = Model.ESubsets(m)
        connecMets = Model.connects(m)
        cycles = m.MaxCycles() #internal cycles?
        #ping = m.PingConc() #doesn't work, but what is perturbing concentrations?...

        print ("\n*dead reactions: ", len(dead), "("+ str(inPercentD)+r"% live)")
        print ("*orphan mets: ", len(orph), "("+ str(inPercentO)+"% not orphans)")
        print ("*internal cycles: ", len(cycles))
        print ("\n*enzyme subsets (grouped by #reacs in set):  " \
        "one: ",sSet[0],", two: ",sSet[1],", three: ",sSet[2],", four: ", \
        sSet[3],", five: ",sSet[4],", more: ",sSet[5])
        print ("\n*top 15 connected mets: ", connecMets[:15])


class DataBases:

    def __init__(self):
        raise TypeError("DataBases object cannot be initialised.")


    @staticmethod
    def open_many(*args, common=None, dirs=None, data='data', **kwargs) -> tuple:

        """
        Given the file path for a database, open that database through ScrumPy.
        Ensure to unpack the returned list (same order as input) before moving on to
        other methods.
        """

        if common:
            args = [f"{common}/{directory}" for directory in dirs]
        
        log.info("Opening databases, this may take a while...")
        with HidePrints():
            databases = [PyoCyc.Organism(data=data, Path=pathdir, **kwargs) for pathdir in args]

        return databases

        
    @staticmethod
    def compare(*args, names=None, GeneAsso=True, commons=True, uniques=True, summary=False, **kwargs):

        master = {}

        database_reactions = [DataBases.gene_associated_reactions(database) if GeneAsso 
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
            except:
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
    def NoGene(db): return [reaction for reaction in db.dbs["REACTION"].keys() if not db[reaction].GetGenes()]
    # list of reactions with no genes

    @staticmethod
    def gene_associated_reactions(db): return SetUtils.complement(db.dbs["REACTION"].keys(), DataBases.NoGene(db))
        # '''pre:True
        # post: return list of reaction with gene association'''
        

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
    


