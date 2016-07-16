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
    args = parser.parse_args()
    return args



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
        r_hits_current_batch = amt_util.get_completed_hits(mturk)
        assignment_results_current_batch = amt_util.get_assignments(mturk, r_hits_current_batch, 'Submitted')
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
    else:
        assignment_results_current_batch = {params.hitId: mturk.get_assignments(params.hitId, status=None)}

    if assignment_results_current_batch.keys()[0] == None:
        print("# annotations submitted: 0")
        sys.exit()

    print("# annotations are submitted:", len(assignment_results_current_batch))

    keymap = {49:'1', 50:'2', 51:'3', 52:'4', 53:'5', 54:'6', 55:'7', 56:'8', 57:'9', 58:'a', 117:'u', 85:'u', 105: 'i', 73:'i'}

    winNameIntersect = "intersection"
    winNameUnion = "union"
    cv2.namedWindow(winNameIntersect)
    cv2.namedWindow(winNameUnion)
    imageName = None
    for i, resultKey in enumerate(assignment_results_current_batch):
        img_mask = []  # polygon mask
        nPolygon = len(assignment_results_current_batch[str(resultKey)])
        img_org = []  # original image
        winName = [None]*len(assignment_results_current_batch[str(resultKey)])
        contours = {}  # all contours
        nValid = 0
        # check if json is already there
        aaa = assignment_results_current_batch[str(resultKey)]
        imageName = str(aaa[0].answers[0][0].fields[0])
        outfn = './jsonout/' + imageName + '.json'
        if os.path.exists(outfn):
            with open(outfn, 'r') as jsonfn:
                try:
                    outdict = json.load(jsonfn)
                except:
                    print(jsonfn)
                #
            if params.hitIdFile == 'hitidlist_blobs_bg.txt':
                if u'blob-bg' in outdict:
                    print("%s's blob-bg is already annotated! So, skip it!" % outfn)
                    continue
            elif params.hitIdFile == 'hitidlist_blobs.txt':
                if u'blobs' in outdict:
                    print("%s's blobs are already annotated! So, skip it!" % outfn)
                    continue
        for j, assignment in enumerate(assignment_results_current_batch[str(resultKey)]):
            # visualization window
            winName[j] = "a_"+str(j+1)
            cv2.namedWindow(winName[j])
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
                print(i + 1, '-', j + 1, ')', imageName, "'s answer has a problem")
                if j == 0:
                    img_mask = img_mask_cur
                continue
            print(i+1, '-', j+1, ')', imageName, '->', polygons)

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
            cv2.imshow(winName[j], img)
            cv2.waitKey(1)
            # mask computation
            if j == 0:
                img_mask = img_mask_cur
            else:
                img_mask[img_mask_cur > 0] += 1
            # assign to all contour variables
            contours[str(j+1)] = compatible_polygons
            nValid += 1

        if nValid == 0:
            print("no valid annotations found! So, skip it")
            continue

        # compute intersection and union
        img_intersect = np.zeros(img_mask.shape, dtype=np.uint8)
        img_union = np.zeros(img_mask.shape, dtype=np.uint8)

        img_intersect[img_mask == nValid] = 1
        img_union[img_mask > 0] = 1

        # obtain the polygons of intersection/union
        polygons_intersection = cv2.findContours(img_intersect, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # img_intersect is changed
        polygons_union = cv2.findContours(img_union, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # img_union is changed

        # visualize intersection polygon
        cv2.namedWindow(winNameIntersect)
        img = img_org.copy()
        for k, polygon in enumerate(polygons_intersection):
            if type(polygon) == list:
                cv2.polylines(img, polygon, True, (0, 0, 255), thickness=2)  # todo: without loop
        contours['i'] = polygons_intersection
        cv2.imshow(winNameIntersect, img)
        cv2.waitKey(1)

        # visualize union polygon
        cv2.namedWindow(winNameUnion)
        img = img_org.copy()
        for k, polygon in enumerate(polygons_union):
            if type(polygon) == list:
                cv2.polylines(img, polygon, True, (0, 0, 255), thickness=2)  # todo: without loop
        contours['u'] = polygons_union
        cv2.imshow(winNameUnion, img)
        key = None
        while(1):
            key = cv2.waitKey(0)
            if key in keymap or key == 113 or key == 81:
                break
            else:
                print("you press %s but press among annotation numbers, 'i', 'u' or 'q'" % key)

        # if key == 121 or key == 89:
        #     print("yes - approve")
        # elif key == 110 or key == 78:
        #     print("no - reject")
        # elif key == 113 or key == 81:
        #     print("quit")
        #     sys.exit(1)

        # accept the assignment
        # mturk_connection.approve_assignment(assignment)

        # reject the assignment
        # mturk_connection.reject_assignment(assignment, "polygon is not well aligned with the instructions")

        polygon_simple = []
        polygon_old_format = []
        if key in keymap:
            polygon_old_format = contours[keymap[key]]
            if keymap[key] == 'u' or keymap[key] == 'i':
                polygon_old_format = polygon_old_format[0]  # if it's output of cv2.findContours, the contour is nested in the first one
            for polygon in polygon_old_format:
                polygon_simple.append(polygon[0].tolist())
            print("\nchosen polygon - %s: %s" % (keymap[key], polygon_simple))
            # visualize intersection polygon
            cv2.namedWindow("final")
            img = img_org.copy()
            for k, polygon in enumerate(polygon_old_format):
                if type(polygon) == list:
                    cv2.polylines(img, polygon, True, (0, 0, 255), thickness=2)  # todo: without loop
            cv2.imshow("final", img)
            cv2.waitKey(0)
        elif key == 113 or key == 81:
            print("quit")
            sys.exit(1)

        # for j, _ in enumerate(assignment_results_current_batch[str(resultKey)]):
        #     cv2.destroyWindow(winName[j])

        # save to json
        outdict = {}
        outfn = './jsonout/'+imageName+'.json'
        # check previous json if so, update
        if os.path.exists(outfn):
            with open(outfn, 'r') as jsonfn:
                outdict = json.load(jsonfn)
        #
        if params.hitIdFile == 'hitidlist_blobs_bg.txt':
            outdict[u'blob-bg'] = polygon_simple
        elif params.hitIdFile == 'hitidlist_blobs.txt':
            outdict[u'blobs'] = polygon_simple
        # write
        with open(outfn, 'w') as fp:
            json.dump(outdict, fp, indent=4)
