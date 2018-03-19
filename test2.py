import math
import numpy as np
import time
np.random.seed(23)
from PIL import Image
# FAKE-DATA
# img = np.random.randint(0,256,size=(512,512,3))
img2 = Image.open('/home/bassist/Desktop/tmpOutput/3D-H-24_x=19_y=162_lvl=0_chr=23-86.png')
img = np.array(img2)
img = img.astype(np.int64)

# LOOP APPROACH
def calcChromaFromPixel(red, green, blue):
    r = int(red)
    g = int(green)
    b = int(blue)
    return math.sqrt(math.pow(r - g, 2) +
                     math.pow(r - b, 2) +
                     math.pow(g - b, 2))


starttime = time.time()
bla = np.zeros(img.shape[:2])
for a in range(img.shape[0]):
    for b in range(img.shape[1]):
        bla[a,b] = calcChromaFromPixel(*img[a,b])  # makes [1 1 1] to 1 1 1
print(bla.sum() / (bla.shape[0] * bla.shape[1]))
print('loop: {}'.format(time.time() - starttime))

# VECTORIZED APPROACH
starttime = time.time()
# img = np.array(img2)
print(img.shape)
stack = np.stack(
        (img[:,:,0] - img[:,:,1],
         img[:,:,0] - img[:,:,2],
         img[:,:,1] - img[:,:,2]))
print(stack.shape)
# https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.linalg.norm.html
# default norm is Frobenius norm is exactly what I want
# sqrt(sum(pow(val1), pow(val2), pow(val3), ..., pow(val_x)))
res = np.linalg.norm(stack, axis=0)
print(res.sum() / (res.shape[0] * res.shape[1]))
print('vectorized: {}'.format(time.time() - starttime))
