import urllib # for downloading URLs
import urllib2 # for downloading URLs
#import pip # for downloading Pillow (image manipulator)
from pip import main
from platform import system # for checking OS
from os import path
from os import mkdir
from os import listdir
import re # for crawling for URLs
import random
import ctypes # for setting windows wallpaper

# import / install some stuff we need
try:
	from PIL import Image
except ImportError:
	main(['install', "Pillow"]) # for putting images together
	from PIL import Image
	
try:
	import requests # for http requests (unsplashed.com)
except ImportError:
	main(['install', "requests"])
	import requests
	
	
# # # config # # #
width = "1920"
height = "1080"
avoidcached = False
debug = True

# # directories # #
bindir = path.dirname(path.realpath(__file__)) + "\\"
#bindir = ".\\"
imagedir = bindir + "..\\images\\"
# make the directory
try:
	mkdir(imagedir)
except OSError: # directory exists
	pass
# # lists # # 
downloaded=[]


# fill downloaded list if image directory already exists
def makeImageDir(website):
	try:
		mkdir(imagedir + website)
	except OSError: # directory exists
		for image in listdir(imagedir):
			downloaded.append(image)

def debug(this):
	if debug:
		print this

def getImages(website):
	urls=[]	      # holds all of them
	usedurls=[]   # holds urls that have been downloaded
	unusedurls=[] # holds urls that haven't been downloaded yet
	goodurls=[]   # holds only the two to download
	imagepaths=[] # where the images sit after download
	
	makeImageDir(website)
	
	if website is "mikedrawsdota":
		websiteurl = 'http://mdd.hirshon.net/'
		# go to website and scrape urls, sort out the ones with resolution in filename
		for url in re.findall('''href=["'](.[^"']+)["']''', urllib.urlopen(websiteurl).read(), re.I):
			if width in url and height in url:
					urls.append(url)
					if url.split('/')[-1] not in downloaded: # if we havent seen it 
						unusedurls.append(url)				 # add to unused array
		
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
		
		# once we have the 2 urls, download them and return image paths
		for goodurl in goodurls:
			filename = goodurl.split('/')[-1] # Set filename to url's filename
			
			# download image to path
			path = imagedir + website + '\\' + filename
			download(goodurl, path)
			
			imagepaths.append(path) # add the image path to list
					
			
	if website is "unsplash":
		websiteurl = "https://api.unsplash.com/photos/random"
		
		# get authorized with dualwallpaper application id
		ID = 'cd356c3b262be554770bea925ce5119f0503605b31a6dc4f3e9365babfd1674c'		
		image_params = {'w':width, 'h':height, 'count':2, 'client_id':ID}
		
		# Request an array of 2 images' json data from api
		r = requests.get(websiteurl, params = image_params)
		
		creditfile = open(imagedir + "unsplash_image_info.txt", 'w')
		
		
		# For each image
		side = "Left"
		for response in r.json():
			url = response["urls"]["custom"].encode("ascii")
			filename = response["id"].encode("ascii")
			filename = filename + ".jpg"
			
			# download image from url to path
			path = imagedir + website + "\\" + filename 
			download(url, path)
		
			imagepaths.append(path)
			
			# get image info
			description = response["description"]
			fullimage = response["urls"]["full"].encode("ascii") + "?utm_source=dualwallpaper&utm_medium=referral&utm_campaign=api-credit"
			artist = response["user"]["name"]
			artisturl= response["user"]["username"]
			if artisturl:
				artisturl= "https://unsplash.com/@" + response["user"]["username"] + "?utm_source=dualwallpaper&utm_medium=referral&utm_campaign=api-credit"
			# write it to file image_info.txt
			write(creditfile, "%s monitor:" % side)
			write(creditfile, "	Description: %s" % description)
			write(creditfile, "	Artist: %s" % artist)
			write(creditfile, "	Artist Profile: %s\n" % artisturl)			
			write(creditfile, "	Full Image: %s\n" % fullimage)			
			# repeat once more for right monitor
			side = "Right"
		
		# credit to Unsplash.com
		write(creditfile, "Images from unsplash.com")
		creditfile.close()
		
	return imagepaths

def write(file, string):
	try:
		file.write("%s\n" % string)
		print string
	except TypeError:
		pass
	
# downloads image to path
def download(url, imagepath):
	if not path.isfile(imagepath): # only download if it doesn't exist already
		# Download image and return the path to it
		imagefile = open(imagepath, "wb")
		imagefile.write(urllib.urlopen(url).read())
		imagefile.close()
	else:
		print "file " + str(imagepath) + " already exists, using cached image"
	
def combine(imagepaths):
	wallpaperpath = imagedir + "current.jpg"
	debug("combining: \n" + imagepaths[0] + "\n" + imagepaths[1] + "\n into:\n" + wallpaperpath)
	
	left = Image.open(imagepaths[0])
	right = Image.open(imagepaths[1])
	
	wallpaper = Image.new('RGB', (int(width)*2, int(height)))
	
	wallpaper.paste(left,  (0,0))
	wallpaper.paste(right, (int(width),0))
	
	wallpaper.save(wallpaperpath)
	return wallpaperpath

	
def setWallpaper(image):
	debug("Setting wallpaper to: \n" + image + " on system=" + system())
	if (system() == 'Windows'):
		ctypes.windll.user32.SystemParametersInfoA(20, 0, image, 3)
    
	if (system() == 'Linux'): # untested
		command = "gconftool-2 --set \
		/desktop/gnome/background/picture_filename \
		--type string '%s'" % image
		status, output = commands.getstatusoutput(command)
	

def main(website):
	images = getImages(website)
	wallpaper = combine(images)
	setWallpaper(wallpaper)

#main("mikedrawsdota")
main("unsplash")
