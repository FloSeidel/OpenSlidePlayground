from docutils.utils.math.latex2mathml import mover
from imutils import paths
from shutil import copyfile
import argparse
import cv2
import os
import numpy as np
import PIL
import sys
#sys.path.append(os.path.abspath("~/Projects/SharpnessPythonConversion"))
#import fish


def fish_run(img):

    # convert color image to grayscale if necessary
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sv, map =fish.fish_bb_fi(img)
    return sv



def variance_of_laplacian(img):

    # convert color image to grayscale if necessary
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # destImage = [[0 for y in range(img.shape[1])] for x in range(img.shape[0])]
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    lap = cv2.Laplacian(src=img, ddepth=cv2.CV_64F)
    variance = lap.var()
    # print('Information about result array:\ntype: {}\nshape: {}\nelemtype: {}'
    #       '\nval: {}\nmin: {}\nmax: {}'
    #       .format(type(lap), lap.shape, type(lap[1, 1]), lap[1,1], lap.min(),
    #               lap.max()))
    # cv2.imshow("Laplacian", lap)
    # key = cv2.waitKey(0)
    return variance


def variance_of_laplacian_Wrapper(img, threshold):
    if isinstance(img, PIL.Image.Image):
        img = np.array(img)
    sv = variance_of_laplacian(img)
    sharp = True
    if sv <= threshold:
        sharp = False
    return sv, sharp


if __name__ == '__main__':
    print('Run SharpnessLibrary...')
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--images', dest='images', required=True,
                    help='path to input directory of images')
    ap.add_argument('-a' '--algorithm', dest='algorithm',
                    default='variance_of_laplacian',
                    help='algorithm, which is used to create sharpness value')
    ap.add_argument('-t', '--threshold', dest='threshold', type=float,
                    default=100.0, help='threshold')
    args = vars(ap.parse_args())

    if not os.path.exists(args['images']):
        raise FileNotFoundError('Passed directory path does not exist!')

    for imagepath in paths.list_images(args['images']):
        # print(imagepath)
        image = cv2.imread(imagepath)

        sv = 0.0
        if args['algorithm'] == 'variance_of_laplacian':
            sv = variance_of_laplacian(image)
        elif args['algorithm'] == 'fish':
            sv = fish_run(image)
        else:
            raise NotImplementedError('Algorithm is currently not implemented!')

        # use threshold
        text = 'not blurry'
        if sv < args['threshold']:
            text = 'blurry'

        # show image
        # cv2.putText(image, '{}: {:.2f}'.format(text, sv), (10, 30),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        # cv2.imshow('Image', image)
        # key = cv2.waitKey(0)

        movePath = imagepath
        if text == 'blurry':
            movePath = movePath.replace('tmpOutput', 'tmpOutput_blurry')
        else:
            movePath = movePath.replace('tmpOutput', 'tmpOutput_sharp')

        copyfile(imagepath, movePath)
        print('#################################\n'
              'Image: {}\n'
              'Sharpnessvalue: {}\n'
              'thresholdapplience: {}'
              .format(imagepath, sv, text))