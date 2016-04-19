from ij import IJ
from ij.plugin.filter import RankFilters

#import sys
#print sys.version

class Log(object):
    DEBUG, INFO, WARN, ERROR = 1, 2, 3, 4
    debug = info = None
    def __init__(self, level=None):
        if level == None:
            level = Log.INFO
        d = {False: lambda *arg: None, True: self._print}
        self.debug = d[level <= Log.DEBUG]
        self.info = d[level <= Log.INFO]
        self.warn = d[level <= Log.WARN]
        self.error = d[level <= Log.ERROR]
    def _print(self, *arg, **kw):
        print ' '.join(['%s' % i for i in arg])

log = Log(level=Log.DEBUG)
log.debug('\n--- debug start ---')

# Creat a new image
#imp = ImagePlus("my new image", FloatProcessor(512, 512))

# Grab the active image
imp = IJ.getImage()
#IJ.run("Skeletonize (2D/3D)")

# Process Pixel
pix = imp.getProcessor().getPixels()

n_pix = len(pix)
w = imp.getWidth()
h = imp.getHeight()

log.debug ('image size:', w, h, w*h, n_pix)
log.debug('pix min max:', min(pix), max(pix))

imp.show()