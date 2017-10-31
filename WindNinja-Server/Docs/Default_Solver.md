# Process to Change the Default Solver for WindNinja Mobile

## Summary

The mobile application does not currently provide a UI element for the user to choose a solver.  While an element (a simple on/off checkbox) could be provided on the job request panel, the spirit of the mobile application is to 'keep things simple'.  It is preferrable at this time to have the server determine the solver to be used.  Therefore, WindNinja Mobile can provide results via the momentum solver but it's an all or none choice.  The user can not control the result. 

Mobile application build 1.0.4 removes the mesh_choice parameter from the job request override settings, making the server side configuration the master setting for this value.  This is necessary because the optimal choice for the mobile application is different for each solver. 

With server version 1.1, no code changes are necessary to swap between solvers.  Simple changes to the configuration file on the server following the steps outlined below will handle the task. 

## Introduction

All settings that need configured are found in the file ../Src/windninjawrapper/windninjawrapper.config.yaml in the job_wrapper/wn_cli sub-section.

**NOTE: The config file is YAML formatted.  YAML is a simple to read but specific syntax. Modifying the file incorrectly will result in failure of the job processing sub-system.**

The relevant sections to modify are 

* job_wrapper/wn_cli/args_da (domain average initialization)
* job_wrapper/wn_cli/args_wx (weather model initialization)
* job_wrapper/wn_cli/defaults

**NOTE: WindNinja Mobile Server currently only uses weather model initialization so the domain average section is not necessary but it's worth keeping them in-sync if supplied.**

The 'args' sections provide all the specific parameters that will be included when constructing the CLI command.  These sections are a LIST of strings in the format:

"[cli parameter name] [hard-coded value]" 

 or 

"[cli parameter name] $[template variable name]"

These values can be configured as:
1. A "hard-code" value that _will NOT_ be overriden by the job parser or default settings 
2. A "template" value that _will_ be matched and replaced against the defaults and job parser.

* The [cli parameter name] value must exactly match the name as defined in the CLI specification including any dash formatting.	
* The [hard-coded value] must exactly match the appropriate value to be used as defined in the CLI specification.
* The $[template variable name] is the 'replacement' location for the values that are determined by the code.  This value MUST start with the template key character $.  It must match either the value defined in the 'defaults' or known to be used with the code or job request.
 
The 'defaults' section supplies the 'default' value to be used in the CLI command if another value is not supplied via the job request or parser code.  This section is a key/value pair dictionary.  The key strings should match the template string used in the args section without the template $ character.
 
## Steps

1. Add the templated cli parameter for momentum solving to the job_wrapper/wn_cli/args_da and job_wrapper/wn_cli/args_wx 

	If value is not present in these sections the following should be added as either hard-coded or default templated i.e.:
	
	"--momentum_flag true"
	
	or
	
	"--momentum_flag $momentum_flag"

	
2. If using the templated sytle, add a key/value pair to the defaults section i.e.

	momentum_flag: true
	
3. To change between the two solvers, change either the hard-coded args value or default key value between true/false as defined by the CLI specification. 

4. Change the defualt value for mesh_choice to the value appropriate for the solver.

**NOTE: this value could also be 'hard-coded' to match the style being used for momentum_flag**


	