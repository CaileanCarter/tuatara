# Documentation

## Table of Contents
- Tutorial
- Definitions and syntax
- Tuatara .spy format


## How does it work?
Instead of having to make and curate a whole metabolic model for each strain of a species, tuatara only takes the accessory reactions of the strains and stores them. Genome assemblies of each strain will need to be annotated with prokka so it can be inputted into Roary. Because isolates will have reactions and genes not present in the model strain, other reference strains will need to be included to cover this deficit. These reference strains are termed 'database organisms' as they require a BioCyc organism database for reactions to be accessed from. Reference assemblies for these database organisms will also need to be annotated with prokka as they will need to be included in the Roary analysis. Be sure to save the TSV output from prokka for database organisms as it will tell tuatara the common gene name for each 'locus tag' in roary output. This is because Roary's output does not respect the different common gene names across database organisms. <br><br>

Firstly, tuatara merges the duplicated gene names from Roary's output and merges the results. It then selects only the accessory genes and starts building a 'hashtable', which is a table of the accessory gene names and their actual gene name for each database organism. This is because gene names are not always shared between organisms. It then builds a master list of all the reactions from database organisms whose genes are present in the hashtable. All conflicts between databases (where the reactions are not identical) are stored seperately. Once the hashtable and master reaction list is made, tuatara begins iterating over the gene presence/absence results for each sample and creates a new ScrumPy file named after the sample. For reactions which are absent in the sample but present in the model (as determined by Roary), tuatara will check to see if the reaction is present in the model ScrumPy files (so it is not attempting to delete a reaction that doesn't exist). Reactions which are absent and those not present in the model files are stored in seperate sections in a ScrumPy file with the prefix "rm_". For reactions which are present in the sample but absent in the model, tuatara will add these to the ScrumPy file. Tuatara will also add reactions which have conflicting equations in a seperate section for the user to sort. During the making of these eggs, tuatara will output information on gene coverage and the reactions for each sample.<br><br>

To load an egg, tuatara will make a copy of the original model and switch out the reactions present/absent in the egg. No changes are made to the original so the two models can be compared. This can be scaled up to include many models at once.




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