# Return the value of a range, or a single value if it is not a range
def safe_index(range, i):
    if isinstance(range, (int, float)):
        return range
    return range[i]

# Add a value to a given index in the array, growing the array if needed
def add_value_to_index(array, index, value):
    # Extend the array if the index is out of bounds
    if index >= len(array):
        array.extend([0] * (index - len(array) + 1))
    
    # Add the value to the specified index
    array[index] += value