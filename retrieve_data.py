# this file contains methods for retrieving experimental data
# initially this was done by querying database, but that makes
# little sense given that we run it frequently and have limited
# number of reads. Therefore the preferred method is to read data
# from a file

from google.cloud import firestore
from enum import Enum
import json


class DataSource(Enum):
    FILE = 0
    DB = 1


# returns data as a dictionary mapping user ids
# to dictionaries representing data for that user
def get_data(hit_id, file_name, source):
    if source == DataSource.FILE:
        return read_data_from_file(file_name)
    elif source == DataSource.DB:
        return read_data_from_db(hit_id)


def read_data_from_file(file_name):
    f = open(file_name)
    data = json.load(f)

    # print some basic numerical info about the data
    # (how many passed comprehension check, how many got approved etc)
    print(f'There were {len(data.keys())} plays recorded.')

    # order_by not only orders but also filters on existence
    approved_assignments = \
        {k: v for k, v in data.items() if 'approved' in v['timestamps']}
    print(f'Out of these, {len(approved_assignments)}' +
          ' submitted an assignment which got approved.')

    comprehension_passed = {k: v for k, v in approved_assignments.items()
                            if 684 in v['comprehension']}
    print(f'Out of these, {len(comprehension_passed)}' +
          ' participants passed the comprehension check.')

    completed_game = \
        {k: v for k, v in comprehension_passed.items() if 'earned' in v}
    print(f'Out of these, {len(completed_game)} participants completed the' +
          ' game and gave us useful data points.')
    return completed_game


def read_evals_from_file(file_name):
    f = open(file_name)
    data = json.load(f)
    return data


def get_evals(hit_id, file_name, source):
    if source == DataSource.FILE:
        return read_evals_from_file(file_name)
    elif source == DataSource.DB:
        return read_evals_from_file(hit_id)


def read_evals_from_db(hit_id):
    db = firestore.Client()
    prediction_evaluations_collection = db.collection(f'{hit_id}evals')
    snapshots = list(prediction_evaluations_collection.stream())
    return {snap.id: snap.to_dict() for snap in snapshots}


def read_data_from_db(hit_id):
    db = firestore.Client()

    # use appropriate HIT ID below
    plays_collection = db.collection(hit_id)

    # print some basic numerical info about the data
    # (how many passed comprehension check, how many got approved etc)
    print(f'There were {len(list(plays_collection.stream()))} plays recorded.')

    # order_by not only orders but also filters on existence
    approved_assignments_ref = plays_collection.order_by(u'timestamps.approved')
    print(f'Out of these, {len(list(approved_assignments_ref.stream()))}'
          f' submitted an assignment which got approved.')

    comprehension_passed_ref = \
        approved_assignments_ref.where(u'comprehension', u'array_contains', 684)
    print(f'Out of these, {len(list(comprehension_passed_ref.stream()))}'
          f' participants passed the comprehension check.')

    completed_game_ref = comprehension_passed_ref.order_by(u'earned')
    print(f'Out of these, {len(list(completed_game_ref.stream()))}'
          f' participants completed the game and gave us useful data points.')

    completed_plays = list(completed_game_ref.stream())
    return {full_play.id: full_play.to_dict() for full_play in completed_plays}
