import re
import sys
import ntpath
import urllib
import urllib2

import ConfigParser

import os.path
import unicodedata
from Debug import * 

try:
    from PIL import Image
except ImportError:
    dprint(__name__, 0, "No PIL/Pillow installation found.")

class ImageBackground():
    options = {'title': "empty", 'image' : 'blank.jpg', 'resolution' : '1080'}
    
    cfg = {}
    
    def __init__(self,opts):
        for opt in self.options:
            self.cfg[opt] = self.options[opt]
        if opts != None:
         for opt in opts:
            if self.cfg[opt] != opts[opt]:
                self.cfg[opt] = opts[opt]

    def setOptions(self,opts):
        for opt in opts:
            if self.cfg[opt] != opts[opt]:
                self.cfg[opt] = opts[opt]
                
    def getRendersize(self, res):
        renderwidth = 1280
        renderheight = 720
        return renderwidth, renderheight

    def createFileHandle(self):
        cachefileTitle = normalizeString(self.cfg['title'])
        cachefileRes = normalizeString(self.cfg['resolution'])
        
        sourcefile = remove_junk(str(self.cfg['image']))
        sourcefile = remove_junk(str(sourcefile))
   
        cachefile = cachefileTitle + "_" + cachefileRes
        
        return cachefile

    def resizedMerge (self,background, stylepath):
        isatv2=0

        renderwidth, renderheight = self.getRendersize(self.cfg['resolution'])
        if str(renderheight) == "720":
            height = int(self.cfg['resolution'])
            if height == 720:
                isatv2 = 1
                width = 1920
                height = 1080
            elif height == 1080:
                width = 1920
        else:
            width = renderwidth
            height = renderheight
            
        im = Image.new("RGB", (width, height), "black")
        background = background.resize((width, height), Image.ANTIALIAS)
    
      
        im.paste(background, (0, 0), 0)
        layer = Image.open(stylepath + "/images/MoviePrePlay.png")
        layer = layer.resize((width, height), Image.ANTIALIAS)
        im.paste(layer, ( 0, 0), layer)
        
        if isatv2>0:
            im = im.resize((1280, 720), Image.ANTIALIAS)
        return im

    def generate(self):
    
    # Catch the Params
        cachepath = sys.path[0]+"/assets/fanartcache"
        stylepath = sys.path[0]+"/assets/templates"
        cachefile = self.createFileHandle()
        
        dprint(__name__, 1, 'Check for Cachefile.')  # Debug
        # Already created?
        if os.path.isfile(cachepath+"/"+cachefile+".jpg"):
            dprint(__name__, 1, 'Cachefile  found.')  # Debug
            return cachefile+".jpg" # Bye Bye
        # No it's not
        else:
            dprint(__name__, 1, 'No Cachefile found. Generating Background.')  # Debug
            # Setup Background
            url = urllib.unquote(self.cfg['image'])
            if os.path.isfile(stylepath+"/images/"+url):
                dprint(__name__, 1, 'Fetching Template Image.'  )  # Debug
                background = Image.open(stylepath+"/images/"+url)
            elif url[0][0] != "/":
                try:
                    bgfile = urllib2.urlopen(url)
                except urllib2.URLError, e:
                    dprint(__name__, 1, 'error: {0}', str(e.code)+" "+e.msg+" // url:"+ url )  # Debug
                    background = Image.open(stylepath+"/images/blank.jpg")
                else:
                    dprint(__name__, 1, 'Getting Remote Image.')  # Debug
                    output = open(cachepath+"/tmp.jpg",'wb')
                    output.write(bgfile.read())
                    output.close()
                    background = Image.open(cachepath+"/tmp.jpg")
                
            # Set Resolution and Merge Layers
            dprint(__name__, 1, 'Merging Layers.')  # Debug
            im = self.resizedMerge(background, stylepath)

            # Save to Cache
            im.save(cachepath+"/"+cachefile+".jpg")  
            dprint(__name__, 1, 'Cachefile  generated.')  # Debug
            return cachefile+".jpg"

# HELPERS

def isPILinstalled():
    try:
        from PIL import Image
    except ImportError:
        return False
    return True
    
def normalizeString(text):
    text = urllib.unquote(str(text)).replace(' ','+')
    text = unicodedata.normalize('NFKD',unicode(text,"utf8")).encode("ascii","ignore")  # Only ASCII CHARS
    text = re.sub(r'\W+', '+', text) # No Special Chars  
    return text
    
def remove_junk(url):
    temp = urllib.unquote(str(url))
    temp = temp.split('/')[-1]
    temp = temp.split('?')[0]
    temp = temp.split('&')[0]
    return temp