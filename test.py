import numpy as np
from PIL import Image
import time
import math


def calcChromaFromPixel(red, green, blue):
    r = int(red)
    g = int(green)
    b = int(blue)
    return math.sqrt(math.pow(r - g, 2) +
                     math.pow(r - b, 2) +
                     math.pow(g - b, 2))


def calcChromaFromArray(arr):
    width, height, px = arr.shape
    if px != 3: # currently not supporting rgba
        raise IOError('Image in wrong format!')

    chromaCum = 0
    pxCount = 0
    for y in range(height):
        for x in range(width):
            chromaCum += calcChromaFromPixel(*arr[x, y])
            pxCount += 1

    return chromaCum / pxCount


def calcChromaFromImage(image):
    arr = np.array(image)
    return calcChromaFromArray(arr)


def calcChromaPerform(arr):
    width, height, px = arr.shape
    if px != 3:  # currently not supporting rgba
        raise IOError('Image in wrong format!')

    # convert to int in case uint array is given
    arr = arr.astype(np.int64)

    res = np.linalg.norm(np.stack(
        (arr[:,:,0] - arr[:,:,1],               # r - g
         arr[:,:,0] - arr[:,:,2],               # r - b
         arr[:,:,1] - arr[:,:,2])), axis=0)     # g - b

    return res.sum() / (width * height)

if __name__ == '__main__':


    #img = Image.open('/home/bassist/Desktop/tmpOutput/3D-H-24_x=19_y=162_lvl=0_chr=23-86.png')

    # starttime = time.time()
    # print(calcChromaFromImage(img))
    # print('time: {}'.format(time.time() - starttime))
    #
    # arr = np.array(img)
    # starttime = time.time()
    # print(calcChromaPerform(arr))
    # print('time: {}'.format(time.time() - starttime))


    # print(arr)
    # print(calcChromaFromArray2(arr))
    # res1 = calcChromaFromArray(arr)
    # print('Chroma: {}, calculated in {} seconds'
    #       .format(res1, time.time() - starttime))

    # print(imgJustWhite(arr))



    img = Image.open('test_bak.png').convert('L')
#    img.save('greyscale2.png')

    print(img.size)
    ar = np.asarray(img, dtype=np.float64)
    print(ar.shape)
    print(len(ar.shape))


    print(ar)