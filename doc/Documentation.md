# Documentation

## Table of Contents
- Tutorial
- Definitions and syntax
- Tuatara .spy format


## Definitions and syntax
Tuatara has definitions which reflect the behaviours of the reptile this package is named after. 
- Each sample, or isolate, added to tuatara is called an `egg`.
- These eggs are stored in a `nest`. 
- When inputting your egg(s) into the `BuildNest` method, you are adding the egg(s) to the `nest`.
- To load an egg into the LP, you `hatch` an egg.

---

## tuatara .spy format
For each egg identified in the Roary gene presence/absence file, a ScrumPy (.spy) is generated. These follows the same syntax as regular spy files. 

Tuatara .spy files are created with the following structure:
- A header containing basic information about the file
- Body of ScrumPy reactions in four sections:
   - Reactions with conflicts (each conflict is numbered per reaction ID).
   - Reactions which were expected to be in model files but were not found.
   - Reactions to have zero flux in LP.
   - Reactions to be added to LP.