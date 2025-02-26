#-*- coding:utf8 -*-

# PYTHON REFERENCE IMPLEMENTATION OF IMPROVED NOISE - COPYRIGHT 2002 KEN PERLIN.
import math

def PerlinNoise(x,y,z, octaves=6, persistence=0.5):
    # Sum of Noise Function = Perlin Noise
    # Each successive noise function you add is known as an octave
    total = 0
    p = persistence  # reference value:  1/4, 1/2 ,3/4 
    for i in range(octaves):
        frequency=2**i
        amplitude=p**i
        octave=ImprovedNoise(x * frequency, y * frequency, z * frequency) * amplitude
        total+=octave
    return total

def ImprovedNoise(x, y, z):
    # frequency=1/wavelength
    # It returns floating point numbers between -1.0 and 1.0
    # FIND UNIT CUBE THAT CONTAINS POINT.
    X = int(math.floor(x)) & 255
    Y = int(math.floor(y)) & 255
    Z = int(math.floor(z)) & 255

    # FIND RELATIVE X,Y,Z OF POINT IN CUBE.
    x -= math.floor(x)
    y -= math.floor(y)
    z -= math.floor(z)

    # COMPUTE FADE CURVES FOR EACH OF X,Y,Z.
    u,v,w = fade(x),fade(y),fade(z)

    # HASH COORDINATES OF THE 8 CUBE CORNERS
    # AND ADD BLENDED RESULTS FROM  8 CORNERS OF CUBE
    A = p[X  ]+Y; AA = p[A]+Z; AB = p[A+1]+Z
    B = p[X+1]+Y; BA = p[B]+Z; BB = p[B+1]+Z
    return lerp(w, lerp(v, lerp(u, grad(p[AA  ], x  , y  , z   ),
                                   grad(p[BA  ], x-1, y  , z   )),
                           lerp(u, grad(p[AB  ], x  , y-1, z   ),
                                   grad(p[BB  ], x-1, y-1, z   ))),
                   lerp(v, lerp(u, grad(p[AA+1], x  , y  , z-1 ),
                                   grad(p[BA+1], x-1, y  , z-1 )),
                           lerp(u, grad(p[AB+1], x  , y-1, z-1 ),
                                   grad(p[BB+1], x-1, y-1, z-1 ))))

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(t, a, b):
    return a + t * (b - a)

def grad(hash, x, y, z):
    # CONVERT LO 4 BITS OF HASH CODE INTO 12 GRADIENT DIRECTIONS.
    h = hash & 15
    u = x if h < 8 else y
    v = y if h < 4 else x if h==12 or h==14 else z

    return (u if (h&1)==0 else -u)+(v if (h&2)==0 else -v)


permutation = [ 151,160,137,91,90,15,
131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180
]
p=permutation*2
