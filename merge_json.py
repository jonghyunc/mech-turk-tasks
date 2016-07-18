from __future__ import print_function
from __future__ import division

import json
import os
import argparse
import boto.mturk.connection as tc
import cv2
import numpy as np
import sys
import progressbar as pgb
import amt_utils.process_hits as amt_util
import pdb

from shutil import copyfile

src = '/Users/jonghyunc/src/mech-turk-tasks/jsonout_more_20160715_morning/'
tgt = '/Users/jonghyunc/src/mech-turk-tasks/jsonout/'

if __name__ == "__main__":
    for root, dirs, files in os.walk(src):
        for file in files:
            if not file.split(".")[-1] == "json":
                continue
            srcfn = os.path.join(root, file)
            tgtfn = os.path.join(tgt, file)
            print(srcfn,'->',tgtfn)
            with open(srcfn, 'r') as jsonfn:
                outdict = json.load(jsonfn)
                # check the target file exists
                if os.path.exists(tgtfn):
                    with open(tgtfn, 'r') as jsonfn_t:
                        tgtdict = json.load(jsonfn_t)
                else:
                    # todo: copy
                    copyfile(srcfn, tgtfn)
                # update blobs only
                tgtdict['blobs'] = outdict['blobs']
                # write it back
                with open(tgtfn, 'w') as fp:
                    json.dump(tgtdict, fp, indent=4)


