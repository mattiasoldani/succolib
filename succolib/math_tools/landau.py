from numpy import exp


########################################################################################################################
# fLandau ##############################################################################################################
"""
fLandau is the Landau's distribution

fLandau(x, A, mpv, width)
x is the distribution variable
A is the distribution amplitude
mpv is the distribution most probable value
width is the distribution width

function format: A * exp[ - (1/2) * ( (x-mpv)/width + exp(-(x-mpv)/width) ) ]

dependencies: numpy.exp
"""

def fLandau(x, A, mpv, width):
    expo0 = (x-mpv)/width
    expo1 = exp(-expo0)
    return A*exp(-0.5*(expo0+expo1))


########################################################################################################################
# fLandauMirror ########################################################################################################
"""
fLandauMirror is the mirrored Landau's distribution, i.e. with inverted abscissas

fLandauMirror(x, A, mpv, width)
x is the distribution variable
A is the distribution amplitude
mpv is the distribution most probable value
width is the distribution width

function format: A * exp[ - (1/2) * ( (mpv-x)/width + exp(-(mpv-x)/width) ) ]

dependencies: numpy.exp
"""

def fLandauMirror(x, A, mpv, width):
    expo0 = (mpv-x)/width
    expo1 = exp(-expo0)
    return A*exp(-0.5*(expo0+expo1))