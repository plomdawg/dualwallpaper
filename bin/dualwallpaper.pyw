import urllib 				# for downloading URLs
import urllib2 				# for downloading URLs
from pip import main 		# for downloading modules
from platform import system # for checking OS
from os import path
from os import mkdir		# for making a directory
from os import listdir		# for listing directories
import re					# for crawling for URLs
import random
import ctypes				# for setting windows wallpaper

# Install Pillow and requests using pip
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

# # # CONFIG # # #
width = "1920"
height = "1080"
monitors = 1
website = "mikedrawsdota"
#website = "unsplash"


# # DIRECTORIES # #
bindir = path.dirname(path.realpath(__file__)) + "\\"
imagedir = bindir + "..\\images\\"
downloaded=[]


# # FUNCTIONS # #

# fill downloaded list if image directory already exists
def makeImageDir(website):
	try: 				
		mkdir(imagedir) # make the folder
	except OSError: 	# folder exists
		pass			# do nothing
	try:
		mkdir(imagedir + website)
	except OSError: # directory exists
		for image in listdir(imagedir):
			downloaded.append(image)


# downloads num images from the website given
# returns paths to images as a list
def getImages(website, num):
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
		
		# until we find num good urls, keep looking
		count = 0		
		while count < num: 
			if len(unusedurls) > 0:
				i = random.randrange(0, len(unusedurls)) 	# generate random index
				goodurls.append(unusedurls.pop(i))	  		# pop the url out of the list
				count += 1
			else:
				i = random.randrange(0, len(urls)) # generate random index
				goodurls.append(urls.pop(i))	   # pop the url out of the list  urls and into goodurls
				count += 1
		
		# once we have the num urls, download them and return image paths
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
		image_params = {'w':width, 'h':height, 'count':num, 'client_id':ID}
		
		# Request an array of num images' json data from api
		r = requests.get(websiteurl, params = image_params)
		
		creditfile = open(imagedir + "unsplash_image_info.txt", 'w')
		
		
		# For each image
		position = 0
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
			write(creditfile, "%s position in image:" % position)
			write(creditfile, "	Description: %s" % description)
			write(creditfile, "	Artist: %s" % artist)
			write(creditfile, "	Artist Profile: %s\n" % artisturl)			
			write(creditfile, "	Full Image: %s\n" % fullimage)			
			# repeat once more for right monitor
			position += 1
		
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
	
# downloads image from given url to path
# does nothing if file is found
def download(url, imagepath):
	if path.isfile(imagepath):
		print "file " + str(imagepath) + " already exists, using cached image"
	else: # file not found, download it
		with open(imagepath, "wb") as f:
			f.write(urllib.urlopen(url).read())
	
# combines the images given as a list of directories
# num = # of images
def combine(imagepaths, num):
	outputfile = imagedir + "current.jpg"

	img = Image.new('RGB', (int(width)*num, int(height)))
	offset = 0
	for x in range(0, num):						# for 0 --> num
		with Image.open(imagepaths[x]) as currentimg: # open the current image
			img.paste(currentimg, (offset, 0))  # paste it to the final image
		offset += int(width)
	
	img.save(outputfile) # save it
	return outputfile	 # return it

# sets the given image as the wallpaper
def setWallpaper(image):
	print(str("Setting wallpaper to: \n" + image + " on system=" + system()))
	if (system() == 'Windows'):
		ctypes.windll.user32.SystemParametersInfoA(20, 0, image, 3)
    
	if (system() == 'Linux'): # untested
		command = "gconftool-2 --set \
		/desktop/gnome/background/picture_filename \
		--type string '%s'" % image
		status, output = commands.getstatusoutput(command)
	




# # WHERE STUFF HAPPENS # #

# get as many images as monitors from the website chosen
images = getImages(website, monitors) 

# combine the images into one
wallpaper = combine(images, monitors)

setWallpaper(wallpaper)
