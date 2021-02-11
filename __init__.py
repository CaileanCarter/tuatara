#!/usr/bin/python3

import logging

from .tools import (
                    WatchList, 
                    scan, 
                    buildLP, 
                    showLP,
                    printLP,
                    check_imbals, 
                    check_biomass_production, 
                    Model, 
                    DataBases, 
                    ReacToGene, 
                    ATP
                        )
from .core import (
                BuildNest,
                Inputs, 
                read_yaml, 
                read_json,
                pick
                    )
from .nest import (
                get_path, 
                check_egg_exists, 
                nest, 
                hatch
                    )


# TODO: Does a more stable and reliable egg storage system need to be included?
# TODO: Reports for eggs?
# TODO: impliment snakemake feature?
# TODO: CLI via __main__.py
# TODO: Add extra functionality to scanner gui
# TODO: write API reference
# TODO: sort out register (is it necessary?)


logging.basicConfig(level=logging.INFO, format="tuatara - %(levelname)s - %(message)s")


def verbose():
    """Hides logging messages. Levels ERROR and above will still be shown."""
    logging.getLogger().setLevel(logging.ERROR)

def debug():
    """Switch logging to debug"""
    logging.getLogger().setLevel(logging.DEBUG)


__version__ = "0.1-dev"

__doc__ = f"""
tuatara - a metabolic model modularisation package for ScrumPy
==============================================================

Version:            {__version__}
Last modified:      22/01/2021
Github:             
Author:             Cailean Carter
Affilitation:       Quadram Institute, Norwich Research Park
Email:              cailean.carter@quadram.ac.uk


For full documentation, see README.md.


To hide logging message, use 'tua.verbose()'
"""