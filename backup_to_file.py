from google.cloud import firestore
import json

# STEP 1: retrieve plays from the database
db = firestore.Client()
# use appropriate HIT ID below
plays_collection = db.collection(u'3HJ1EVZS3T8TBOSXTPWY3UWPO5NR34')

backup = {}
for full_play in plays_collection.stream():
    backup[full_play.id] = full_play.to_dict()

backupAsJson = json.dumps(backup, indent = 4, sort_keys = True, default = str)
print(backupAsJson)

backupFile = open('firstStudyBackup.txt', 'w')
backupFile.write(backupAsJson)
backupFile.close()