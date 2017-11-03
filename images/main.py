# Image manipulation
#
# You'll need to do this:
#
#   pip install numpy
#   pip install PyOpenGL
#   pip install Pillow


import sys, os, numpy

try: # Pillow
  from PIL import Image, ImageOps
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

factor = 1 # factor by which luminance is scaled

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

    imgDir = 'data'
    imgFilename = 'mandrill.png'

    # Read image and convert to YCbCr
    src = Image.open( os.path.join(imgDir, imgFilename) ).convert( 'YCbCr' )
    srcPixels = src.load()

    hist = calcHistogram(src, srcPixels)
    # Set up a new, blank image of the same size

    dst = Image.new( 'YCbCr', (src.width,src.height) )
    dstPixels = dst.load()

	# Run histogram calculation
    h = calcHistogram(src, srcPixels)
    cdf = numpy.array(cumsum(h)) # cumulative distribution function
    transFn = numpy.uint8(255 * cdf) # finding transfer function values

    # Build destination image from source image

    for i in range(src.width):
        for j in range(src.height):

            # read source pixel

            y,cb,cr = srcPixels[i,j]

            # ---- MODIFY PIXEL ----
            y = transFn[y]
            y = factor * y

            # write destination pixel (while flipping the image in the vertical direction)
            
            dstPixels[i,src.height-j-1] = (y,cb,cr)

    # Done

    return dst.convert( 'RGB' )



# Set up the display and draw the current image

def display():

    # Clear window

    glClearColor ( 1, 1, 1, 0 )
    glClear( GL_COLOR_BUFFER_BIT )

    # rebuild the image

    img = buildImage()

    # Find where to position lower-left corner of image

    baseX = (windowWidth-img.width)/2
    baseY = (windowHeight-img.height)/2

    glWindowPos2i( baseX, baseY )

    # Get pixels and draw

    imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

    glDrawPixels( img.width, img.height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

    glutSwapBuffers()


    
# Handle keyboard input

def keyboard( key, x, y ):

    if key == '\033': # ESC = exit
        sys.exit(0)
    else:
        print 'key =', key

    glutPostRedisplay()



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

    global button, initX, initY, initFactor

    if state == GLUT_DOWN:

        button = btn
        initX = x
        initY = y
        initFactor = factor

    elif state == GLUT_UP:

        button = None



# Handle mouse motion

def motion( x, y ):

    diffX = x - initX
    diffY = y - initY

    global factor

    factor = initFactor + diffX / float(windowWidth)

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
