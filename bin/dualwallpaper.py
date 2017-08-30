import urllib # for downloading URLs
import pip # for downloading Pillow (image manipulator)
import os 
import re # for crawling for URLs
import random
import ctypes # for setting wallpaper

# directories
bindir = os.path.dirname(os.path.realpath(__file__)) + "\\"
imagedir = bindir + "..\\images\\"

# lists
downloaded=[]

# config
width = "1920"
height = "1080"
avoidcached = True

try:
    from PIL import Image
except ImportError:
    pip.main(['install', "Pillow"])
    from PIL import Image


# fill downloaded list if image directory already exists
try:
    os.mkdir(imagedir)
except OSError: # directory exists
    for image in os.listdir(imagedir):
        downloaded.append(image)


def fetchURLs(website):
    urls=[]       # holds all of them
    goodurls=[]   # holds only the two to return
    usedurls=[]   # holds urls that have been downloaded
    unusedurls=[] # holds urls that haven't been downloaded yet

    # go to website and scrape urls, sort out the ones with resolution in filename
    for url in re.findall('''href=["'](.[^"']+)["']''', urllib.urlopen(website).read(), re.I):
        if width in url and height in url:
            urls.append(url)

    # figure out which ones we haven't used yet
    for url in urls:
        if url.split('/')[-1] not in downloaded:
            unusedurls.append(url)

    # until we find 2 good urls, keep looking
    while len(goodurls) < 2: 
        if avoidcached and len(unusedurls) > 0:
            i = random.randrange(0, len(unusedurls)) # generate random index
            goodurls.append(unusedurls.pop(i))      # pop the url out of the list
        else:
            i = random.randrange(0, len(urls)) # generate random index
            goodurls.append(urls.pop(i))      # pop the url out of the list  

    return goodurls

def getImages(urls):
    # go to both urls and download them
    imagepaths = []
    for url in urls:
        imagepaths.append(download(url))
    # return the files
    return imagepaths

def combine(images):
    wallpaperpath = imagedir + "current.jpg"

    left  = Image.open(images[0])
    right = Image.open(images[1])

    wallpaper = Image.new('RGB', (int(width)*2, int(height)))

    wallpaper.paste(left,  (0,0))
    wallpaper.paste(right, (int(width),0))

    wallpaper.save(wallpaperpath)
    return wallpaperpath

def setWallpaper(image):
    ctypes.windll.user32.SystemParametersInfoA(20, 0, image, 3)

def download(url):
    # Set filename to url's filename
    filename=url.split('/')[-1]

    # Set image path based on filename
    imagepath=imagedir + filename

    if not os.path.isfile(imagepath): # only download if it doesn't exist already
        # Download image and return the path to it
        imagefile = open(imagepath, "wb")
        imagefile.write(urllib.urlopen(url).read())
        imagefile.close()
    else:
        print "file " + str(imagepath) + " already exists"

    # Return image path
    return imagepath

def main(url):
    print "Fetching URLs from " + url
    urls = fetchURLs(url)
    print "Downloading images from"
    for www in urls:
        print "   " + www
    images = getImages(urls)
    print "Combining images"
    wallpaperpath = combine(images)
    print "Setting wallpaper"
    setWallpaper(wallpaperpath)

main('http://mdd.hirshon.net/')
