#!/aging1/software/anaconda/bin/python
"""
Utilities for saving and printing JSON files.
"""

import os  # system functions
import json
from collections import OrderedDict


def write_json(json_dict, json_filename, subject_id='', instrument_prefix='', verbose=False):
    """ Write JSON output file"""

    with open(json_filename, 'w') as outfile:
        json.dump(json_dict, outfile, indent=4, ensure_ascii=True, sort_keys=False)

    if verbose:
        print_json_redcap_instrument(json_stats_filename)

    return


def print_json(in_json):
    """ Pretty Print JSON file"""
    if type(in_json) is dict or type(in_json) is OrderedDict:
        json_dict = in_json

    elif type(in_json) is str and os.path.isfile(in_json):
        with open(in_json, 'r') as infile:
            json_dict = json.load(infile, object_pairs_hook=OrderedDict)

    else:
        print('Unknown JSON type for printing')
        return

    print('')
    print(json.dumps(json_dict, indent=4, ensure_ascii=True, sort_keys=False))
    print(' ')

    return


def print_json_redcap_instrument(in_json):
    """ Print REdCap instrument measures to a JSON file"""
    print_json(in_json)
