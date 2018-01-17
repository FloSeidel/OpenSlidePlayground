import openslide
from PIL import Image
import os
import errno
import numpy as np
import time
import sys

from multiprocessing import Pool
from itertools import product

def convert_RGBA2RGB(rgba_img):
    """Converts a RGBA Pillow image to a RGB image.
    :param rgba_img: RGBA-image
    :type rgba_img"""
    # img = pillow image
    # Returns the given image in rgb mode.

    # if image is already in rgb mode
    if rgba_img.mode == 'RGB':
        return rgba_img
    # throw error if image is not in rgba mode
    elif rgba_img.mode != 'RGBA':
        raise ValueError('Image is not in RGBA mode ({})'.format(rgba_img.mode))
    # convert rgba to rgb
    rgb_img = Image.new("RGB", rgba_img.size, (255, 255, 255))
    rgb_img.paste(rgba_img, mask=rgba_img.split()[3]) # 3 is the alpha channel (rgba)
    return rgb_img


def processTile(resultMap, slidePath, tileX, tileY, tileSize = None, level = 0):
    if tileSize is None:
        tileSize = (512, 512)

    with openslide.open_slide(slidePath) as slide:
        # raise if level is not supported in slide
        if level >= slide.level_count or level < 0:
            raise OverflowError('wsi level not available ({})'.format(level))

        slideW, slideH = slide.level_dimensions[level]
        slideX = tileX * tileSize[0]
        slideY = tileY * tileSize[1]
        location = (slideX, slideY)

        # check if given tile position can be accessed
        if slideX + tileSize[0] > slideW or slideY + tileSize[1] > slideH:
            raise OverflowError('given level ({}: {}) is smaller than given '
                                'location: {}'.format(level, (slideW, slideH),
                                                      location))
        with get_image_region(slide, location, tileSize, level) as img:
            tileResult = processExtractedImage(img, slidePath,
                                               (tileX, tileY),
                                               level)
            # print('result for tile: ({}, {}): {}'.format(tileX, tileY,
            #                                              tileResult))
            resultMap[tileX, tileX] = tileResult
            # sharpnessValues[tileX][tileY] = evaluateSharpness(img)


def processExtractedImage(img, slidePath, tilePos, level):
    """Currently just saves the given image if it contains more than just white
    and the chroma is greater than 20. If no error occurred True is returned,
    otherwise False.
    :param img: image
    :type img: PIL image
    :param slidePath: path to WSI
    :type slidePath: string
    :param tilePos: position of the image in the given WSI
    :type tilePos: tuple of int (width, height)
    :param level: level-origin of the image from the wsi
    :type level: int
    :return value that indicates, that the the process was successful or not
    :rtype boolean
    """
    try:
        # continue if image just contains white pixels
        if imgJustWhite(img):
            raise AssertionError('Image contains just white')
        # calculate chroma of the extracted image
        chroma = calcChromaFromImage(img)
        # continue if image probably just background
        if chroma < 20:
            raise AssertionError('Chroma value is under 20')

        filename = os.path.splitext(os.path.basename(slidePath))[0]
        filename += '_x=' + str(tilePos[0])
        filename += '_y=' + str(tilePos[1])
        filename += '_lvl=' + str(level)
        filename += '_chr=' + str(round(chroma, 2)).replace('.', '-')
        filename += '.png'
        saveImg(img, filename)
        return True
    except:
        exc = sys.exc_info()
        print('{}: {}'.format(exc[0], exc[1]))
        return False



def processTileCallback(result):
    """ Callback for processTile function. Currently nothing is done here!"""
    print("callback method called: {}".format(result))

    # do nothing
    return


def iterateOverWsi(slidePath, tileSize = None, level = 0):
    """Iterates parallel over the given WSI. If no tileSize is given a (512x512)
    Tile is assumed. If nothing else is specified the baselayer is assumed as
    level
    :param slidePath: path to wsi
    :type slidePath: string
    :param tileSize: size of the tiles which are processed (default: (512x512))
    :type tileSize: tuple of int (width, height)
    :param level: layer of the wsi (default: 0)
    :type level: int
    :return: nothing
    :rtype:
    """

    # throw if given slidePath cannot be found
    if not os.path.exists(slidePath):
        raise FileNotFoundError('slide could not be found ({})'
                               .format(slidePath))

    # use default tileSize if nothing else is passed
    if tileSize is None:
        tileSize = (512, 512)  # current default

    resultMap = None
    resultW, resultH = 0, 0
    with openslide.open_slide(slidePath) as slide:
        # leave if level is not supported
        if level >= slide.level_count or level < 0:
            raise OverflowError('wsi level not available ({})'.format(level))
        slideWidth, slideHeight = slide.level_dimensions[level]
        resultW = slideWidth // tileSize[0]
        resultH = slideHeight // tileSize[1]

    # init result heatMap
    resultMap = [[0 for x in range(resultW)] for y in range(resultH)]

    print('Starting threadpool')
    # start thread pool (multithreading.Pool())
    pool = Pool()
    for tileX in range(resultW):
        for tileY in range(resultH):
            # start processTile function foreach tile in wsi
            pool.apply_async(func=processTile,
                             args=(resultMap, slidePath, tileX, tileY, tileSize, level),
                             callback=processTileCallback)
    pool.close()
    pool.join()

    return resultMap

def saveImg(image, name = None):
    # debug mode...just save this image

    if name is None:
        name = 'imagetest.png'
    if not name.endswith('.png'):
        name += '.png'

    dirPath = os.path.dirname(name)
    if dirPath != '':
        try:
            os.makedirs(dirPath)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    image.save(name)


def imgJustWhite(image):
    allWhite = False

    extrema = image.convert("L").getextrema()
    # if extrema == (0, 0):
    #     # all black
    if extrema == (255, 255):
        # all white
        allWhite = True

    return allWhite

def calcChromaFromImage(image):
    chromaCum = 0
    pxCount = 0
    arr = np.array(image)
    width, height, px = arr.shape

    if px != 3: # currently not supporting argb
        raise IOError('Image in wrong format!')

    for y in range(height):
        for x in range(width):
            pixel = arr[x,y]
            chromaCum += calcChromaFromPixel(pixel[0], pixel[1], pixel[2])
            pxCount += 1

    return chromaCum / pxCount

def calcChromaFromPixel(red, green, blue):
    r = int(red)
    g = int(green)
    b = int(blue)
    return abs(int(r) - g) + abs(r - b) + abs(g - b)

def evaluateSharpness(image):
    raise NotImplementedError("lazy programer ;)")


def get_macro_image(slide):
    raise NotImplementedError


def get_label_image(slide):
    raise NotImplementedError


def get_thumbnail_image(slide):
    raise NotImplementedError


def get_thumbnail_with_max_size(slide, size):
    return slide.get_thumbnail(size)


def get_associated_images(slide):
    # get images
    label = get_label_image(slide)
    macro = get_macro_image(slide)
    thumbnail = get_thumbnail_image(slide)

    return label, macro, thumbnail


def get_image_region(slide, location, size=(512, 512), level=0):
    # slide:
    # location (tuple) – (x, y) tuple giving the top left pixel in the level
    # 0 reference frame
    # level (int) – the level number (0 is base layer)
    # size (tuple) – (w, h) tuple giving the region size

    # read region returns rgba image
    region = slide.read_region(location, level, size)
    return convert_RGBA2RGB(region)

def get_foreground_positions_from_sharpnessmap(sharpness_map_path):
    positions = []
    img = Image.open(sharpness_map_path)
    width, height = img.size
    for x in range(width):
        for y in range(height):
            val = img.getpixel((x,y))
            
            # print (type(val))
            if val != (255, 255, 255, 255):
                positions.append((x,y))

    return positions


if __name__ == '__main__':
    
    # initialize slide
    # slidePath = '/home/bassist/WSIs/1M01.mrxs'
    sharpnessMapPath = '/home/bassist/WSIs/E2017069762P1-a-8_GBG-53BP1_0000000000003C55/meta/sharpness/E2017069762P1-a-8_GBG-53BP1_0000000000003C55.debug.Png'
    ndpiSlidePath = '/home/bassist/WSIs/E2017069762P1-a-8_GBG-53BP1_0000000000003BE7/E2017069762P1-a-8_GBG-53BP1_0000000000003BE7.ndpi'

    # openslide is not capable of reading vsf!
    # vsfSlidePath = '/home/bassist/WSIs/E2017069762P1-a-8_GBG-53BP1_0000000000003C55/E2017069762P1-a-8_GBG-53BP1_0000000000003C55.vsf'

    dirPath = '/home/bassist/Desktop/tmpOutput6'



    # slidePath = '/home/bassist/WSIs/533-13_HG.ndpi'

    # slide = openslide.open_slide(ndpiSlidePath)
    with openslide.open_slide(ndpiSlidePath) as slide:

        # ATTENTION
        wsiDim = slide.dimensions[0] # gets width
        wsiDim = slide.level_dimensions[0] # get dimensions from baselayer



    # # get foreground positions from the sharpnessmap
    # foregroundPos = get_foreground_positions_from_sharpnessmap(sharpnessMapPath)
    #
    # # saving tissue tiles
    # for pos in foregroundPos:
    #     level = 1    # because sharpnessmap was created with scale 0.5
    #     wsipos = tuple(1024 * x for x in pos)    # wsi base layer coordinates
    #     tilesize = (512, 512)
    #     img = get_image_region(slide, wsipos, level, tilesize)
    #     img.save('tmp/wsi_x={}_y={}.jpg'.format(wsipos[0], wsipos[1]))

    # # get some slide information
    # print('level_count: {}'.format(slide.level_count))
    # print('dimensions: {}'.format(slide.dimensions))
    # print('level_dimensions: {}'.format(slide.level_dimensions))
    # print('level_downsamples: {}'.format(slide.level_downsamples))
    # # print('properties: {}'.format(slide.properties))
    # print('associated_images: {}'.format(slide.associated_images))

    # get thumbnail image with maximum size
    # get_thumbnail_with_max_size(slide, (2000, 20000)).save('thumbnail_max.jpg')

    # 1194x407 (wxh)
    # for lvl in range(slide.level_count):
    #     img = get_image_region(slide, (0, 0), lvl, (512, 512))
    #     img.save('level_{}.jpg'.format(lvl))

    # extract and save meta images (associated_images)
    # for name, image in slide.associated_images.items():
    #     eprint('saving {} image'.format(name))
    #     convert_RGBA2RGB(image).save('{}.jpg'.format(name))

    # releasing slide object
    # slide.close()
    # slide.read_region(location=(0,0), level=0, size=(512, 512))

