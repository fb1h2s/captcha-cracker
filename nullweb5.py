from PIL import Image,ImageChops
from operator import itemgetter
import urllib2,hashlib,time,urllib
import cStringIO,glob
#we have kept all our letters in this folder 
files_names =  glob.glob("/root/ctf/let/*.*")
#we need to get the captcha at the same time get the session cookie, and use it for all solved captcha request.
response = urllib2.urlopen('http://54.165.191.231/imagedemo.php')
cookie = response.headers['Set-Cookie']
#print cookie

#lets make 500 request read teach captcha 
for x in range(1,500):
  
  captcha =""
  opener = urllib2.build_opener()
  opener.addheaders =[
                    ('Accept', 'application/json, text/javascript, */*; q=0.01'),
                    ('Referer', 'http://www.garag4hackers.com'),
                    ('Cookie' ,cookie),]
                  
  response = opener.open('http://54.165.191.231/imagedemo.php')
  length = response.headers['content-length']
  # read the captch and we will save them with there content length */
  print "[-] Image Content length " , length
  image_read = response.read()
  #cStringIO to create an object from memmory
  #image_read = Image.open("/root/ctf/u.png")
  image_read = cStringIO.StringIO(image_read)
  captcha_image = Image.open(image_read)
  #im = Image.open("/root/ctf/de")
  captcha_image = captcha_image.convert("P")
  temp = {}
  captcha_filtered = Image.new("P",captcha_image.size,255)

  #print im.histogram()
  his = captcha_image.histogram()
  values = {}

  for i in range(256):
    values[i] = his[i]
    
  print "[-] Image pixel concentration \n"  
  for color,concentrate in sorted(values.items(), key=itemgetter(1), reverse=True)[:10]:
    print color,concentrate
    
  for x in range(captcha_image.size[1]):
    for y in range(captcha_image.size[0]):
      pix = captcha_image.getpixel((y,x))
      temp[pix] = pix
      if pix == 204 or pix == 205: # these are the numbers to get
	captcha_filtered.putpixel((y,x),0)

  captcha_filtered.save("/root/ctf/images/"+length+".gif")
  inletter = False
  foundletter=False
  start = 0
  end = 0

  letters = []

  for y in range(captcha_filtered.size[0]): # slice across
    for x in range(captcha_filtered.size[1]): # slice down
      pix = captcha_filtered.getpixel((y,x))
      if pix != 255:
	inletter = True
    if foundletter == False and inletter == True:
      foundletter = True
      start = y

    if foundletter == True and inletter == False:
      foundletter = False
      end = y
      letters.append((start,end))

    inletter=False
  
  print "[-] Horizontal Position Where letter start and stop \n"  
  print letters
  print "\n"

  count = 0
  for letter in letters:
    m = hashlib.md5()
    im3 = captcha_filtered.crop(( letter[0] , 0, letter[1],captcha_filtered.size[1] ))
    #Match current letter with sample data
    #im3.save("/root/ctf/let/%s.gif"%(m.hexdigest()),quality=95)
    count += 1
    base = im3.convert('L')
    
    #print files_names

    class Fit:
        letter = None
        difference = 0 

    best = Fit()

    for letter in files_names:
        #print letter
        current = Fit()
        current.letter = letter

        sample_path = letter
        #print sample_path
        sample = Image.open(sample_path).convert('L').resize(base.size)
        difference = ImageChops.difference(base, sample)
        
        for x in range(difference.size[0]):
            for y in range(difference.size[1]):
                current.difference += difference.getpixel((x, y))

        if not best.letter or best.difference > current.difference:
            best = current
    
    #final captcha decoded
    tmp = best.letter[14:15]
    captcha = captcha+tmp
  
  #let us post the captcha to the server along with the session token
  print "[+] Captcha is ", captcha
  url = 'http://54.165.191.231/verify.php'
  data = urllib.urlencode({'solution' : captcha.strip(), 'Submit' : 'Submit'})
  req = opener.open(url, data)
  response = req.read()
  print response

  
