# Get started

### What you need:
- A metabolic model compatible with ScrumPy
- Complete genome assemblies of the model organism, reference organisms/strains, and strains of interest
- BioCyc databases of reference organisms/strains and for the model strain
- Software Roary and Prokka



### Analysis




### Data needed:

1. "Gene Presence Absence file in Rtab format" from Roary
2. Locustags from Roary under description of "Clustered proteins file".
3. BioCyc databases for reference strains
4. Prokka annotations of all strains used in Roary analysis in TSV format


```
File structure
.
|-annotation
| |-- isolate_1.tabular
| |-- isolate_2.tabular
| |-- isolate_3.tabular
| |-- database_1.tabular
| |-- database_2.tabular
| |-- database_3.tabular
| |-- model.tabular
|
|-database
| +-- database_1 ...
| +-- database_2 ...
| +-- database_3 ...
| +-- model ...
|
|-- gene_presence_absence.txt
|-- locustags_gpa.txt


```


Execute in ScrumPy:
```
>>> import tuatara as tua

>>> inputs = tua.Inputs(
                        roary="./gene_presence_absence.txt",
                        model="model",
                        databases={
                                "sampleE" : "databaseA",
                                "sampleF" : "databaseB"
                        },
                        fp="filepath",
                        annots="filepath",
                        locustags="filepath"
                        )
>>> inputs.rename({
                "sampleX" : "sampleA",
                "sampleY" : "sampleB"
                })
>>> inputs.drop("sampleB")

>>> inputs.samples
"sampleA, sampleC, sampleD"
>>> inputs.databases
"sampleE, sampleF"
>>> nest = tua.BuildNest(inputs)
# Output

```