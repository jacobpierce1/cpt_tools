# Mass Identifier

## INSTRUCTIONS: 

Run from within the directory mass_identifier (the folder where the file mass_identifier.py is located):


syntax: ipython mass_identifier.py  mode  omega  d_omega  [optional query args] 

	mode: 	0 for all ions 
		1 for all ions and known molecules

	optional query args: 
		min_half_life FLOAT 
		min_cf_yield FLOAT 
		small_molecule_size INT 
		max_charge INT

	example: to check all molecules in DB with max charge of 1 and defaults for other params: 
		ipython mass_identifier.py 1 616024 0.5 max_charge 1  




If you forget the syntax, just type ipython mass_identifier.py and it will print out the above message.

The first time you run the program in molecule mode (mode 1), a database will be generated containing the masses of all molecules with nuclide combinations meeting the half life, cf yield, molecule size, and abundance criteria in the code. For subsequent calls in molecule mode, the same database will be used and metadata about the database (what criteria were used to select molecules / nuclides ) will be printed. If you want to regenerate the database with different criteria, just set delete the database on your computer (it’s located in the directory ‘storage’) and set the desired criteria using the optional query args described above. If you don’t set one or more of the parameters, default values will be used.  

In the future I can add support for a command line argument to reset the molecule database, but I doubt that would be used very frequently. 






## KNOWN PROBLEMS

The program contains file ‘molecule_parser.py’ which has a function called atom counter. That function returns a list of Z values for each element in a molecule string. For example, ‘CH3I’ —> (6, 1, 53), ( 1, 3, 1) . Currently, atom_counter does not provide support for hydrates (which is a solvable problem, but will take a bit more effort) or molecules with a charge state specified NOT at the end of the string. Ambiguously charged molecules with a charge state higher than 1 specified at the end of the string such that the molecule is ambiguoous are ignored. For example, ’NH32-‘ could be two different molecules: ’NH3 2-‘ or ’NH32 -‘. To solve that, I manually went through the list of molecules and put spaces at the end for these ambiguous charge states, but if more molecules are added this same measure will need to be taken. 

In any case, if you see in the output a hydrate (which you shouldn’t see, as the atom_counter function should ignore them) or a molecule with a charge state higher than 1 specified in the middle of the molceule (e.g. CH32+I), then you can assume its mass was computed incorrectly. 

This will be an important bug to fix in the future, because I believe the usual syntax for amino acids, which probably are present in fingerprints, contains a charge state specified in the middle of the string. 

At the time of writing, the database does not handle large molecules (which at the time of writing is defined to be a molecule with more than 8 atoms). That will be fixed very soon. 

Finally, for carbon-based molecules there will be some repeats because there are some redundant carbon-based molecules in the list of molecules used since I took lists for several different locations. I know of a way to solve this which is not much effort, but to implement the solution without any side effects (i.e. removing too many molecules) will take some nontrivial testing. So I have not implemented it yet. 





## SUMMARY OF HOW PROGRAM WORKS 

Todo 