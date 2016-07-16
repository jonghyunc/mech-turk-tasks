from __future__ import print_function

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

from copy import deepcopy
import boto.mturk.connection as tc
import boto.mturk.question as tq
from boto.mturk.qualification import PercentAssignmentsApprovedRequirement, Qualifications, Requirement

import pdb

# These lines import my aws access keys
# from keysTkingdom import mturk_ai2
# from amt_utils.keysTkingdom import aws_tokes

import amt_utils.process_hits as amt_util
# import amt_utils.turk_email_utils as turkmail_util

import argparse

def parseArguments():
    parser = argparse.ArgumentParser(description='Tool to compare the annotations.')
    parser.add_argument('-hidf', '--hitIdFile', help='HIT ID File', required=True)
    args = parser.parse_args()
    return args



if __name__ == '__main__':
    params = parseArguments()

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
        print("Working in the SANDBOX with")
    else:
        print("Working in the REAL WORLD with")
    print(current_account_balance) # a reminder of sandbox

    if params.hitIdFile == "all":
        print("remove all")
        # remove all turk tasks associating with this requester's account
        amt_util.delete_all_hits(mturk)
    else:
        print("remove HITs in", params.hitIdFile)
        with open(params.hitIdFile, 'r') as f:
            hitIds = [line.rstrip() for line in f]
        for i, hitId in enumerate(hitIds):
            print(i, hitId)
            mturk.disable_hit(hitId)