def add_numbers(a, b):
    if not isinstance(a, int) or isinstance(a, bool):
        raise TypeError(f"Expected int for 'a', got {type(a).__name__}")
    if not isinstance(b, int) or isinstance(b, bool):
        raise TypeError(f"Expected int for 'b', got {type(b).__name__}")
    return a + b
