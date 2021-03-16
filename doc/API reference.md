# API reference

## Nest building

All inputs required to build a nest can be given in a YAML or JSON format. They accept the same input parameters as `tuatara.Inputs`. Examples are provided in the [doc](https://github.com/CaileanCarter/tuatara/tree/master/doc) folder.

`tuatara.`<b>`read_yaml`(fp)</b>
<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;fp</b> : <i>str</i> &emsp;File path<dd>
<dt>&emsp;Returns:</dt>
<dd><b>&emsp;Inputs</b> : <i>obj</i></dd>
</dl>

`tuatara.`<b>`read_json`(fp)</b>
<dl>
<dt>&emsp;Parameters:</dt>
<dd>&emsp;<b>fp</b> : <i>str</i> &emsp;File path<dd>
<dt>&emsp;Returns:</dt>
<dd><b>&emsp;Inputs</b> : <i>obj</i></dd>
</dl>
<br>

### tuatara.<b>Inputs</b>
---
`tuatara.`<b>`Inputs`(roary=None, model=None, databases=None, fp=None, annots=None, locustags=None)</b><br>
Inputs class takes all the arguments to make a `nest` and allows for changes to be made to attributes before committing to building a nest. Thus, arguments are not giving directly to `tuatara.BuildNest` but this class.
<dl>
<dt><b>Parameters:</b></dt>
<dd><b>roary</b> : <i>str</i> &emsp;File path for roary "Gene Presence Absence file in Rtab format".</dd>
<dd><b>locustags</b> : <i>str</i>&emsp;File path for roary "Clustered proteins file".</dd>
<dd><b>databases</b> : <i>dict</i><br>
Declare which isolates in Roary files have BioCyc databases available.
key (str) : database organism in roary file<br>
value (str) : directory name for location of database (excluding version number subdirectory).<br>
Example: {"UTI89" : "EcoliUTI89"}</dd>
<dd><b>fp</b> : <i>str</i> &emsp;Shared path for database directories.</dd>
<dd><b>model</b> : <i>str</i>&emsp;Name of organism used as model as stated in roary files</dd>
<dd><b>annots</b> : <i>str</i><br>
File path for directory containing Prokka annotation files of database organism genomes in tabular format.
The Galaxy output is normally titled: "Prokka on [input]: tsv"<br>
Ensure file name is the same name as given in the roary files.<br>
Format: organism_name.tabular</dd>

<dt><b>Returns:</b></dt>
<dd><b>Inputs</b> : <i>obj</i></dd>
</dl>

<br>

<b>Attributes</b><br>

`Inputs.`<b>`model`</b> : <i>str</i> <br>
&emsp;Name of organism used as model as stated in roary files

`Inputs.`<b>`databases`</b> : <i>list</i><br>
&emsp;List of database organism IDs

`Inputs.`<b>`db_fp`</b> : <i>dict</i><br>
&emsp;key : database organism ID<br>
&emsp;value : database file path

`Inputs.`<b>`samples`</b> : <i>list</i><br>
&emsp;List of isolates found in roary gene presence/absence file (excluding database organisms)

`Inputs.`<b>`gpafile`</b> : <i>str</i><br>
&emsp;File path for roary "Gene Presence Absence file in Rtab format".

`Inputs.`<b>`annotations`</b> : <i>str</i><br>
&emsp;File path for directory containing Prokka annotation files of database organism genomes in tabular format.

`Inputs.`<b>`drop_columns`</b> : <i>list</i><br>
&emsp;A list of organisms to be ignored from the Roary file.

`Inputs.`<b>`rename`</b> : <i>dict</i><br>
&emsp;Rename an isolate in the roary file.<br>
&emsp;key (str) : original name of isolate<br>
&emsp;value (str) : new name for isolate

<br>

<b>Methods</b><br>

`Inputs.`<b>`drop`(*isolates)</b><br>
&emsp;Remove an isolate from the list.<br>
&emsp;Takes isolate IDs as input<br>
`Inputs.`<b>`rename`(pair)</b><br>
&emsp;Rename an isolate.<br>
&emsp;Takes dictionary as input, (key) original name : (value) new name

<br>

### tuatara.<b>BuildNest</b>
---
`tuatara.`<b>`BuildNest`(inputs)</b><br>

A class for creating .spy files for each isolate. This turns isolates into `eggs` which become metabolic models.<br>
<dl>
<dt><b>Parameters:</b></dt>
<dd><b>inputs</b> : <i>obj</i> &emsp;A class object containing all necessary inputs.</dd>

<br>

<b>Attributes</b>

`BuildNest.`<b>`model`</b> : <i>str</i><br>
&emsp;Name of organism used as model as stated in roary files

`BuildNest.`<b>`databases`</b> : <i>list</i><br>
&emsp;List of database organism IDs

`BuildNest.`<b>`db`</b> : <i>dict</i><br>
&emsp;key : database organism ID<br>
&emsp;value : database file path

`BuildNest.`<b>`samples`</b> : <i>list</i><br>
&emsp;List of eggs found in roary gene presence/absence file (excluding database organisms)

`BuildNest.`<b>`names`</b> : <i>list</i><br>
&emsp;List of all eggs found in roary gene presence/absence file
<dl>

<br>

## Nests and Eggs
---

`tuatara.`<b>`pick`(egg)</b><br>
Show egg's ScrumPy file in editor window.
<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;egg</b> : <i>str</i> &emsp;Egg ID<dd>

</dl>

`tuatara.`<b>`hatch`(model, egg=None, fromspy=False)</b><br>
Initialise new egg from model.
<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model<br>
<dd><b>&emsp;egg</b> : <i>str</i> &emsp;egg ID<br>
<dd><b>&emsp;fromspy</b> : <i>bool|str</i> &emsp;open file explorer to select .spy file or open file path
<dt>&emsp;Returns:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model of egg
</dl>

`tuatara.`<b>`get_path`(egg)</b><br>
Get ScrumPy file filepath for an egg

`tuatara.`<b>`check_egg_exists`(egg)</b><br>
Check a given egg has a ScrumPy file.

`tuatara.`<b>`scan`(egg=None, from_file=False, file_path=None, stdout=False)</b><br>
Scan ScrumPy file for unwanted items declared in `tuatara.WatchList`. Launches a table showing line, matches and reaction.

<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;egg</b> : <i>str</i> &emsp;egg ID<br>
<dd><b>&emsp;from_file</b> : <i>bool</i> &emsp;input own file through a file explorer<br>
<dd><b>&emsp;file_path</b> : <i>str</i> &emsp;provide file path for .spy file<br>
<dd><b>&emsp;stdout</b> : <i>bool</i> &emsp;print results<br>
</dl>

<br>

### tuatara.<b>WatchList</b>

---

<i>class</i> `tuatara.`<b>`WatchList`()</b><br>
WatchList is a tua file containing metabolites and items deemed unwanted in a metabolic model. While tuatara comes with a default WatchList, it is completely customisable by the user. WatchList does not need to be openned or initialised as this functionality is done by the class methods.<br>
> See also: `tuatara.`<b>`scan`</b>

<br>

<b>Methods</b>

`WatchList.`<b>`str_watchlist`(watchlist)</b><br>
Return a string representation of the watchlist.
<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;watchlist</b> : <i>list</i> &emsp;watchlist<br>
<dt>&emsp;Returns:</dt>
<dd><b>&emsp;watchlist</b> : <i>str</i> &emsp;string representation of watchlist
</dl>

`WatchList.`<b>`open_watchlist`()</b><br>
Returns the watchlist as a list.<br>

`WatchList.`<b>`close_watchlist`(watchlist)</b><br>
Saves watchlist to file.
<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;watchlist</b> : <i>list</i> &emsp;watchlist<br>
</dl>

<br>

<b>Class methods</b><br>

`tuatara.WatchList.`<b>`tidy`()</b><br>
Removes duplicates from the watchlist and orders the items alphabetically.<br>

`tuatara.WatchList.`<b>`edit`()</b><br>
Opens editor window to edit the watchlist. Changes can be saved and in the editor window and committed to watchlist using `tuatara.WatchList.commit()`<br>

`tuatara.WatchList.`<b>`commit`()</b><br>
Commit changes made in editor window to watchlist<br>

`tuatara.WatchList.`<b>`dump`(items)</b><br>
Add list of items to watchlist<br>

`tuatara.WatchList.`<b>`dumps`(item)</b><br>
Add string item to watchlist<br>

`tuatara.WatchList.`<b>`drop`(items)</b><br>
Remove list of items from watchlist<br>

`tuatara.WatchList.`<b>`drops`(item)</b><br>
Remove string item from watchlist<br>

`tuatara.WatchList.`<b>`wipe`()</b><br>
Clear the watchlist<br>

`tuatara.WatchList.`<b>`from_file`(fp, replace=False)</b><br>
Add items to watchlist from a text file or replace existing watchlist.

<br>

### tuatara.<b>Nest</b>
---

### tuatara.<b>Community</b>

---

<br>

## Tuakit

---

Tuatara offers a number of tools for handling metabolic models. 

### tuatara.<b>LP</b>

---
`tuatara.LP.`<b>`build`(model, reaction=None, fluxdict=None, flux=1, block_uptake=False, suffix="_tx", obj="min", solve=True)</b> <br>

Build a linear programme in ScrumPy.

<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model</dd>
<dd><b>&emsp;reaction</b> : <i>str</i> &emsp;name of reaction</dd>
<dd><b>&emsp;fluxdict</b> : <i>dict</i> &emsp;flux dictionary</dd>
<dd><b>&emsp;flux</b> : <i>int</i> &emsp;flux value for reaction</dd>
<dd><b>&emsp;block_uptake</b> : <i>bool</i> &emsp;block transporters</dd>
<dd><b>&emsp;suffix</b> : <i>str</i> &emsp;block transporters with given suffix</dd>
<dd><b>&emsp;obj</b> : <i>str</i> &emsp;objective (only "min" supported)</dd>
<dd><b>&emsp;solve</b> : <i>bool</i> &emsp;solve LP</dd>
<dt>&emsp;Returns:</dt>
<dd><b>&emsp;lp</b> : <i>obj</i> &emsp;linear programme of model
</dl>

Examples:
```
>>> import tuatara as tua
>>> m = ScrumPy.Model("MyModel.spy")
>>> lp1 = tua.LP.build(m, "ATPSynth")
optimal
>>> fluxdict = {"ATPSynth" : 1, "X_RXN" : 3}
>>> lp2 = tua.LP.build(m, fluxdict=fluxdict, block_uptake=True)
not feasible
```

`tuatara.LP.`<b>`prints`(model, lp)</b> <br>
Print the LP with flux values.

`tuatara.LP.`<b>`find`(lp, text)</b> <br>
Find reactions in your LP.
<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;lp</b> : <i>obj</i> &emsp;LP</dd>
<dd><b>&emsp;text</b> : <i>str</i> &emsp;search term</dd>
<dt>&emsp;Returns:</dt>
<dd><b>&emsp;result</b> : <i>list</i> &emsp;list of results</dd>
</dl>

`tuatara.LP.`<b>`show`(model, lp)</b> <br>
View LP in an Editor Window. Ideal for LPs with large contents without slowing down shell.

`tuatara.LP.`<b>`tabulate`(model, LP, output=None, exclude=None, include=None)</b> <br>
Visualise LP in a table window.

<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model</dd>
<dd><b>&emsp;lp</b> : <i>obj</i> &emsp;LP</dd>
<dd><b>&emsp;output</b> : <i>str</i> &emsp;(optional) output to a text file as tab seperated</dd>
<dd><b>&emsp;exclude</b> : <i>list</i> &emsp;exclude given metabolites</dd>
<dd><b>&emsp;include</b> : <i>list</i> &emsp; include only given metabolites
</dl>

There is a default list of common metabolites to exclude which can be excluded by using the argument "default" for exclude. This is the same as doing:
```
>>> exclude = ["NADP", "NAD", "NADPH", "Pi", "PROTON", "WATER", "ADP", "ATP", "NADH", "PPI"]
>>> tuatara.LP.tabulate(n, lp, exclude=exclude)
```

`tuatara.LP.`<b>`plot`(model, lp, exclude=None, include=None)</b><br>
Plot LP as a network graph.

<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model</dd>
<dd><b>&emsp;lp</b> : <i>obj</i> &emsp;LP</dd>
<dd><b>&emsp;exclude</b> : <i>list</i> &emsp;exclude given metabolites</dd>
<dd><b>&emsp;include</b> : <i>list</i> &emsp; include only given metabolites</dd>
</dl>

There is also a default list of common metabolites as mentioned in `tuatara.LP.tabulate`.<br>


### tuatara.<b>Model</b>

---

`tuatara.Model.`<b>`find`(model, key, types)</b><br>
Easily find a metabolic or reaction by a keyword.

<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model</dd>
<dd><b>&emsp;keyword</b> : <i>str</i> &emsp;keyword to search</dd>
<dd><b>&emsp;types</b> : <i>str|tuple</i> &emsp;'met' or 'reac' for metabolite or reaction, respectively</dd>
</dl>

`tuatara.Model.`<b>`transporters`(model, stdout=None, include=None, only=None)</b><br>
Get a dictionary of all transporters present in a model by suffix.

<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model</dd>
<dd><b>&emsp;stdout</b> : <i>bool</i> &emsp;print transporters</dd>
<dd><b>&emsp;include</b> : <i>list</i> &emsp;include suffixes to find in reactions</dd>
<dd><b>&emsp;only</b> : <i>list</i> &emsp;only show specified suffixes
<dt>&emsp;Returns:</dt>
<dd><b>&emsp;reactions</b> : <i>dict</i> &emsp;reaction suffix (key) and reactions (values : list)</dd>
</dl>

`tuatara.Model.`<b>`reacs_to_mets`(model, reacs)</b><br>
Get the metabolites involved in a list of reactions.

<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model</dd>
<dd><b>&emsp;reacs</b> : <i>list</i> &emsp;list of reactions</dd>
<dt>&emsp;Returns:</dt>
<dd><b>&emsp;metabolites</b> : <i>set</i> &emsp;metabolites involved in reactions</dd>
</dl>

`tuatara.Model.`<b>`summary`(model, output=None)</b><br>
Print a summary of a model.

<dl>
<dt>&emsp;Parameters:</dt>
<dd><b>&emsp;model</b> : <i>obj</i> &emsp;model</dd>
<dd><b>&emsp;output</b> : <i>str</i> &emsp;file path to write to</dd>
</dl>


### tuatara.<b>DataBases</b>

---





<br>

## Logging (stdout)
---

`tuatara.`<b>`verbose`()</b><br>
Hides logging messages. Levels ERROR and above will still be shown.<br>

`tuatara.`<b>`debug`()</b><br>
Switch logging to debug

`tuatara.`<b>`HidePrints`()</b><br>
Context manager for hiding print statements.