
[logo]: ./doc/img/Asset_1.png "Tuatara"
[prokka]: ./doc/img/Asset_2.png
[translation]: ./doc/img/Asset_3.png
[roary]: ./doc/img/Asset_4.png
[gs]: ./doc/img/Asset_5.png "Genome sequence"
[database]: ./doc/img/Asset_6.png "Organism database"
[gsm]: ./doc/img/Asset_7.png "GSM"
[bacteria]: ./doc/img/Asset_9.png

![alt text][logo]
# Tuatara

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/CaileanCarter/tuatara?include_prereleases)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/CaileanCarter/tuatara.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/CaileanCarter/tuatara/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/CaileanCarter/tuatara.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/CaileanCarter/tuatara/context:python)

<br>

Make and analyse many metabolic models simultaneously in [ScrumPy](https://mudshark.brookes.ac.uk/ScrumPy).

![gs] ![database] ![gsm]

## What is it?

Tuatara allows for complete genome assemblies of different strains of your model's species to be adapted into metabolic models. From the publically available tools [prokka](https://github.com/tseemann/prokka) and [Roary](https://github.com/sanger-pathogens/Roary), translate gene presence/absence results into reaction presence/absence with tuatara. Instead of creating and curating more than one metabolic model of closely related strains, tuatara stores and handles all the accessory reactions. Meaning only a single metabolic model for a species is required. Thus, the user only needs to curate the accessory reactions. 

![bacteria]
> ^ (top) GSM, (middle) database organisms, (bottom) bacteria samples. All from the same species of bacteria

To help with the curation of metabolic models, tuatara comes with tools for rapidly identifying unwanted elements in a model. It also includes assisting tools for visualising linear programmes and analysis of models. 

<br>

![prokka] &nbsp;
![roary] &nbsp;
![translation]

<br>

### Main features:
- Creating pseudo metabolic models of strains
- Containers for storing and dealing with many metabolic models
- Rapid searching for unwanted items in metabolic models
- Visualisation of linear programmes
- Multiple organism database handling and comparing

<br>


### Documentation ![database]
- [Documentation](https://github.com/CaileanCarter/tuatara/blob/master/doc/Documentation.md)
- [API reference](https://github.com/CaileanCarter/tuatara/blob/master/doc/API%20reference.md)
- [Get started](https://github.com/CaileanCarter/tuatara/blob/master/doc/Get%20started.md)

<br>

### Dependencies:
- [ScrumPy](https://mudshark.brookes.ac.uk/ScrumPy) (3.0-alpha)
- Python (3.6.9 and higher)
- pandas (1.1.5)
- numpy (1.19.5)
- [flashtext](https://github.com/vi3k6i5/flashtext) (2.7)
- matplotlib (3.3.4)
- networkx (2.5)

### Optional:
- PyYAML (5.4.1)
- Seaborn 


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


