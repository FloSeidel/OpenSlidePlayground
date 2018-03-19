import openslideTest
import time
from PIL import Image
import numpy as np
import os

# static sharpness colors
col_background = np.array([255, 255, 255])
col_sharp = np.array([0, 255, 0])
col_blurry = np.array([255, 0, 0])

def run_sharpness_estimation(paths, outputPrefix="data/"):
    """runs the sharpness estimation for the given paths"""

    if os.path.exists(outputPrefix):
        os.makedirs(outputPrefix)

    for path in paths:
        startTime = time.time()
        filename = os.path.splitext(os.path.basename(path))[0]
        resultMap = openslideTest.iterateOverWsi(slidePath=path,
                                                 tileSize=(512, 512),
                                                 level=0)

        np.save(outputPrefix + "/{}_sharpness.npy".format(filename), resultMap)

        imgMap = resultMap.astype(np.uint8)
        img = Image.fromarray(imgMap)
        img.save(outputPrefix + "/{}_sharpnessmap.png".format(filename))

        cnt_background = np.sum(np.all(resultMap == col_background, axis=2))
        cnt_sharp = np.sum(np.all(resultMap == col_sharp, axis=2))
        cnt_blurry = np.sum(np.all(resultMap == col_blurry, axis=2))
        print("Map contains {} sharp pixels, {} blurry pixels and {} "
              "background pixels".format(cnt_sharp, cnt_blurry, cnt_background))

        print('Runtime for slide{}: {}'.format(filename, time.time()-startTime))


if __name__ == '__main__':

    outputDirPrefix = 'outData/'
    rootDir = '/media/bassist/extDrive/WSI/ESC3/3DH_HT/HT20x/'
    files = [f for f in os.listdir(rootDir)
             if os.path.isfile(os.path.join(rootDir, f)) and f.endswith('.mrxs')]
    files = [rootDir + f for f in files]
    print('I\'m now estimating the sharpness to the following slides: {}'
          .format(files))
    run_sharpness_estimation(files, outputPrefix=outputDirPrefix)

    # startTime = time.time()
    # # path = '/media/bassist/extDrive/WSI/ESC3/3DH_HT/HT20x/3D-H-24.mrxs'
    # path = '/media/bassist/extDrive/WSI/strangeSharpness/wsi-bck/2018-01-09/E2017072037P1-L-1_E-HE_00000000000040ED.ndpi'
    # resultMap = openslideTest.iterateOverWsi(slidePath=path,
    #                                          tileSize=(512, 512),
    #                                          level=1) #0
    # filename = os.path.splitext(os.path.basename(path))[0]
    # print(resultMap.shape)
    # np.save("{}_sharpness.npy".format(filename), resultMap)
    # # with np.load("sharpness.npy") as resultMap:
    # resultMap = np.load("{}_sharpness.npy".format(filename))
    # # resultMap = np.fromfile("sharpness.npy")
    # # print(resultMap.shape)
    # # width = resultMap.shape[0]
    # # height = resultMap.shape[1]
    #
    # resultMap = resultMap.astype(np.uint8)
    # img = Image.fromarray(resultMap)
    # img.save("{}_sharpnessmap.png".format(filename))
    #
    #
    #
    # # build sum of boolean array
    # cnt_background = np.sum(np.all(resultMap == col_background, axis=2))
    # cnt_sharp = np.sum(np.all(resultMap == col_sharp, axis=2))
    # cnt_blurry = np.sum(np.all(resultMap == col_blurry, axis=2))
    #
    # print("Map contains {} sharp pixels, {} blurry pixels and {} "
    #       "background pixels".format(cnt_sharp, cnt_blurry, cnt_background))


    # print('runtime: {}'.format(time.time() - startTime))
    # print(resultMap)
    # np.save("sharpness.npy", resultMap)
    # np.savetxt("sharpness.txt", resultMap)

    # resultMap = np.fromfile("sharpness.npy")
    # todo prepare resultmap to look like a sharpness heatmap
    # Image.fromarray(resultMap)
    # if resultMap.max() == 0 and resultMap.min() == 0:
    #     print('contains nothing')
    # elif resultMap.max() == 255 and resultMap.min() == 255:
    #     print('contains just white')
    # else:
    #     print('happy')


    # img = Image.new(mode="RGB", size=(width, height))
    # img.putdata(resultMap)

    # for x in range(width):
    #     for y in range(height):
    #         img[x,y] = resultMap[x,y]

    # img.save("test.png")



    print('done...')


