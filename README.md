# mturkDataAnalysis

This file analyses experimental data from the MTurk trust 
game experiment.

Two ways of providing the data are supported:
1. (Preferred) A JSON file, whose name must be specified in
```analyse_data.py```. 
2. A database; in particular Firestore Database with 
GOOGLE_APPLICATION_CREDENTIALS shell variable set to the location
of credentials json file to authenticate with Firestore and HIT_ID
hardcoded in ```analyse_data.py``` file

analyse_data.py is the main file where analysis is performed,
but various aspects of the process are refactored into 
separate files.

backup_to_file.py reads a specified (hardcoded) document
from the database and backs it up by writing a file 
whose name must be provided (also hardcoded...).

