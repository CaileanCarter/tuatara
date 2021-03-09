[![LGTM](https://img.shields.io/lgtm/grade/python/github/CaileanCarter/tuna.svg?style=flat-square)](https://lgtm.com/projects/g/CaileanCarter/tuatara)

# tuatara

Make and analyse many metabolic models simultaneously in [ScrumPy](https://mudshark.brookes.ac.uk/ScrumPy).

## What is it?

Tuatara allows for complete genome assemblies of different strains of your model's species to be adapted into metabolic models. From the publically available tools [prokka](https://github.com/tseemann/prokka) and [Roary](https://github.com/sanger-pathogens/Roary), translate gene presence/absence results into reaction presence/absence with tuatara. Instead of creating and curating more than one metabolic model of closely related strains, tuatara stores and handles all the accessory reactions. Meaning only a single metabolic model for a species is required. Thus, the user only needs to curate the accessory reactions.

To help with the curation of metabolic models, tuatara comes with tools for rapidly identifying unwanted elements in a model. It also includes assisting tools for visualising linear programmes and analysis of models. 

<br>

### Main features:
- Creating pseudo metabolic models of strains
- Containers for storing and dealing with many metabolic models
- Rapid searching for unwanted items in metabolic models
- Visualisation of linear programmes
- Multiple organism database handling and comparing

<br>

### Documentation
- [Documentation](https://github.com/CaileanCarter/tuatara/blob/master/doc/Documentation.md)
- [API reference](https://github.com/CaileanCarter/tuatara/blob/master/doc/API%20reference.md)



<br>

### Dependencies:
- [flashtext](https://github.com/vi3k6i5/flashtext) (2.7)
- matplotlib (3.3.4)
- networkx (2.5)
- numpy (1.19.5)
- pandas (1.1.5)
- Python (3.8.2)
- [ScrumPy](https://mudshark.brookes.ac.uk/ScrumPy) (3.0-alpha)

<br>

---

## Preview

<b>Building your first nest.</b>

```
>>> import tuatara as tua

>>> inputs = tua.Inputs(
                        roary="filepath",
                        model="modelA",
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
---



