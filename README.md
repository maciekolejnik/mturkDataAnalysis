# mturkDataAnalysis

This file analyses experimental data from the MTurk trust 
game experiment.

The data is assumed to be stored in Firestore Database 
(part of Firebase). Hence, GOOGLE_APPLICATION_CREDENTIALS
shell variable must be set to the location of credentials
json file to authenticate with Firestore.

analyse_data.py is the main file where analysis is performed,
but various aspects of the process are refactored into 
separate files.

backup_to_file.py reads a specified (hardcoded) document
from the database and backs it up by writing a file 
whose name must be provided (also hardcoded...).

