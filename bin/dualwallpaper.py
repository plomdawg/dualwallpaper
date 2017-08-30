import urllib # for downloading URLs
import urllib2 # for downloading URLs
import pip # for downloading Pillow (image manipulator)
import os 
import re # for crawling for URLs
import random
import ctypes # for setting wallpaper
 # for downloading from unsplash

# directories
bindir = os.path.dirname(os.path.realpath(__file__)) + "\\"
imagedir = bindir + "..\\images\\"

# lists
downloaded=[]

# config
width = "1920"
height = "1080"
avoidcached = False
debug = True

try:
	from PIL import Image
except ImportError:
	pip.main(['install', "Pillow"])
	from PIL import Image
	
try:
	import requests
except ImportError:
	pip.main(['install', "requests"])
	import requests


# fill downloaded list if image directory already exists
try:
	os.mkdir(imagedir)
except OSError: # directory exists
	for image in os.listdir(imagedir):
		downloaded.append(image)

def debug(this):
	if debug:
		print this

def getImages(website):
	urls=[]	   # holds all of them
	usedurls=[]   # holds urls that have been downloaded
	unusedurls=[] # holds urls that haven't been downloaded yet
	goodurls=[]   # holds only the two to download
	imagepaths=[] # where the images sit after download

	# create folder to store images from site
	try:
		os.mkdir(imagedir + website)
	except OSError:
		pass
	
	if website is "mikedrawsdota":
		website = 'http://mdd.hirshon.net/'
		# go to website and scrape urls, sort out the ones with resolution in filename
		for url in re.findall('''href=["'](.[^"']+)["']''', urllib.urlopen(website).read(), re.I):
			if width in url and height in url:
					urls.append(url)
					debug("all urls")
					debug(url)
					if url.split('/')[-1] not in downloaded: # add to unused array if we havent seen it before
						debug("unused")
						debug(url)
						unusedurls.append(url)
		
		# debug info to figure out wtf is happening
		
		debug("plenty of unusedurls:")
		debug(unusedurls)
		
		debug("all the urls:")
		debug(urls)
		
		# until we find 2 good urls, keep looking
		count = 0		
		while count < 2: 
			if avoidcached and len(unusedurls) > 0:
				i = random.randrange(0, len(unusedurls)) # generate random index
				goodurls.append(unusedurls.pop(i))	  # pop the url out of the list
				count += 1
			else:
				i = random.randrange(0, len(urls)) # generate random index
				goodurls.append(urls.pop(i))	  # pop the url out of the list  urls and into goodurls
				count += 1
		
		debug(goodurls)
		
		
		# once we have the 2 urls, download them and return image paths
		for goodurl in goodurls:
			filename = goodurl.split('/')[-1] # Set filename to url's filename
			debug("filename: " + filename)
			imagepath = imagedir + "mikedrawsdota\\" + filename # Set image path based on filename
			
			if not os.path.isfile(imagepath): # only download if it doesn't exist already
				# Download image and return the path to it
				imagefile = open(imagepath, "wb")
				imagefile.write(urllib.urlopen(goodurl).read())
				imagefile.close()
			else:
				print "file " + str(imagepath) + " already exists, using cached image"
			
			imagepaths.append(imagepath) # add the image path to list
					
			
	if website is "unsplash":
		website = "https://api.unsplash.com/photos/random/"
		# need to send this request:
		# GET /photos/random/w: width h: height 
		prams = {'w':width, 'h':height, 'count':2}
		
		r = requests.get(url = website, params = prams)
		
		data = r.json
		print data
		
		print urllib2.urlopen(website).read()
		print website + params
		print urllib2.urlopen(website + params).read()
		
		
	return imagepaths

	
def combine(imagepaths):
	wallpaperpath = imagedir + "current.jpg"
	
	debug("imgagepaths")
	debug(imagepaths)
	
	left = Image.open(imagepaths[0])
	right = Image.open(imagepaths[1])
	
	wallpaper = Image.new('RGB', (int(width)*2, int(height)))
	
	wallpaper.paste(left,  (0,0))
	wallpaper.paste(right, (int(width),0))
	
	wallpaper.save(wallpaperpath)
	return wallpaperpath

	
def setWallpaper(image):
	ctypes.windll.user32.SystemParametersInfoA(20, 0, image, 3)
	

def main(url):
	images = getImages(url)
	wallpaper = combine(images)
	setWallpaper(wallpaper)

#main("mikedrawsdota")
main("unsplash")
