#!/usr/bin/env python
#  redcapcheck:  download all records like the one in the specified JSON file
# CAHamilton  10/24/16

import sys
import argparse
import json
import get_api_key as gapi
import pandas as pd
from collections import OrderedDict
from io import StringIO
import redcap
import os


def redcap_check(project_name, json_filename, ini_filename):
    """
    Check results data in a JSON file compared to all other similar data in Redcap.
    Reads a specified JSON file and then downloads all matching info from other
    subjects and save this info to a CSV file.
    """

    print('Project= ', project_name)
    print('JSON file= ', json_filename)
    print('INI file= ', ini_filename)

    # ~~~~~~~~~~~~~~~ read the JSON file into a dictionary ~~~~~~~~~~~~~~~~~~~~~
    try:
        jfilep = open(json_filename, 'rt')
    except OSError:
        print('unable to open JSON file: {f}'.format(f=json_filename))
        sys.exit(0)

    jdict = json.load(jfilep, object_pairs_hook=OrderedDict)

    jfilep.close()

    # ~~~~~~~~~~~~~  read API keys from config file ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    api_token = gapi.get_api_key(ini_filename, project_name)

    if api_token == '000':
        print('Cannot find API key in INI file for the project name specified!')
        sys.exit(1)

    # ~~~~~~~~~~~~~~~~ connect to project ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    api_url = 'http://redcapint.tsi.wfubmc.edu/redcap_int/api/'

    project = 'empty'
    try:
        project = redcap.Project(api_url, api_token)
    except redcap.RedcapError:
        print('Unable to connect to TSI RedCap')

    print('Connected to RedCap project {a}'.format(a=project_name))

    # ~~~~~~~~~~~~~~  export records and dump to CSV file ~~~~~~~~~~~~~~~~~~~~~~~

    recs = project.export_records(fields=jdict.keys(), format='csv')

    # recs is a single string with \n between each record.  First record is headings.

    cfile = 'empty'
    try:
        cfile = json_filename+'.'+'dump.csv'
    except OSError:
        print('unable to open CSV output file: {f}'.format(f=cfile))

    # use pandas to read the recs string and save to CSV file in proper format

    df = pd.read_csv(StringIO(recs), sep=',')
    df.to_csv(cfile, index=False)

    print('{n} records downloaded to {a}'.format(n=df.shape[0], a=cfile))

if __name__ == "__main__":
    # ~~~~~~~~~~~~~~   parse command line   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    redcap_path = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        usage="redcap_check <RedCapProjectName> <JSONfile> <INIfile>",
        description="redcap_check: download JSON data from selected RedCap project")
    parser.add_argument("project", type=str,
                        help="name of RedCap project [CENC, Issues, CAHtest1]")
    parser.add_argument("jsonfile", type=str,
                        help="JSON file specifying records to download")
    parser.add_argument("--inifile", type=str,
                        help="file containing Redcap project API keys",
                        default=os.path.abspath(os.path.join(redcap_path, 'upcap.ini')))

    args = parser.parse_args()

    print('project= ', args.project)
    print('jsonfile= ', args.jsonfile)
    print('inifile= ', args.inifile)

    redcap_check(args.project, args.jsonfile, args.inifile)
