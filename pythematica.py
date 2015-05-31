import pexpect
import sympy
import re as regex
from sympy.printing import mathematica_code
from sympy.functions.special.delta_functions import DiracDelta

trans = {
    'Exp'       : sympy.exp,
    'Log'       : sympy.log,
    'Sin'       : sympy.sin,
    'Cos'       : sympy.cos,
    'Tan'       : sympy.tan,
    'Cot'       : sympy.cot,
    'ArcSin'    : sympy.asin,
    'ArcCos'    : sympy.acos,
    'ArcTan'    : sympy.atan,
    'ArcSinh'   : sympy.asinh,
    'ArcCosh'   : sympy.acosh,
    'ArcTanh'   : sympy.atanh,
    'ArcCoth'   : sympy.acoth,
    'Cosh'      : sympy.cosh,
    'Coth'      : sympy.coth,
    'Sinh'      : sympy.sinh,
    'Tanh'      : sympy.tanh,
    'Sqrt'      : sympy.sqrt,
    
    'Plus'      : sympy.Add,
    'Times'     : sympy.Mul,
    'Power'     : sympy.Pow,
    
    'List'      : lambda *args: args,

    'Pi'                : sympy.pi,
    'Infinity'          : sympy.oo,
    'DirectedInfinity'  : lambda x: x*sympy.oo,
    'Complex'           : lambda x, y: x + sympy.I * y,
    'DiracDelta'        : DiracDelta,
    

}

def sanitize(mexpr):
    '''
    >>> sanitize('Hold[x]')
    'x'
    >>> sanitize('x')
    'x'
    '''
    s = regex.search('Hold\[(.*)\]', mexpr)
    if s:
        return s.group(1)
    else:
        return mexpr

prompt = b'In\[\d+\]\:\='
output = b'Out\[\d+\]//FullForm=(.*)\r\n\r\n'

def to_mathematica(mexpr):
    '''
    >>> from sympy import *
    >>> from sympy.abc import x, y
    >>> T = to_mathematica
    >>> T(sin(x))
    'Sin[x]'
    >>> T(x**y)
    'x^y'
    >>> T((x, -oo, +oo))
    '{x, -Infinity, Infinity}'
    '''
    return sanitize(mathematica_code(mexpr))

def from_mathematica(mexpr):
    '''
    >>> from sympy import *
    >>> from sympy.abc import x, y
    >>> F = from_mathematica
    >>> assert F('Rational[1, 2]') == Integer(1)/Integer(2)
    >>> assert F('Times[Rational[1, 2], Power[x, 2]]') == 1/2*x**2
    >>> assert F('Power[E, x]') == exp(x)
    >>> assert F('Plus[x, y]') == x + y
    >>> assert F('Plus[x, Times[-1, y]]') == x - y
    >>> assert F('Times[x, Power[y, -1]]') == x/ y
    >>> assert F('Cos[x]') == cos(x)
    >>> assert F('Power[Pi, 2]') == pi**2
    >>> assert F('Power[Pi, Rational[1, 2]]') == sqrt(pi)
    >>> assert F('Power[Pi, Rational[-1, 2]]') == 1/sqrt(pi)
    '''
    mexpr = regex.sub('\[', '(', mexpr)
    mexpr = regex.sub('\]', ')', mexpr)
    mexpr = regex.sub('\{', '(', mexpr)
    mexpr = regex.sub('\}', ')', mexpr)
    return sympy.sympify(mexpr, locals=trans)

class Mathematica(object):
    '''
    >>> m = Mathematica()
    >>> m( 'Integrate[x, x]' )
    'Times[Rational[1, 2], Power[x, 2]]'
    >>> m( 'x+y' )
    'Plus[x, y]'
    >>> m( 'x-y' )
    'Plus[x, Times[-1, y]]'
    >>> m( 'x/y' )
    'Times[x, Power[y, -1]]'
    >>> m( 'D[Sin[x], x]' )
    'Cos[x]'
    >>> m( 'Integrate[x^2, {x, -1, 1}]' )
    'Rational[2, 3]'
    '''
        
    def __init__(self, program='wolfram'):
        self.m = pexpect.spawn('{} {}'.format(program, '-rawterm'))
        self.m.expect(prompt)

    def __del__(self):
        self.m.sendline(b'Quit')
        self.m.expect(pexpect.EOF)

    def __call__(self, strexpr):
        self.m.sendline('FullForm[{}]'.format(strexpr).encode())
        self.m.expect(prompt)
        s = regex.search(output, self.m.before, flags=regex.DOTALL)
        rslt = s.group(1).strip().decode()
        rslt = regex.sub('>', '', rslt)
        rslt = regex.sub('\s+', ' ', rslt) #replace white spaces
        rslt = rslt.strip()
        return rslt

def get_mathematica_func(m, name):
    def func(*args):
        mexpr = to_mathematica(args)
        mexpr = m('Apply[{}, {}]'.format(name, mexpr))
        mexpr = from_mathematica(mexpr)
        return mexpr
    return func

class Pythematica(object):
    '''
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
    '''

    def __init__(self, program='wolfram'):
        self.m = Mathematica(program=program)

    def __call__(self, mexpr):
        mexpr = to_mathematica(mexpr)
        mexpr = self.m(mexpr)
        mexpr = from_mathematica(mexpr)
        return mexpr
    
    def __getattr__(self, name):
        return get_mathematica_func(self.m, name)
        
