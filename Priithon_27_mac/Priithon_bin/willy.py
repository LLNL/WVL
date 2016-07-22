# This file was automatically generated by SWIG (http://www.swig.org).
# Version 2.0.4
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.



from sys import version_info
if version_info >= (2,6,0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_willy', [dirname(__file__)])
        except ImportError:
            import _willy
            return _willy
        if fp is not None:
            try:
                _mod = imp.load_module('_willy', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _willy = swig_import_helper()
    del swig_import_helper
else:
    import _willy
del version_info
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0



def medianer(*args):
  """medianer(float array3d, float threshold)"""
  return _willy.medianer(*args)

def wave3dChp(*args):
  """wave3dChp(float arg0, float array3d, int ordx, int ordy, int ordz)"""
  return _willy.wave3dChp(*args)

def willyStdDevMeasure(*args):
  """willyStdDevMeasure(float array3d) -> double"""
  return _willy.willyStdDevMeasure(*args)

def writeWavletVTK(*args):
  """
    writeWavletVTK(float array3d, int ordx, int ordy, int ordz, float dx, 
        float dy, float dz, char unit, char fn)
    """
  return _willy.writeWavletVTK(*args)
# This file is compatible with both classic and new-style classes.


def binarize(*args):
  """
    binarize(unsigned char array3d, unsigned char threshold)
    binarize(short array3d, short threshold)
    binarize(float array3d, float threshold)
    binarize(unsigned short array3d, unsigned short threshold)
    binarize(long array3d, long threshold)
    """
  return _willy.binarize(*args)

def grow(*args):
  """
    grow(unsigned char arg0, unsigned char array3d, unsigned char skirt = 1)
    grow(unsigned char arg0, unsigned char array3d)
    grow(short arg0, short array3d, short skirt = 1)
    grow(short arg0, short array3d)
    grow(float arg0, float array3d, float skirt = 1)
    grow(float arg0, float array3d)
    grow(unsigned short arg0, unsigned short array3d, unsigned short skirt = 1)
    grow(unsigned short arg0, unsigned short array3d)
    grow(long arg0, long array3d, long skirt = 1)
    grow(long arg0, long array3d)
    """
  return _willy.grow(*args)

def writeVol(*args):
  """
    writeVol(char outfn, unsigned char array3d)
    writeVol(char outfn, short array3d)
    writeVol(char outfn, float array3d)
    writeVol(char outfn, unsigned short array3d)
    writeVol(char outfn, long array3d)
    """
  return _willy.writeVol(*args)

def readPointsToVol(*args):
  """
    readPointsToVol(char fn, unsigned char array3d, double xmin, double xside, 
        double ymin, double yside, double zmin, 
        double zside)
    readPointsToVol(char fn, short array3d, double xmin, double xside, 
        double ymin, double yside, double zmin, double zside)
    readPointsToVol(char fn, float array3d, double xmin, double xside, 
        double ymin, double yside, double zmin, double zside)
    readPointsToVol(char fn, unsigned short array3d, double xmin, double xside, 
        double ymin, double yside, double zmin, 
        double zside)
    readPointsToVol(char fn, long array3d, double xmin, double xside, double ymin, 
        double yside, double zmin, double zside)
    """
  return _willy.readPointsToVol(*args)

def fastwv6(*args):
  """
    fastwv6(float arg0, float array3d, int ordx, int ordy, int ordz, 
        bool prints = 0)
    fastwv6(float arg0, float array3d, int ordx, int ordy, int ordz)
    """
  return _willy.fastwv6(*args)

def discriminator(*args):
  """
    discriminator(float arg0, float arg1, short array3d, int order, float thrsh, 
        float offset, bool zdis, double deltax = 1, 
        double deltay = 1, double deltaz = 1)
    discriminator(float arg0, float arg1, short array3d, int order, float thrsh, 
        float offset, bool zdis, double deltax = 1, 
        double deltay = 1)
    discriminator(float arg0, float arg1, short array3d, int order, float thrsh, 
        float offset, bool zdis, double deltax = 1)
    discriminator(float arg0, float arg1, short array3d, int order, float thrsh, 
        float offset, bool zdis)
    """
  return _willy.discriminator(*args)
