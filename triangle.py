import numpy as np # linear algebra library

# Return a single random number, given a low, expected, and high range, using a triangular distribution
# Just return the expected number if requested, or if the range is invalid
def triangle(a, just_expected = False):

    # if a is a single number, return it
    if isinstance(a, (int, float)):
        return a

    # if the range is invalid, return the likely (middle) value
    if(a[0] > a[1] or a[1] > a[2] or a[0] >= a[2]):
        return a[1]
    
    # if requested, just return the likely (middle) value
    if (just_expected):
        return a[1]
    
    # return a random number, given a low, likely, and high range, using a triangular distribution
    return np.random.triangular(a[0], a[1], a[2])