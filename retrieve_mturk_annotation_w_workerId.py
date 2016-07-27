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


def parseArguments():
    parser = argparse.ArgumentParser(description='Tool to compare the annotations.')
    parser.add_argument('-in', '--imageDir', help='Directory containing images', required=True)
    parser.add_argument('-hid', '--hitId', help='HIT ID', required=False)
    parser.add_argument('-hidf', '--hitIdFile', help='HIT ID File', required=False)
    parser.add_argument('-wid', '--workerId', help='worker ID to retrieve the jobs', required=False)
    args = parser.parse_args()
    return args


keymap = {49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9', 58: 'a', 117: 'u', 85: 'u',
          105: 'i', 73: 'i'}

if __name__ == '__main__':
    params = parseArguments()
    imgDir = params.imageDir
    #
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


    # get the results
    if not params.hitId and not params.hitIdFile:
        r_hits_current_batch = mturk.get_all_hits()
    if params.workerId:
        print('getting tasks done by %s' % params.workerId)
        r_hits_current_batch = mturk.get_all_hits()
        assignments_for_workerid = []
        for hit in r_hits_current_batch:
            hit_assignments = mturk.get_assignments(hit.HITId)
            for hit_assignment in hit_assignments:
                if str(hit_assignment.WorkerId) == params.workerId:
                    assignments_for_workerid.append(hit_assignment)
        print('total # tasks done by %s is %d' %(params.workerId, len(assignments_for_workerid)))
    elif params.hitIdFile:
        with open(params.hitIdFile, 'r') as f:
            hitIds = [line.rstrip() for line in f]
        assignment_results_current_batch = {}
        print("# HITs: %d" % len(hitIds))
        # progress bar
        widgets = ['Collecting HITs: ', pgb.Percentage(), ' ', pgb.Bar(marker=pgb.RotatingMarker()), ' ', pgb.ETA(),
                   ' ']  # , pgb.FileTransferSpeed()]
        pbar = pgb.ProgressBar(widgets=widgets, maxval=100)
        pbar.start()
        for j, hitid in enumerate(hitIds):
            pbar.update(j*100/len(hitIds))
            assignment_results_current_batch[hitid] = mturk.get_assignments(hitid, status=None)
        pbar.finish()
    elif params.hitId:
        assignment_results_current_batch = {params.hitId: mturk.get_assignments(params.hitId, status=None)}

    # if assignments_for_workerid.keys()[0] == None:
    #     print("# annotations submitted: 0")
    #     sys.exit()
    #
    # print("# annotations are submitted:", len(assignment_results_current_batch))

    imageName = None
    winName = "a"
    cv2.namedWindow(winName)
    for j, assignment in enumerate(assignments_for_workerid):
        # visualization window
        # get answer
        ans = assignment.answers[0]
        # get image name
        imageName = str(ans[0].fields[0])
        # for visualize the results
        img_org = cv2.imread(os.path.join(imgDir,imageName))
        img = img_org.copy()
        img_mask_cur = np.zeros([img.shape[0], img.shape[1], 1])  # annotation mask to compute the intersection or union of the annotations
        # get the polygons
        polygons = json.loads(ans[1].fields[0])
        if len(polygons) == 0:
            print(j + 1, ')', imageName, "'s answer has a problem")
            if j == 0:
                img_mask = img_mask_cur
            continue
        print(j+1, ')', imageName, '->', polygons)

        # change the polygon to opencv polygon
        compatible_polygons = []
        for k, polygon in enumerate(polygons):
            pts = np.array(polygon, np.int32)
            pts = pts.reshape((-1,1,2))
            # put the polygon to the image for visualization
            cv2.polylines(img, [pts], True, (0, 0, 255), thickness=2)  # todo: without loop
            # put the polygon filled to compute the intersection or union
            cv2.fillPoly(img_mask_cur, [pts], 1)
            compatible_polygons.append([pts])
        # visualize
        cv2.imshow(winName, img)
        while (1):
            key = cv2.waitKey(0)
            if key in keymap or key == 113 or key == 81:
                break
            else:
                print("you press %s but press among annotation numbers, 'i', 'u' or 'q'" % key)
        if key == 113 or key == 81:
            print("quit")
            sys.exit(1)

