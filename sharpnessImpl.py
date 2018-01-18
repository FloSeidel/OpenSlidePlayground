from imutils import paths
import argparse
import cv2
import os


def variance_of_laplacian(img):

    # convert color image to grayscale if necessary
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(img, cv2.CV_64F).var()



if __name__ == '__main__':
    print('Run SharpnessLibrary...')
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--images', dest='images', required=True,
                    help='path to input directory of images')
    ap.add_argument('-a' '--algorithm', dest='algorithm', required=True,
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

        # use threshold
        text = 'not blurry'
        if sv < args['threshold']:
            text = 'blurry'

        # show image
        cv2.putText(image, '{}: {:.2f}'.format(text, sv), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        cv2.imshow('Image', image)
        key = cv2.waitKey(0)