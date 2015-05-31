Pythematica
=============

Pythematica is python package that allows for seamless interoperability between Python 
and Mathematica. On the python side it expresses python formulae as sympy expressions. 
It translates those into strings parsable by Mathematica, evaluates them in the 
Mathematica interpreter, and then parses the output back into sympy expressions. 

Examples:
----------

:: 

    >>> from pythematica import Pythematica
	
    >>> from sympy import exp, sin, cos, oo, sqrt, pi, I
    >>> from sympy.abc import x, y, u, v, n, k

    >>> m = Pythematica()
    >>> m.Integrate(x, x) 
    x**2/2
    >>> m.Integrate(exp(x), x) 
    exp(x)
    >>> m.Integrate(exp(-x**2), (x, -oo, +oo))
    sqrt(pi)
    >>> m( x+y )
    x + y
    >>> m( x-y )
    x - y
    >>> m( x/y )
    x/y
    >>> m.Sum(1/n**k, (k, 0, oo))
    n/(n - 1)
    >>> m.Sum(1/n**k, (k, 1, oo))
    1/(n - 1)
    >>> m.D(sin(x), x)
    cos(x)
    >>> m.D(sin(sin(x)), x)
    cos(x)*cos(sin(x))
    >>> m.Integrate(x**2, (x, -1, +1))
    2/3
    >>> m.Integrate(1/(x**2 + 1), (x, 0, +oo))
    pi/2
    >>> m.Integrate(sqrt(1 - x**2), (x, 0, 1))
    pi/4
    >>> m.Integrate(sin(x)*cos(x), (x, 0, pi))
    0
    >>> m.Integrate(sin(x)*cos(2*x), (x, 0, pi))
    -2/3
    >>> m.FourierTransform(exp(I*x), (x, y), (u, v))
    2*pi*DiracDelta(v)*DiracDelta(u + 1)
    >>> m.InverseFourierTransform(exp(I*x), (x, y), (u, v))
    2*pi*DiracDelta(v)*DiracDelta(u - 1)
    >>> m.InverseFourierTransform(
    ...     m.FourierTransform(exp(I*x), (x, y), (u, v)), 
    ...     (u, v), (x, y))
    exp(I*x)
    >>> m.Integrate(exp(I*x), (x, 0, pi))
    2*I

Installation:
--------------

First make sure that all the unit tests pass:

::

    $ py.test --doctest-module pythematica.py

Then, to install simply run in your favorite shell:

::

    $ python setup.py install
	
