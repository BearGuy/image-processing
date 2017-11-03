# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow

import sys, os, numpy

try: # Pillow
  from PIL import Image
except:
  print 'Error: Pillow has not been installed.'
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print 'Error: PyOpenGL has not been installed.'
  sys.exit(0)


# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800

global imgFilter
imgFilter = "normal"

factor = 1 # factor by which luminance is scaled
contrast = 1 # initial contrast factor



# Image directory and pathe to image file

imgDir      = 'images'
imgFilename = 'mandrill.png'

imgPath = os.path.join( imgDir, imgFilename )



# File dialog

# import Tkinter, tkFileDialog

# root = Tkinter.Tk()
# root.withdraw()

# Histogram Calculation

def calcHistogram(src, srcPixels):
	h = [0.0] * 256

	for i in range(src.width):
		for j in range(src.height):
			y,cb,cr = srcPixels[i,j]

			h[y] += 1

	return numpy.array(h)/(src.width * src.height) 

def cumsum(h):
  # finds cumulative sum of a numpy array, list
	return [sum(h[:i+1]) for i in range(len(h))] 


# Read and modify an image.

def buildImage():

  # Read image and convert to YCbCr

  print imgPath
  print imgFilter
  src = Image.open( imgPath ).convert( 'YCbCr' )
  srcPixels = src.load()

  width  = src.size[0]
  height = src.size[1]

  # Set up a new, blank image of the same size

  dst = Image.new( 'YCbCr', (width,height) )
  dstPixels = dst.load()

  # Run histogram calculation
  
  if imgFilter == "histogram":
    h = calcHistogram(src, srcPixels)
    cdf = numpy.array(cumsum(h)) # cumulative distribution function
    transFn = numpy.uint8(255 * cdf) # finding transfer function values

  # Build destination image from source image

  for i in range(width):
    for j in range(height):

      # read source pixel
      
      y,cb,cr = srcPixels[i,j]

      if imgFilter == "histogram":
        y = transFn[y]
      
      # ---- MODIFY PIXEL ----

      y = int(factor * y)
      y = int(128 + contrast * (y - 128))
      y = max(0, min(255, y))

      # write destination pixel (while flipping the image in the vertical direction)
      
      dstPixels[i,height-j-1] = (y,cb,cr)

  # Done
  print contrast
  return dst.convert( 'RGB' )



# Set up the display and draw the current image

def display():
  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  # rebuild the image

  img = buildImage()

  width  = img.size[0]
  height = img.size[1]

  # Find where to position lower-left corner of image

  baseX = (windowWidth-width)/2
  baseY = (windowHeight-height)/2

  glWindowPos2i( baseX, baseY )

  # Get pixels and draw

  imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

  glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

  glutSwapBuffers()


  
# Handle keyboard input

def keyboard( key, x, y ):

  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'h':
    global imgFilter
    imgFilter = "histogram"

  elif key == 'n':
    global imgFilter
    imgFilter = "normal"
    
  # elif key == 'l':
  #   path = tkFileDialog.askopenfilename( initialdir = imgDir )
  #   if path:
  #     loadImage( path )

  # elif key == 's':
  #   outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
  #   if outputPath:
  #     saveImage( outputPath )

  else:
    print 'key =', key    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

  glutPostRedisplay()



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.

def loadImage( path ):

  global imgPath
  imgPath = path

def saveImage( path ):

  buildImage().save( path )

  

# Handle window reshape

def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glutPostRedisplay()



# Mouse state on initial click

button = None
initX = 0
initY = 0
initFactor = 0



# Handle mouse click/unclick

def mouse( btn, state, x, y ):

  global button, initX, initY, initFactor, initContrast

  if state == GLUT_DOWN:

    button = btn
    initX = x
    initY = y
    initFactor = factor
    initContrast = contrast

  elif state == GLUT_UP:

    button = None



# Handle mouse motion

def motion( x, y ):

  diffX = x - initX
  diffY = y - initY

  global factor
  global contrast

  factor = initFactor + diffX / float(windowWidth)

  contrast = initContrast + diffY / float(windowHeight)
  # (259 * (initContrast + diffY + 255)) / (255 * (259 - initContrast + diffY))

  if factor < 0:
    factor = 0

  glutPostRedisplay()
  

    
# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()
