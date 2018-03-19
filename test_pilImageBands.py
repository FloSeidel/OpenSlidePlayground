from PIL import Image

# org_img = Image.open().convert('L')
# org_img = np.loadtxt('/home/bassist/Testdata.txt')



filename = "/home/bassist/Projects/Sharpness/FISH_code/orig/lena.png"

org_img = Image.open(filename)

print(org_img.getbands())

org_img = org_img.convert('L')
print(org_img.getbands())

if org_img.getbands() == ('L',):
    print("just l")
else:
    print("nope")

if len(org_img.getbands()) == 1:
    print("just one")
else:
    print("nope...more")