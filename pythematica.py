import pexpect
import sympy
import re
from sympy.printing import mathematica_code

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
    #'ArcCsch'   : sympy.acsch,
    #'ArcSech'   : sympy.asech,
    'Cosh'      : sympy.cosh,
    'Coth'      : sympy.coth,
    #'Csch'      : sympy.csch,
    #'Sech'      : sympy.sech,
    'Sinh'      : sympy.sinh,
    'Tanh'      : sympy.tanh,
    'Sqrt'      : sympy.sqrt,
    
    'Plus'      : sympy.Add,
    'Times'     : sympy.Mul,
    'Power'     : sympy.Pow,
    
    'Integrate' : sympy.Integral,
    'D'         : sympy.diff,

    'Pi'                : sympy.pi,
    'Infinity'          : sympy.oo,
    'DirectedInfinity'  : lambda x: x*sympy.oo,
    'Complex'           : lambda x, y: x + sympy.I * y,

    'List'      : lambda *args: args
}

def sanitize(mexpr):
    '''
    >>> sanitize('Hold[x]')
    'x'
    >>> sanitize('x')
    'x'
    '''
    s = re.search('Hold\[(.*)\]', mexpr)
    if s:
        return s.group(1)
    else:
        return mexpr

prompt = b'In\[\d+\]\:\='
output = b'Out\[\d+\]//FullForm=(.*)\r\n\r\n'

def to_mathematica(mexpr):
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
    mexpr = re.sub('\[', '(', mexpr)
    mexpr = re.sub('\]', ')', mexpr)
    return sympy.sympify(mexpr, locals=trans)

class Mathematica(object):
        
    def __init__(self, program='wolfram'):
        self.m = pexpect.spawn('{} {}'.format(program, '-rawterm'))
        self.m.expect(prompt)

    def call_string(self, strexpr):
        self.m.sendline('FullForm[{}]'.format(strexpr).encode())
        self.m.expect(prompt)
        s = re.search(output, self.m.before, flags=re.DOTALL)
        rslt = s.group(1).strip().decode()
        rslt = re.sub('>', '', rslt)
        rslt = re.sub('\s+', ' ', rslt) #replace white spaces
        rslt = rslt.strip()
        return rslt

    def __call__(self, mexpr):
        if type(mexpr) is str:
            return self.call_string(mexpr)
        else: #assume sypmpy expression
            mexpr = to_mathematica(mexpr)
            mexpr = self.call_string(mexpr)
            mexpr = from_mathematica(mexpr)
            return mexpr

    def __del__(self):
        self.m.sendline(b'Quit')
        self.m.expect(pexpect.EOF)

def example1():
    
    print('\nMathematica:')
    m = Mathematica()
    print(m( 'Integrate[x, x]' ))
    print(m( 'Integrate[Exp[x], x]' ))
    print(m( 'Integrate[Exp[-x^2], {x, -Infinity, +Infinity}]' ))
    print(m( 'x+y' ))
    print(m( 'x-y' ))
    print(m( 'x/y' ))
    print(m( 'D[Sin[x], x]' ))
    print(m( 'D[Sin[Sin[x]], x]' ))
    print(m( 'Integrate[x^2, {x, -1, 1}]' ))
    print(m( 'FourierTransform[Sin[x], {x, y}, {u, v}]' ))
    print(m( 'InverseFourierTransform[Sin[x], {x, y}, {u, v}]' ))
    print(m( 'Integrate[Exp[I x], {x, 0, Pi}]' ))
    print(m( 'I*I' ))

def example2():

    from sympy import Integral, exp, diff, sin, cos, oo, sqrt, pi, I
    from sympy.abc import x, y

    print('\nSympy:')
    m = Mathematica()
    print(m( Integral(x, x) ))
    print(m( Integral(exp(x), x) ))
    print(m( Integral(exp(-x**2), (x, -oo, +oo)) ))
    print(m( x+y ))
    print(m( x-y ))
    print(m( x/y ))
    print(m( diff(sin(x), x) ))
    print(m( diff(sin(sin(x)), x) ))
    print(m( Integral(x**2, (x, -1, +1)) ))
    print(m( Integral(1/(x**2 + 1), (x, 0, +oo)) ))
    print(m( Integral(sqrt(1 - x**2), (x, 0, 1)) ))
    print(m( Integral(sin(x)*cos(x), (x, 0, pi)) ))
    print(m( Integral(sin(x)*cos(2*x), (x, 0, pi)) ))
    print(m( Integral(exp(I*x), (x, 0, pi)) ))
    print(m( I*I ))

if __name__ == '__main__':
    example1()
    example2()
    
