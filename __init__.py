<<<<<<< HEAD
#!/usr/bin/python3

import logging

from .tools import (
                    WatchList, 
                    scan, 
                    LP,
                    Model, 
                    DataBases,  
                    ATP,
                    HidePrints
                        )
from .core import (
                BuildNest,
                Inputs, 
                read_yaml, 
                read_json,
                pick,
                Nest,
                Community
                    )
from .nest import (
                get_path, 
                check_egg_exists, 
                Eggs, 
                hatch
                    )


# TODO: Does a more robust egg storage system need to be included?
# TODO: Reports for eggs?
# TODO: Add extra functionality to scanner gui?
# TODO: write API reference
# TODO: sort out register (is it necessary?)
# TODO: create script to keep copy in main drive
# TODO: consider including jellyfish to find matching reactions
# TODO: implement system where models can interact

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
Last modified:      23/02/2021
Github:             
Author:             Cailean Carter
Affilitation:       Quadram Institute, Norwich Research Park
Email:              cailean.carter@quadram.ac.uk


For full documentation, see README.md.

=======
#!/usr/bin/python3

import logging

from .tools import (
                    WatchList, 
                    scan, 
                    LP,
                    Model, 
                    DataBases,  
                    ATP,
                    HidePrints
                        )
from .core import (
                BuildNest,
                Inputs, 
                read_yaml, 
                read_json,
                pick,
                Nest,
                Community
                    )
from .nest import (
                get_path, 
                check_egg_exists, 
                Eggs, 
                hatch
                    )


# TODO: Does a more robust egg storage system need to be included?
# TODO: Reports for eggs?
# TODO: Add extra functionality to scanner gui?
# TODO: write API reference
# TODO: sort out register (is it necessary?)
# TODO: create script to keep copy in main drive
# TODO: consider including jellyfish to find matching reactions
# TODO: implement system where models can interact

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
Last modified:      25/06/2021
Github:             
Author:             Cailean Carter
Affilitation:       Quadram Institute, Norwich Research Park
Email:              cailean.carter@quadram.ac.uk


For full documentation, see README.md.

>>>>>>> c31daa9d32fa85138c7efe1b3c02bac2e65a37ad
"""