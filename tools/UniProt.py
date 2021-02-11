from collections import namedtuple
from bioservices import UniProt

services = UniProt()

def search_gene(entry=None, organism=None):
    # FIXME

    uniprot = namedtuple("UniProt", ["gene", "ID", "entry", "protein", "reaction", "pathway"])

    gene, ID, entry_name, protein, reaction, pathway = services.search(
        f"{entry} AND {organism}", 
        limit=1, 
        columns="id,entry name, protein names, comment(CATALYTIC ACTIVITY), comment(PATHWAY)") \
        .split("\t")

    reaction = reaction.replace("CATALYTIC ACTIVITY: Reaction=", "").strip()
    pathway = pathway.replace("PATHWAY:", '').strip()
    return  uniprot(gene, ID, entry_name, protein, reaction, pathway)