"""
Some implementations to currify/uncurrify functions.

All implementations require that there are no keyword args, 
    and any default arguments will be treated like normal arguments.
These curry functions can also be used as decorators, with the exception of
    stringCurry.
"""

import inspect
import functools

"""
My initial and very crude implementation of curryifying function. 
Builds a lambda function as a string that eventually just calls the original
function with the curried arguments, and returns the eval of the string.

This implementation will only work with named functions and not with 
anonymous functions.

"""
def stringCurry(f):
    args, varargs, kwargs, defaults = inspect.getargspec(f)
    sourceLines = inspect.getsourcelines(f)[0]
    func = list(filter(lambda x: x.startswith("def "), sourceLines))[0]
    g = func[4:func.find(")")+1]
    while args != []:
        curArg = args.pop(-1)
        g = "lambda %s: %s" %(curArg, g)
    return eval(g)


"""
Second curry implementation. It uses functool's partial function to recursively
build a new function until all the arguments are curried.
"""
def wrapperCurry(f):
    argLen = len(inspect.getargspec(f).args)
    @functools.wraps(f)
    def new(arg):
        if argLen <= 1:
            return f(arg)
        else:
            return wrapperCurry(functools.partial(f, arg))
    return new

"""
This implementation also uses functool's partial function to recursively build
a currified function, but does so anonymously.
"""
def lambdaCurry(f):
    if len(inspect.getargspec(f).args) == 0:
        return f()
    return lambda x: lambdaCurry(functools.partial(f, x))
import types

"""
Converts a curried function into a uncurried function. If the number of
arguments is provided, it will 'uncurrify' the number of arguments specified.

For example, a curried function of type f(a)(b)(c), when uncurried with 
arguments = 2, will return a function of type f(a,b)(c).
If the number of arguments is not specified, it will uncurry until the returning
value is no longer a function. 
This means that to make it work for a function that returns a function,
the number of arguments must be specified.
"""
def unCurry(f, arguments = None):
        def fullyCurry(*args):
            argLen = 0
            output = f
            prev = 0
            while isinstance(output, types.FunctionType) and prev < len(args)-1: 
                try:
                    prev = argLen
                    argLen = prev + len(inspect.getargspec(output).args)
                    output = output(*args[prev:argLen])
                except TypeError:
                    raise Exception ("Expected more arguments")
                except IndexError:
                    print(prev, args)
                    raise Exception ("Expected less arguments")
            if argLen < len(args) :
                raise Exception("Too many arguments")
            elif isinstance(output, types.FunctionType):
                raise Exception("Too few arguments")
            print(prev, argLen, len(args))
            return output

        def curryTo(*args):
            
            if len(args) > arguments:
                raise TypeError("%d arguments were asked to be \curried for %s \
                    but %d were given" %(arguments, f.__name__, len(args)))
            output = f
            prev = 0
            argLen = 0

            for arg in range(arguments):
                try:
                    prev = argLen
                    argLen = prev + len(inspect.getargspec(output).args)
                    output = output(*args[prev:argLen])
                except IndexError:
                    raise TypeError("%d arguments were asked to be curried for \
                        %s but %d only were given" %(arguments,f.__name__, arg))

            return output

        if arguments == None: return fullyCurry
        else: 
            return curryTo
