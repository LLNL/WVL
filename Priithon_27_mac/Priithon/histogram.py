"""provides the histogram scaling OpenGL-based panel for Priithon's ND 2d-section-viewer"""
from __future__ import absolute_import

__author__  = "Sebastian Haase <seb.haase+Priithon@gmail.com>"
__license__ = "BSD license - see LICENSE file"

#20051107 from wxPython   import wx
import wx

from wx import glcanvas
from OpenGL.GL import *
from .viewerCommon import myGL_PixelTransfer
# from OpenGL import GLU   ## CHECK langur has not GLUT - debian glutg3
#seb     from OpenGL.GLUT import *
import Priithon_bin.glSeb as glSeb


## import Numeric as Num
#from numarray import numeric as Num
#import numarray as na
import numpy as N
import traceback
from . import PriConfig

###########################################from numarray import numeric as na
#----------------------------------------------------------------------

#  #timings
#  # Numeric
#  ms: 0.00
#  setHist00  ms: 0.00
#  setHist01  ms: 110.00
#  setHist1  ms: 380.00
#  setHist2  ms: 380.00
#  setHist3 ms: 380.00
#  setHist3b ms: 380.00
#  setHist4 ms: 380.00
#  setHist5 ms: 510.00

#  #numarray
#  setHist00  ms: 0.00
#  newshape: (65536, 2)
#  setHist01  ms: 0.00
#  setHist1  ms: 10.00
#  setHist2  ms: 20.00
#  setHist3 ms: 20.00
#  setHist3b ms: 20.00
#  setHist4 ms: 16630.00
#  setHist5 ms: 16630.00
#  ms: 10.00
#  setHist00  ms: 0.00
#  setHist01  ms: 0.00
#  setHist1  ms: 0.00
#  setHist2  ms: 0.00
#  setHist3 ms: 0.00
#  setHist3b ms: 0.00
#  setHist4 ms: 16790.00
#  setHist5 ms: 16800.00


#before going to numpy: (laptop windows)
# >>> Y.view(a)
# setHist00     ms: 0.01
# newshape: (10000, 2)
# setHist01     ms: 1.25
# setHist1 ms: 6.39
# setHist2 ms: 7.11
# setHist3 ms: 7.51
# setHist3b ms: 8.25
# setHist4 ms: 8.63
# setHist5 ms: 9.09
# >>> 
#with numpy:
# >>> Y.view(a)
# setHist00     ms: 0.01
# newshape: (10000, 2)
# setHist01     ms: 2.29
# setHist1 ms: 3.15
# setHist2 ms: 4.22
# setHist3 ms: 4.80
# setHist3b ms: 6.40
# setHist4 ms: 7.00
# setHist5 ms: 8.09

### without sebgl. module
# >>> Y.view(a)
# setHist00     ms: 0.01
# newshape: (10000, 2)
# setHist01     ms: 2.93
# setHist1 ms: 4.24
# setHist2 ms: 5.31
# setHist3 ms: 6.34
# setHist3b ms: 7.91
# setHist4 ms: 80.02
# setHist5 ms: 81.40


Menu_Reset = wx.NewId()
Menu_ZoomToBraces   = wx.NewId()
Menu_AutoFit   = wx.NewId()
Menu_Log   =  wx.NewId()
Menu_FitYToSeen   =  wx.NewId()
Menu_EnterScale   =  wx.NewId()
#20051117 Menu_Gamma   = 1004


HistLogModeZeroOffset = .0001

class MyCanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent, size=wx.DefaultSize):
        glcanvas.GLCanvas.__init__(self, parent, -1, size=size, style=wx.WANTS_CHARS)
        # wxWANTS_CHARS to get arrow keys on Windows

        try:
            self.context = glcanvas.GLContext(self)
        except TypeError: # wx < 2.9.1
            # isRGB__unused= 0
            # glcanvas.GLContext(isRGB__unused, self)
            self.context = self .GetContext() 

        self.init = False
        self.m_w, self.m_h = 0,0
        
        self.zoomChanged = 1
        self.m_doViewportChange = 1
        self.m_sx, self.m_sy = 1,1
        self.m_tx, self.m_ty = 0,0
        
        # initial mouse position
        #seb self.lastx = self.x = 30
        #seb self.lasty = self.y = 30
        wx.EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_PAINT(self, self.OnPaint)
        #          EVT_LEFT_DOWN(self, self.OnMouseDown)  # needs fixing...
        #          EVT_LEFT_UP(self, self.OnMouseUp)
        #          EVT_MOTION(self, self.OnMouseMotion)
        
        # xPlotArrayCache
        #20080701 self.ca_xMin = 0
        #20080701 self.ca_xMax = 0
        #20080701 self.ca_n = 0
        if wx.VERSION >= (2,9):  # API change with wx 2.9 --
            # http://wxpython-users.1045709.n5.nabble.com/GLCanvas-and-GLContext-td2651535.html
            self.set_current = lambda : self.SetCurrent(self.context)
        else:
            self.set_current = self.SetCurrent
        

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnSize(self, event):
        self.m_w, self.m_h = self.GetClientSizeTuple()
        if self.m_w <=0 or self.m_h <=0:
            #print "debug: HistogramCanvas.OnSize: self.m_w <=0 or self.m_h <=0", self.m_w, self.m_h
            return
        # do not change viewport if size negative
        self.m_doViewportChange = 1
        event.Skip()
        
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        if self.m_w <=0 or self.m_h <=0:
            #THIS IS AFTER wx.PaintDC -- OTHERWISE 100% CPU usage
            return 
        self.set_current() # 2012 self.SetCurrent(self.context) # 20111103
        if not self.init:
            self.InitGL()
            self.init = 1

        if self.m_doViewportChange:
            #print "debug: m_doViewportChange", self.m_w, self.m_h
            glViewport(0, 0, self.m_w, self.m_h)
            glMatrixMode (GL_PROJECTION)
            glLoadIdentity ()
            glOrtho (-.375, self.m_w-.375, -.375, self.m_h-.375, 1., -1.)
            glMatrixMode (GL_MODELVIEW)
            self.m_doViewportChange = False
            ####glOrtho(  0, self.m_w, 0, self.m_h, -1,1);


        if self.zoomChanged:
            #print "debug: zoomChanged", self.m_sx,self.m_sy
            glMatrixMode (GL_MODELVIEW);
            glLoadIdentity ();     
            glTranslated(self.m_tx,self.m_ty,0);
            glScaled(self.m_sx,self.m_sy,1.);          
            self.zoomChanged = 0

        self.OnDraw()

#      def OnMouseDown(self, evt):
#          self.CaptureMouse()

#      def OnMouseUp(self, evt):
#          self.ReleaseMouse()

#      def OnMouseMotion(self, evt):
#          if evt.Dragging() and evt.LeftIsDown():
#              self.x, self.y = self.lastx, self.lasty
#              self.x, self.y = evt.GetPosition()
#              self.Refresh(False)




class HistogramCanvas(MyCanvasBase):
    def __init__(self, parent, size=wx.DefaultSize):
        MyCanvasBase.__init__(self, parent, size=size)

        
        self.m_log = True # 20070724 - default log-scale
        self.fitYtoSeen = True # 20080731

        self.mouse_last_x, self.mouse_last_y = 0,0 # in case mouseIsDown happens without preceeding mouseDown
        self.dragCenter = False # in case mouseIsDown happens without preceeding mouseDown
        self.dragLeft   = True # in case mouseIsDown happens without preceeding mouseDown
        self.keepZoomedToBraces = True # 20080806

        wx.EVT_MOUSE_EVENTS(self, self.OnMouse)
        wx.EVT_MOUSEWHEEL(self, self.OnWheel)
        #wx.EVT_CLOSE(self, self.OnClose)
        self.MakePopupMenu()
        self.m_histPlotArray = None
        self.leftBrace = 0.
        self.rightBrace= 100.
        self.bandTobeGenerated = True
        self.m_imgChanged = True
        self.m_histScaleChanged = True
        self.colMap = None
        self.m_texture_list = None
        self.m_histGlRGB=(1.0, 1.0, 1.0)

        #20080707 doOnXXXX event handler are now lists of functions
        self.doOnBrace = [] # (self) # use self.leftBrace, self.rightBrace to get current brace positions
        self.doOnMouse = [] # (xEff, ev)
        

        if wx.version()=='2.9.3.1 msw (classic)':
            def ReleaseMouse_SebMSW293bugfix():
                try:
                    super(HistogramCanvas, self).ReleaseMouse()
                except wx.PyAssertionError: 
                    pass
            self.ReleaseMouse = ReleaseMouse_SebMSW293bugfix


    def OnSize(self, event):
        MyCanvasBase.OnSize(self, event)
        self.fitY() # CHECK - efficiency could cache hm=na.maximum.reduce( self.m_histPlotArray[:,1])
        if self.keepZoomedToBraces:
            self.zoomToBraces()



    def InitGL(self):
        (self.m_w, self.m_h) = self.GetClientSizeTuple()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(  0, self.m_w, 0, self.m_h, -1,1)
        glMatrixMode(GL_MODELVIEW);

        glEnableClientState(GL_VERTEX_ARRAY)
        
        glClearColor(1.0, 1.0, 1.0, 0.0)

        glEnable(GL_TEXTURE_1D)


    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);


        #print "debug:", "ondraw", self.bandTobeGenerated, self.m_histScaleChanged,self.m_imgChanged

        if self.bandTobeGenerated:
            self.tex_nx = 256
            self.tex_ny = 1
            # self.m_gllist = glGenLists( 1 )
            if self.m_texture_list:
                glDeleteTextures(self.m_texture_list)#glDeleteTextures  silently  ignores  zeros
                
            self.m_texture_list = glGenTextures(1)

            glBindTexture(GL_TEXTURE_1D, self.m_texture_list)
            
            glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
            #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
            glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
            #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
            #    // GL_CLAMP causes texture coordinates to be clamped to the range [0,1] and is
            #    // useful for preventing wrapping artifacts when mapping a single image onto
            #    // an object.
            #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP)
            #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP)
            glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_S,GL_REPEAT)
            
            glTexImage1D(GL_TEXTURE_1D,0,  GL_RGB, self.tex_nx, 0, 
                            GL_LUMINANCE,GL_UNSIGNED_BYTE, None)
        
            self.bandTobeGenerated = False

        if self.m_histScaleChanged:
            if self.colMap is not None:
                myGL_PixelTransfer(self.colMap)
            else:
                glPixelTransferi(GL_MAP_COLOR, False);

            self.m_histScaleChanged = False

        HEIGHT = self.m_h/ float(self.m_sy)
        try:

            if self.m_imgChanged:
                self.m_imgArr = N.arange(self.tex_nx).astype(N.uint8)
                #self.m_imgArr[:] = 128
                glBindTexture(GL_TEXTURE_1D, self.m_texture_list)
      
                if self.m_imgArr.dtype.type == N.uint8:
                    glTexSubImage1D(GL_TEXTURE_1D,0,  0, self.tex_nx, 
                                       GL_LUMINANCE,GL_UNSIGNED_BYTE, self.m_imgArr.tostring())

                self.m_imgChanged = False

            glColor3fv(self.m_histGlRGB);
            #20051205 glColor3f(1.0, 1.0, 1.0);
            glBindTexture(GL_TEXTURE_1D, self.m_texture_list)
            glBegin(GL_QUADS)
            glTexCoord2f( 0, 0);          glVertex2f  ( self.leftBrace, HEIGHT*.1)
            glTexCoord2f( 0, 1);          glVertex2f  ( self.leftBrace, HEIGHT*.9)
            glTexCoord2f( 1, 1);          glVertex2f  ( self.rightBrace, HEIGHT*.9)
            glTexCoord2f( 1, 0);          glVertex2f  ( self.rightBrace, HEIGHT*.1)
            glEnd()
        except:
            print 'DEBUG: histogram.py: oops - set self.bandTobeGenerated'
            print 'DEBUG: self.m_texture_list', self.m_texture_list
            self.bandTobeGenerated  = True

        glDisable(GL_TEXTURE_1D);

        glColor3f(0.0, 0.0, 1.0);
        if self.m_histPlotArray is not None:
            glDrawArrays(GL_LINE_STRIP, 0, self.m_histPlotArray.shape[0])
            #crashed here if my glSeb extension is compiler on a NVIDIA based OpenGL debian
            #haase@colobus:~: file  /usr/lib/libso
            #/usr/lib/libso: broken symbolic link to `libso.1.2'

            #glSeb.glDrawArrays(GL_LINE_STRIP, 0, self.m_histPlotArray.shape[0])

        braceW = 15        / float(self.m_sx)
        braceY1 = HEIGHT*.95
        #braceY0 = self.m_h*.05 /self.m_sy
        braceY0 = 0
        glColor3f(1.0, 0.0, 0.0);
        
        #print self.leftBrace, self.m_h, self.m_sx
        x = self.leftBrace
        glBegin(GL_LINE_STRIP);
        glVertex2d(x+braceW, braceY0);
        glVertex2d(x,        braceY0);
        glVertex2d(x,        braceY1);
        glVertex2d(x+braceW, braceY1);
        glEnd();
        
        x = self.rightBrace
        glBegin(GL_LINE_STRIP);
        glVertex2d(x-braceW, braceY0);
        glVertex2d(x,        braceY0);
        glVertex2d(x,        braceY1);
        glVertex2d(x-braceW, braceY1);
        glEnd();
        
        glEnable( GL_TEXTURE_1D);
        
        self.SwapBuffers()


    def OnWheel(self, evt):
        # print "DEBUG: OnWheel"
        #delta = evt.GetWheelDelta()
        rot = evt.GetWheelRotation()      / 120. #HACK
        #linesPer = evt.GetLinesPerAction()
        #print "wheel:", delta, rot, linesPer
        zoomSpeed = 1. # .25
        
        #sfac = 1.05 ** (rot*zoomSpeed)
        sfac = 1.5 ** (rot*zoomSpeed)
        self.m_tx *= sfac
        x = evt.GetX()
        self.m_tx += x* (1.-sfac)
        self.m_sx *= sfac

        #20080731 self.zoomChanged = 1
        #20080731 #self.mouse_last_x, self.mouse_last_y = x,y
        #20080731 self.Refresh(0)
        self.fitY() #20080731 

    def OnMouse(self, ev):
        x,y = ev.GetX(), self.m_h-ev.GetY()
        xEff = (x - self.m_tx) / float(self.m_sx)
        
        #  global evt
        #          evt = ev
        #          print dir(ev)
        
        midButt = ev.MiddleDown() or (ev.LeftDown() and ev.AltDown())
        midIsButt = ev.MiddleIsDown() or (ev.LeftIsDown() and ev.AltDown())
        rightButt = ev.RightDown() or (ev.LeftDown() and ev.ControlDown())

        # TODO CHECK 
        # Any application which captures the mouse in the beginning of some
        # operation must handle wxMouseCaptureLostEvent and cancel this
        # operation when it receives the event.
        # The event handler must not recapture mouse. 
        if self.HasCapture():
            if not (midIsButt or ev.LeftIsDown()):
                #print "#debug hist: capture release"
                self.ReleaseMouse()
        else:
            if midButt or ev.LeftDown():
                #print "#debug hist: capture mouse"
                self.CaptureMouse()

                
        #20070713 if ev.Leaving():
        #20070713     #if(self.dragging):
        #20070713     #    print "TODO"
        #20070713     ## leaving trigger  event - bug !!
        #20070713     return

        if rightButt:
            pt = ev.GetPosition()
            self.PopupMenu(self.menu, pt)

        elif midButt:
            self.mouse_last_x, self.mouse_last_y = x,y
        elif midIsButt: #ev.Dragging()
            dx = x-self.mouse_last_x
            dy = y-self.mouse_last_y
            sfac = 1.05 ** dy ##(round(dy/10.)*10)
            self.m_tx += dx
            self.m_tx *= sfac
            self.m_tx += x* (1.-sfac)
            self.m_sx *= sfac

            self.mouse_last_x, self.mouse_last_y = x,y
            self.keepZoomedToBraces = False
            #20080731 self.zoomChanged = 1
            #20080731 self.Refresh(0)
            self.fitY() #20080731


        elif ev.LeftDown():
            self.mouse_last_x, self.mouse_last_y = x,y

            braceSpace4= abs(self.rightBrace-self.leftBrace) /4.
#           if braceSpace4 < 8./ float(self.m_sx):
#               braceSpace4 = 8./ float(self.m_sx)
            braceCenter= (self.rightBrace+self.leftBrace) / 2.
            self.dragCenter = (abs(xEff-braceCenter) < braceSpace4) 
            self.dragLeft = (abs(xEff-self.leftBrace) < abs(xEff-self.rightBrace))
        elif ev.LeftIsDown(): #ev.Dragging()
            d =(x-self.mouse_last_x) / float(self.m_sx)
            if self.dragCenter:
                self.leftBrace  += d
                self.rightBrace += d
                #CHECK  if self.leftBrace>= self.rightBrace:
                #CHECK      self.leftBrace = self.rightBrace -1
            elif self.dragLeft:
                self.leftBrace += d
                #CHECK  if self.leftBrace>= self.rightBrace:
                #CHECK      self.leftBrace = self.rightBrace -1
            else:
                self.rightBrace += d
                #CHECK  if self.rightBrace <= self.leftBrace:
                #CHECK     self.rightBrace = self.leftBrace +1

            self.mouse_last_x, self.mouse_last_y = x,y
            self.keepZoomedToBraces = False

            from .usefulX import _callAllEventHandlers
            _callAllEventHandlers(self.doOnBrace, (self,), "doOnBrace")
                    
            self.Refresh(0)


        """#20080731 unused -- OnWheel is called instead (mac)
        #print ev.GetEventType()
        elif ev.GetEventType() == wx.EVT_MOUSEWHEEL:
            print "DEBUG: wx.EVT_MOUSEWHEEL"
            d = ev.GetWheelRotation() / 120.0
            sfac = 1.2 ** d
            deltax = self.m_w * self.m_sx * .1 * d;
            print "wx.EVT_MOUSEWHEEL", d,sfac,deltax,self.m_w
            self.m_tx += .5 * self.m_sx * self.m_w * (1.-sfac)
            self.m_sx *= sfac
            self.zoomChanged = 1
            self.Refresh(0)
        """
        if ev.LeftDClick():
            print "x,y: %d %d    xEff: %.3f" %(x,y, xEff)

        from .usefulX import _callAllEventHandlers
        _callAllEventHandlers(self.doOnMouse, (xEff, ev), "doOnMouse")

    #20080707 def doOnMouse(self, xEff, bin):
    #20080707    pass

    def MakePopupMenu(self):
        """Make a menu that can be popped up later"""
        menu = wx.Menu()
        menu.Append(Menu_Reset, "zoom to full range")
        menu.Append(Menu_ZoomToBraces, "zoom to braces")
        menu.Append(Menu_AutoFit, "auto zoom + scale")
        #20051117 menu.Append(Menu_Gamma, "gamma...")

        menu.Append(Menu_Log, "log\tl")
        menu.Append(Menu_FitYToSeen, "auto fit y axis to shown values")
        menu.Append(Menu_EnterScale, "scale to ...\ts")
        wx.EVT_MENU(self, Menu_Reset, self.OnReset)
        wx.EVT_MENU(self, Menu_ZoomToBraces, self.zoomToBraces)
        wx.EVT_MENU(self, Menu_AutoFit, self.autoFit)
        wx.EVT_MENU(self, Menu_Log, self.OnLog)
        wx.EVT_MENU(self, Menu_FitYToSeen, self.OnFitYToSeen)
        wx.EVT_MENU(self, Menu_EnterScale, self.OnEnterScale)
        #20051117  wx.EVT_MENU(self, Menu_Gamma, self.OnMenuGamma)
        self.menu = menu

    def OnReset(self,ev):
        ma, mi = self.m_histPlotArray[-1,0], self.m_histPlotArray[0,0]
        if ma == mi: #CHECK
            ma += 1

        self.m_sx = self.m_w / float(ma-mi)
        self.m_tx = -mi * self.m_sx
        
        self.m_sy = 1
        self.m_ty = 0
        self.fitY()
        #  #  #          self.zoomChanged = 1
        #  #  #          self.Refresh(0)
        #      def OnFit(self,ev):
        #          self.fitXcontrast()

    def OnEnterScale(self,ev=77777):
        if ( hasattr(self, "my_viewer") and 
             hasattr(self.my_viewer, '_lastGamma_set')):
            defStr = '%s %s %s' %( self.leftBrace, self.rightBrace, 
                                   self.my_viewer._lastGamma_set)
        else:
            defStr = '%s %s' %( self.leftBrace, self.rightBrace)
        s = wx.GetTextFromUser('''enter min max values \n
     and (optinally) a gamma value\n
     if no gamma given, gamma stays as before''',
                               "min max [gamma]",
                               defStr)
        if s=='':
            return
        f = s.split()
        if len(f)>2:
            gamma = float(f[2])
        else:
            gamma = None
        self.setBraces(float(f[0]), float(f[1])) #20060823 , gamma)
        if gamma and hasattr(self, "my_viewer"):
            self.my_viewer._lastGamma_set = gamma
            from .viewerCommon import cm_gray
            self.my_viewer.setColMap( cm_gray(gamma) )
            
    def OnLog(self,ev=77777):
        if self.m_log:
            self.goLinear()
        else:
            self.goLog()            

    def OnFitYToSeen(self,ev=77777):
        self.fitYtoSeen = not self.fitYtoSeen
        self.fitY()
        
    #def OnClose(self, ev):
    #    print "OnCLose() - done."

    def setHist(self, yArray, xMin, xMax):
        import time
        x = time.clock()

        n = yArray.shape[0]
        #glSeb      print "setHist00     ms: %.2f"% ((time.clock()-x)*1000.0)
        if n < 2:
            raise ValueError, "cannot have Histogram with less than 2 bins"
        if xMin == xMax:
            #WARN:? print " ** setHist: xMin == xMax ==",xMin, "!! set xMax+=1"
            xMax+=1

        if self.m_histPlotArray is None or \
               self.m_histPlotArray.shape[0] != n:
            self.m_histPlotArray = N.zeros((n,2), N.float32)
            #glSeb          print "newshape:", (n,2)
        #glSeb      print "setHist01     ms: %.2f"% ((time.clock()-x)*1000.0)
        if self.m_log:
            self.m_histPlotArray[:,1] = N.log(yArray+HistLogModeZeroOffset)
        else:
            self.m_histPlotArray[:,1] = yArray

        #glSeb      print "setHist1 ms: %.2f"% ((time.clock()-x)*1000.0)

        #20070605  FIXME TODO - comparison of floats !?
        if self.m_histPlotArray.shape[0] != n or \
              self.m_histPlotArray[0,   0] != xMin or \
              self.m_histPlotArray[-1,  0] != xMax:
           self.m_histPlotArray[:,0] = N.linspace(xMin,xMax, n)
        #glSeb      print "setHist2 ms: %.2f"% ((time.clock()-x)*1000.0)

        #20111103 if not self.GetContext():
        #20111103     print " ** setHist: no self.GetContext():"
        #20111103     return

        #glSeb      print "setHist3 ms: %.2f"% ((time.clock()-x)*1000.0)
        self.set_current() # 2012 self.SetCurrent(self.context) # 20111103)
        #glSeb      print "setHist3b ms: %.2f"% ((time.clock()-x)*1000.0)
        #
        glSeb.glVertexPointer(self.m_histPlotArray)
        #glVertexPointerf(self.m_histPlotArray)
        
        #glSeb       print "setHist4 ms: %.2f"% ((time.clock()-x)*1000.0)

        self.fitY()
        #glSeb      print "setHist5 ms: %.2f"% ((time.clock()-x)*1000.0)
        
    def goLog(self):
        self.m_log = True
        self.m_histPlotArray[:,1] = N.log(self.m_histPlotArray[:,1]+HistLogModeZeroOffset)
        self.set_current() # 2012 self.SetCurrent(self.context) # 20111103)
        glSeb.glVertexPointer(self.m_histPlotArray)
        self.fitY()
        #self.Refresh(0)
        
    def goLinear(self):
        self.m_log = False
        self.m_histPlotArray[:,1] = N.exp(self.m_histPlotArray[:,1])-HistLogModeZeroOffset
        self.set_current() # 2012 self.SetCurrent(self.context) # 20111103)
        glSeb.glVertexPointer(self.m_histPlotArray)
        self.fitY()
        # self.Refresh(0)

    #20080707 def doOnBrace(self, left, right):
    #20080707    pass
    def fitY(self):
        if self.m_histPlotArray is None:
            return

        ys = self.m_histPlotArray[:,1]
        if self.fitYtoSeen:
            xs = self.m_histPlotArray[:,0]
            mi = -self.m_tx / self.m_sx
            ma = mi + self.m_w / self.m_sx
            shownIdxs = N.where((xs>=mi) & (xs<=ma))[0]
            if len(shownIdxs) == 0:
                return
            hm = ys[shownIdxs].max()
        else:
            hm = ys.max()

        if hm == 0:
            #nothing to fit -- done --raise "histogram 'empty'"
            return 
        if self.m_h == 0:
            #nothing to fit -- done --raise "window zero size"
            return
        self.m_sy = float(self.m_h) / hm *.95
        self.zoomChanged = 1
        self.Refresh(0)

    def zoomToBraces(self, ev=None): #fitXcontrast(self, ev=None):
        # self.m_ty =
        #print "#DEBUG: self.m_w", self.m_w
        self.keepZoomedToBraces=True # 20080806

        den = abs(float(self.rightBrace-self.leftBrace))
        if den == 0 or self.m_w <= 0:
            self.m_sx = 1
        else:
            self.m_sx = self.m_w / den
        self.m_tx = - self.leftBrace * self.m_sx
        # self.m_sy =
        self.zoomChanged = 1
        self.Refresh(0)

    def autoFit(self, ev=None, amin=None, amax=None, autoscale=True):
        # self.setBraces(   )
        whereHelper = None
        if amin is None:
            #20080730 amin = float( self.m_histPlotArray[0,0] ) # pyOpenGL cannot handle numpy.float32
            if self.m_log:
                whereHelper = N.where(self.m_histPlotArray[:,1]>-1)[0]
            else:
                whereHelper = N.where(self.m_histPlotArray[:,1]>0)[0]

            amin = self.m_histPlotArray[ whereHelper[0],  0]
        if amax is None:
            #20080730 amax = float( self.m_histPlotArray[-1,0] ) # pyOpenGL cannot handle numpy.float32
            if whereHelper is None:
                if self.m_log:
                    whereHelper = N.where(self.m_histPlotArray[:,1]>-1)[0]
                else:
                    whereHelper = N.where(self.m_histPlotArray[:,1]>0)[0]

            amax = self.m_histPlotArray[ whereHelper[-1],  0]
        self.leftBrace =  float(amin)  # fix numpy types like uint16 coming from a.min()
        self.rightBrace=  float(amax)
        #self.Refresh(0)
        if autoscale:
            self.zoomToBraces()
        else:
            self.Refresh(0)

        from .usefulX import _callAllEventHandlers
        _callAllEventHandlers(self.doOnBrace, (self,), "doOnBrace")

    def setBraces(self, l,r): #20060823 , gamma=None):
        self.leftBrace = float(l)
        self.rightBrace= float(r)

        from .usefulX import _callAllEventHandlers
        _callAllEventHandlers(self.doOnBrace, (self,), "doOnBrace")

        #20080707 self.doOnBrace(self.leftBrace, self.rightBrace) #20060823, gamma)
        self.Refresh(0)

def hist(histArray, hMin, hMax, title=""):
    #      global hframe
    #      global hcanvas
    frame = wx.Frame(None, -1, title)
    canvas = HistogramCanvas(frame, size=(400,100))

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(canvas, 1, wx.EXPAND | wx.ALL, 5);
    frame.SetSizer(sizer);
    sizer.SetSizeHints(frame);
    frame.SetAutoLayout(1)
    sizer.Fit(frame)

    frame.Show(1)
    wx.Yield() ## other raise "window zero size" in fitY(self)
    canvas.setHist(histArray, hMin, hMax)

    return canvas


