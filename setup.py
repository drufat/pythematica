from distutils.core import setup

setup(name='pythematica',
    modules=['pythematica'],
    description='Python bindings to Mathematica',
    author='Dzhelil Rufat',
    author_email='drufat@caltech.edu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    requires = ['sympy', 'pexpect'],
)
