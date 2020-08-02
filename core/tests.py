from django.test import TestCase


def foo(a, b, c):
    print("a = %d, b = %d, c = %d" % (a, b, c))


y = {'a': 7, 'b': 8, 'c': 9}
foo(*y)
