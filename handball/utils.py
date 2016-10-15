# coding: utf-8


def just(n, seq, default=None):
    """
    A handy little function that accepts a number and a sequence and returns a
    generator that has n element with a single value in each except the last
    one which is a tuple with the rest of the elements from the iterator (or
    an empty tuple if none are left).

    If len(seq) < n the missing elements will be set to whatever is passed as
    default (by default None). In other words, the function always returns a
    generator with n values.


    Examples:
    >>> list(just(3, range(10)))
    [0, 1, (2, 3, 4, 5, 6, 7, 8, 9)]

    >>> list(just(3, range(2)))
    [0, 1, ()]

    >>> list(just(10, range(3)))
    [0, 1, 2, None, None, None, None, None, None, ()]

    >>> list(just(1, range(3)))
    [(0, 1, 2)]

    >>> list(just(5, range(3), default=1))
    [0, 1, 2, 1, ()]
    """
    it = iter(seq)
    for _ in range(n - 1):
        yield next(it, default)
    yield tuple(it)

def ignore_exception(exception=Exception, default=None):
    """Returns a decorator that ignores an exception raised by the function it
    decorates.

    Using it as a decorator:

    @ignore_exception(ValueError)
    def my_function():
        pass

    Using it as a function wrapper:

    >>> int_try_parse = ignore_exception(ValueError, 0)(int)
    >>> int_try_parse("")
    0

    >>> int_try_parse("a")
    0

    >>> int_try_parse("5")
    5
    """
    def decorator(function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exception:
                return default
        return wrapper
    return decorator
