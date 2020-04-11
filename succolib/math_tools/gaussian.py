from numpy import exp


########################################################################################################################
# fGaus ################################################################################################################
"""
fGaus is the Gaussian distribution

fGaus(x, A, u, sigma) is the Gaussian distribution
x is the distribution variable
A is the distribution amplitude
u is the distribution mean
sigma is the distribution sigma

function format: A * exp[ - ( (x-u)^2 / (2*(sigma)^2) ) ]

dependencies: numpy.exp
"""

def fGaus(x, A, u, sigma):
    expo = -(x-u)**2/(2*sigma**2)
    return A*exp(expo)