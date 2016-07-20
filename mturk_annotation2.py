__author__ = 'Jonghyun Choi'
__email__ = "jonghyunc@allenai.org"

import simplejson as json
import boto.mturk.connection as tc
import amt_utils.process_hits as amt_util
import argparse
import sys

import pdb


def parseArguments():
    parser = argparse.ArgumentParser(description='Upload HITs to the mturk')
    parser.add_argument('-config', '--configfile', help='Configuration file', required=True)
    args = parser.parse_args()
    return args


def genFilelist():
    # parse annotated categories
    try:
        with open('/Users/jonghyunc/src/vision/datasets/shining3/categories.json', 'r') as file:
            categorydict = json.load(file)
    except Exception as e:
        print(e)
        return None
    return categorydict


def deunicodify_hook(pairs):
    new_pairs = []
    for key, value in pairs:
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        new_pairs.append((key, value))
    return dict(new_pairs)


if __name__ == '__main__':
    params = parseArguments()

    params_json = None
    with open(params.configfile, 'r') as f:
        params_json = json.load(f)

    if params_json == None:
        sys.exit()
        
    #
    hosturl = None
    if params_json["sandbox_or_real"] == "sandbox":
        print("Working in the SANDBOX with")
        hosturl = 'mechanicalturk.sandbox.amazonaws.com'
    elif params_json["sandbox_or_real"] == "real":
        print("Working in the REAL WORLD with")
        hosturl = 'mechanicalturk.amazonaws.com'
    else:
        print("error: unknown turk - %s" % params_json["sandbox_or_real"] )
        sys.exit()
    #
    mturk = tc.MTurkConnection(  # CAUTION: make sure your environmental variables for credential are set
        host = hosturl,
        debug = 1 # debug = 2 prints out all requests.
    )

    # print balance
    current_account_balance = mturk.get_account_balance()[0]
    print current_account_balance # a reminder of sandbox

    static_params = {
        'title': params_json['static_params']['title'],
        'description': params_json['static_params']['description'],
        'keywords': params_json['static_params']['keywords'],
        'frame_height': eval(params_json['static_params']['frame_height']),
        'amount': eval(params_json['static_params']['amount']),
        'duration': eval(params_json['static_params']['duration']),
        'lifetime': eval(params_json['static_params']['lifetime']),
        'max_assignments': eval(params_json['static_params']['max_assignments'])
    }

    # read categories.json
    categorydict = genFilelist()
    # read filelist to annotate
    with open(params_json["file_to_annotate"], 'r') as f:
        lines = [line.rstrip() for line in f]

    # get a list of duplicated images
    with open(params_json["duplicated_files"], 'r') as f:
        dups = [line.rstrip().split('/')[-1] for line in f]

    # generate pages to use
    pages_to_use = []
    for f in lines:
        if f in dups:  # todo
            print(f,'is duplicated image')
        else:
            pages_to_use.append(params_json['webpage_url']+"?image="+f+"&imageType="+categorydict[f])

    print(len(pages_to_use),'will be created for turkers to annotate')

    # # # create the HIT
    results = amt_util.create_hits_from_pages(mturk, pages_to_use, static_params)
    print(len(pages_to_use), "turker's job has been created")

    hitIds = [str(result[0].HITId) for result in results]
    print("all HITIds:", hitIds)
    with open(params_json["hit_id_output_file"], 'w') as f:
        for hitid in hitIds:
            f.write("%s\n" % hitid)
