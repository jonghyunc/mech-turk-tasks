# %%capture
from __future__ import division
import numpy as np
import pandas as pd
import scipy.stats as st
import itertools
import math
from collections import Counter, defaultdict
# %load_ext autoreload
# %autoreload 2

#The lines commented below set the look and feel of mpl generated plots.
import matplotlib as mpl

import re
import pickle
import boto
import json
import os

import boto.mturk.connection as tc

import pdb


import amt_utils.process_hits as amt_util

import argparse

parser = argparse.ArgumentParser(description='Upload HITs to the mturk')


if __name__ == '__main__':
    ## Switch between sandbox and the real world here ##
    ## DON'T FORGET to change submission POST request in the client ##

    sandbox_host = 'mechanicalturk.sandbox.amazonaws.com'
    real_world_host = 'mechanicalturk.amazonaws.com'
    mturk = tc.MTurkConnection(  # CAUTION: make sure your environmental variables for credential are set
        # host = sandbox_host,
        host = real_world_host,
        debug = 1 # debug = 2 prints out all requests.
    )
    current_account_balance = mturk.get_account_balance()[0]
    if current_account_balance.amount == 10000:
        print "Working in the SANDBOX with"
    else:
        print "Working in the REAL WORLD with"
    print current_account_balance # a reminder of sandbox



    static_params = {
        'title': "Annotate Background of a Diagram",
        'description': "Outline the background of a diagram from the questions from a grade-school science",
        'keywords': ['image', 'annotation', 'background' ],
        'frame_height': 800,
        'amount': 0.02,
        'duration': 3600 * 12,
        'lifetime': 3600 * 24 * 3,
        'max_assignments': 3   # change to 3 when running for real
    }

    # TODO: parse it from the file
    pages_to_use = ["https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=61.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=787.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1262.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1266.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1267.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1268.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1275.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1308.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1309.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1310.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1311.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1314.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1316.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1321.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1474.png&imageType=volcano",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1480.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1484.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1485.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1487.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1489.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1493.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1494.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1495.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1498.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1502.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=1503.png&imageType=waterCNPCycle",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=4095.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=4107.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=4141.png&imageType=photosynthesisRespiration",
                    "https://s3-us-west-2.amazonaws.com/ai2-vision-turk-data/blobs-bg-3/html/objectPolygonsRound1/image_annotation3.html?image=5021.png&imageType=waterCNPCycle"
                    ]

    # create the HIT
    amt_util.create_hits_from_pages(mturk, pages_to_use, static_params)
