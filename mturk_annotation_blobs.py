
import json

import boto.mturk.connection as tc

import pdb


import amt_utils.process_hits as amt_util

import argparse

parser = argparse.ArgumentParser(description='Upload HITs to the mturk')

def genFilelist():
    # parse annotated categories
    try:
        with open('/Users/jonghyunc/src/vision/datasets/shining3/categories.json', 'r') as file:
            categorydict = json.load(file)
    except Exception as e:
        print(e)
        return None
    return categorydict


if __name__ == '__main__':
    sandbox_host = 'mechanicalturk.sandbox.amazonaws.com'
    real_world_host = 'mechanicalturk.amazonaws.com'
    mturk = tc.MTurkConnection(  # CAUTION: make sure your environmental variables for credential are set
        host = sandbox_host,
        # host = real_world_host,
        debug = 1 # debug = 2 prints out all requests.
    )
    current_account_balance = mturk.get_account_balance()[0]
    if current_account_balance.amount == 10000:
        print "Working in the SANDBOX with"
    else:
        print "Working in the REAL WORLD with"
    print current_account_balance # a reminder of sandbox



    static_params = {
        'title': "Annotate Objects in a Diagram",
        'description': "Outline each objects in a diagram from the questions from a grade-school science",
        'keywords': ['image', 'annotation', 'background' ],
        'frame_height': 800,
        'amount': 0.05,
        'duration': 3600 * 12,
        'lifetime': 3600 * 24 * 3,
        'max_assignments': 1   # change to 3 when running for real
    }

    # read categories.json
    categorydict = genFilelist()
    # read filelist to annotate
    with open('/Users/jonghyunc/src/vision/datasets/shining3-potential/file_to_annotate_blobs_more.txt', 'r') as f:
        lines = [line.rstrip() for line in f]

    # get a list of duplicated images
    with open('/Users/jonghyunc/src/vision/utils/bin/dup.txt', 'r') as f:
        dups = [line.rstrip() for line in f]

    # generate pages to use
    pages_to_use = []
    cnt = 0
    for f in lines:
        if "../../datasets/shining3/images/"+f in dups:
            print(f,'is duplicated image')
        else:
            cnt += 1
            pages_to_use.append("https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-july2016/html/objectPolygons/image_annotation2.html?image="+f+"&imageType="+categorydict[f])
            # if cnt > 10:
            #     break

    print(len(pages_to_use),'will be created for turkers to annotate')

    # # create the HIT
    results = amt_util.create_hits_from_pages(mturk, pages_to_use, static_params)
    print(len(pages_to_use), "turker's job has been created")

    hitIds = [str(result[0].HITId) for result in results]
    print("all HITIds:", hitIds)
    with open('hitidlist_blobs_more.txt', 'w') as f:
        for hitid in hitIds:
            f.write("%s\n" % hitid)
