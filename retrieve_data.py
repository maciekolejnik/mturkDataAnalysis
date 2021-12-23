# this file contains methods for retrieving experimental data
# initially this was done by querying database, but that makes
# little sense given that we run it frequently and have limited
# number of reads. Therefore the preferred method is to read data
# from a file
import json


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
