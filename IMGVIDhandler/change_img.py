from PIL import Image
import os

imglink = r"C:\Users\CARBON\Desktop\IMG-20180329-WA0000.jpg"
imglink2 = r"C:\Users\CARBON\Desktop\IMG-20180329-WA0000.jpg"
quality_val = 100

def compress_img(img, story=None):
    if story:
        size = 1080, 1920
    else:
        size = 1080, 1080
    im1 = Image.open(img)
    im1 = im1.resize(size, Image.ANTIALIAS)
    link = os.path.join(r"C:\Users\CARBON\Desktop\ping2.jpg")
    width, height = im1.size
    #im1 = im1.resize(size, Image.ANTIALIAS)
    im1.save(link,"JPEG", quality=quality_val)

    #im1.save(link, "JPEG", quality=10, optimize=True)
    return link, str(os.path.getsize(link)), width, height

