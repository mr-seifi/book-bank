def batch(iterable, n=5000):
    l = len(iterable)

    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]
