import openslideTest
import time


if __name__ == '__main__':

    startTime = time.time()
    path = '/media/bassist/extDrive/WSI/ESC3/3DH_HT/HT20x/3D-H-24.mrxs'

    resultMap = openslideTest.iterateOverWsi(path, (512, 512), 0)

    print('runtime: {}'.format(time.time() - startTime))
    print(resultMap)
    print('done...')


