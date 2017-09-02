import urllib # for downloading URLs
import urllib2 # for downloading URLs
import pip # for downloading Pillow (image manipulator)
from platform import system # for checking OS
import os 
import re # for crawling for URLs
import random
import ctypes # for setting wallpaper

# import / install some stuff we need
try:
	from PIL import Image
except ImportError:
	pip.main(['install', "Pillow"]) # for putting images together
	from PIL import Image
	
try:
	import requests # for http requests (unsplashed.com)
except ImportError:
	pip.main(['install', "requests"])
	import requests
	
# figure out operating system
OS = system() # using platform.system()
	
# # # config # # #
width = "1920"
height = "1080"
avoidcached = False
debug = False

# # directories # #
bindir = os.path.dirname(os.path.realpath(__file__)) + "\\"
imagedir = bindir + "..\\images\\"
# make the directory
try:
	os.mkdir(imagedir)
except OSError: # directory exists
	pass
# # lists # # 
downloaded=[]


# fill downloaded list if image directory already exists
def makeImageDir(website):
	try:
		os.mkdir(imagedir + website)
	except OSError: # directory exists
		for image in os.listdir(imagedir):
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
			path = imagedir + website + "\\" + filename
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
			
			# download image from url to path
			path = imagedir + website + "\\" + filename 
			download(url, path)
		
			imagepaths.append(path)
			
			# get image info
			description = response["description"]
			artist = response["user"]["name"]
			artisturl= response["user"]["portfolio_url"]
			if artisturl:
				artisturl= response["user"]["portfolio_url"] + "?utm_source=dualwallpaper&utm_medium=referral&utm_campaign=api-credit"
			# write it to file image_info.txt
			write(creditfile, "%s monitor:" % side)
			write(creditfile, "	Description: %s" % description)
			write(creditfile, "	Artist: %s" % artist)
			write(creditfile, "	Artist Portfolio: %s\n" % artisturl)			
			# repeat once more for right monitor
			side = "Right"
		
		# credit to Unsplash.com
		creditfile.write("Images from unsplash.com")
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
	if not os.path.isfile(imagepath): # only download if it doesn't exist already
		# Download image and return the path to it
		imagefile = open(imagepath, "wb")
		imagefile.write(urllib.urlopen(url).read())
		imagefile.close()
	else:
		print "file " + str(imagepath) + " already exists, using cached image"
	
def combine(imagepaths):
	wallpaperpath = imagedir + "current.jpg"
	
	left = Image.open(imagepaths[0])
	right = Image.open(imagepaths[1])
	
	wallpaper = Image.new('RGB', (int(width)*2, int(height)))
	
	wallpaper.paste(left,  (0,0))
	wallpaper.paste(right, (int(width),0))
	
	wallpaper.save(wallpaperpath)
	return wallpaperpath

	
def setWallpaper(image):
	if (OS == 'Windows'):
		ctypes.windll.user32.SystemParametersInfoA(20, 0, image, 3)
    
	if (OS == 'Linux'):
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
