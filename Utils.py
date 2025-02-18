import math
import random

def colorHex(color, color_variation=5):
    r, g, b = color
    r = min(max(r + random.randint(-color_variation, color_variation), 0), 255)
    g = min(max(g + random.randint(-color_variation, color_variation), 0), 255)
    b = min(max(b + random.randint(-color_variation, color_variation), 0), 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def rainfallCurve(x):
    x = abs(x)
    return 0 if x > 1 else max(math.cos((3 * math.pi / 2) * x), 0) + max(math.cos((3 * math.pi / 2) * (x - 2/3)), 0) / 3
