#!/usr/bin/env python

# redcap_upload:  upload JSON results to Redcap
# CAHamilton

import sys
import argparse
import get_api_key as gapi
import json
from collections import OrderedDict
import redcap
import os


def redcap_upload(project_name, json_filename, ini_filename):
    """
    Uploads a JSON file to a project in Redcap.

    arguments:

      project_name:  must match one of the projects listed in INI file

      json_filename: file containing the results to upload

      ini_filename:  file containing the API keys for Redcap projects

    """

    # ~~~~~~~~~~~~~  read the JSON file into a dictionary ~~~~~~~~~~~~~~~~~~~~~

    try:
        jfilep = open(json_filename, 'rt')
    except OSError:
        print('unable to open JSON file: {f}'.format(f=json_filename))
        sys.exit(1)

    jdict = json.load(jfilep, object_pairs_hook=OrderedDict)

    jfilep.close()

    print('read JSON file OK')

    # ~~~~~~~~~~~~~  read API keys from config file ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    api_token = gapi.get_api_key(ini_filename, project_name)

    if api_token == '000':
        print('Cannot find API key in INI file for the project name specified!')
        sys.exit(1)

    print('api_token=',api_token)
    # ~~~~~~~~~~~~~  connect to Redcap project  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    api_url = 'http://redcapint.tsi.wfubmc.edu/redcap_int/api/'

    try:
        project = redcap.Project(api_url, api_token)
    except redcap.RedcapError:
        print('Unable to connect to TSI RedCap')
        sys.exit(1)

    print('Project =', project_name)
    print('subject_id=', jdict['subject_id'])

    # ~~~~~ upload dictionary one item at the time so error can be identified, ~~~~~
    #         note: it needs to be a list
    count = 0
    for key, val in jdict.items():
        if key != 'subject_id':

            count += 1

            try:
                project.import_records([{'subject_id': jdict['subject_id'], key: val}])
                print('uploading {a} of {b}: {c}'.format(a=count, b=len(jdict)-1, c=key))
            except redcap.RedcapError:
                print('Error uploading item {a}: {b}'.format(a=count, b=key))


if __name__ == "__main__":

    # ~~~~~~~~~~~~~~   parse command line   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    redcap_path = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        usage="redcap_upload <RedCapProjectName> <JSONfile> <INIfile>",
        description="redcap_upload: upload JSON data to selected RedCap project")
    parser.add_argument("project", type=str,
                        help="name of RedCap project (CENC, Issues)"),
    parser.add_argument("jsonfile", type=str,
                        help="JSON file to upload")
    parser.add_argument("--inifile", type=str,
                        help="file containing Redcap project API keys",
                        default=os.path.abspath(os.path.join(redcap_path,'upcap.ini')))

    args = parser.parse_args()

    print('project= ', args.project)
    print('jsonfile= ', args.jsonfile)
    print('inifile= ', args.inifile)

    redcap_upload(args.project, args.jsonfile, args.inifile)
