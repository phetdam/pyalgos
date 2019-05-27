__doc__ = """
file for testing the different functions in pyalgos. can specify which modules
to dynamically load and unload, and test each function with different args.

IMPORTANT: this script should be in the same directory as the pyalgos package!

add more examples by defining new objects, and then also defining a string
name for that object as well; i.e. object foo has name foo__name (string).
then create an entry in _INPUT_LIST of the following format (nested dict):

for an object foo:

foo__name:
{_ENAME: foo__name, _EVALUE: foo,
 _EBLURB: ("Some helpful description about the object.\\n\\nView:\\n{0}\\n"
           "".format(foo))}

recommended for nested lists: in format(), replace foo with
str(foo).replace("],", "],\\n") or equivalent as necessary.

in this manner, it becomes possible to look the object up with the info
command and see what exactly is being passed into a function.
"""
# Changelog:
#
# 05-26-2019
#
# added implementations for the help function, and started writing code for the
# test command, which is the main command to be used for testing modules. added
# functionality for the test command, by using eval to evaluate expressions with
# the interpreter and return the formatted string output. added checks for
# the package being in the same directory as this file. started work on the
# info command.
#
# 05-25-2019
#
# added changelog, changed name. added graph examples and changed direction of
# the script; it is now to become an interactive script for testing. python's
# ability to introspect will be used to retrieve function arguments so that they
# can all be passed at will to test every argument combination on predefined
# example inputs, which are included in this file.
#
# 05-23-2019
#
# initial creation.

import importlib # dynamic imports
import inspect # for object introspection (unused except in main)
import os # for file, misc os stuff
import pkgutil # for module/package introspection
import sys
import textwrap # for wrapping lines

from pyalgos import _PACKAGE_NAME # global package name
from pyalgos import graph

### global variables ###

# package path
_PACKAGE_PATH = "./"

# program name
_PROGNAME = "pyalgos_test"

# help flag
_HELP_FLAG = "--help"

# help string
_HELP_STR = ("Usage: {0} [ {1} ]\n\n"
             "{0} is an interactive script that allows the user to dynamically "
             "load different modules from the {2} package, and run them on "
             "different predefined examples for each module. type '{0} {1}' for"
             " this usage.\n\nhelp on the individual commands can be found by "
             "invoking the 'help' command while in the interpreter. note that "
             "the {2} package must be in the same directory as {0}, or else the"
             " script will not run."
             "".format(_PROGNAME, _HELP_FLAG, _PACKAGE_NAME))

# useful for indexing command names and help blurbs
_CNAME = "_cname"
_CHELP = "_chelp"

# default string if there is no help blurb available for the command
_NOHELP = "No help string available for this command."

# command names, abstracted into variable names
C_EXIT = "exit"
C_QUIT = "quit"
C_HELP = "help"
C_TEST = "test"
C_INFO = "info"
C_INFO_SRC = "source"
C_INFO_INP = "inputs"

# global dictionary of imported modules
_IMPORT_LIST = {}

# dictionary of available commands (for lookup purposes)
_COMMAND_LIST = {C_EXIT:
                 {_CNAME: C_EXIT,
                  _CHELP: "Usage: {0}\n\nExits the program.".format(C_EXIT)},
                 C_QUIT:
                 {_CNAME: C_QUIT,
                  _CHELP: "Usage: {0}\n\nExits the program.".format(C_QUIT)},
                 C_HELP:
                 {_CNAME: C_HELP,
                  _CHELP: ("Usage: {0} [ command ] \n\nReturns the help blurb "
                           "for the specified command. '{0} {0}' returns this "
                           "blurb, while specifying no arguments returns a "
                           "list of all available commands.\n".format(C_HELP))},
                  C_TEST:
                  {_CNAME: C_TEST,
                   _CHELP: ("Usage: {0} module_name.function_name < arg1, arg2,"
                            " ... \n\n"
                            "Tests a function specified by function_name from "
                            "module module_name. args is a sequence of comma-"
                            "separated strings, representing any args for the "
                            "specified function. arguments may either be "
                            "manually specified, or refer to any predefined"
                            " internal examples whose descriptions may be "
                            "retrieved with the '{1}' command.\n"
                            "".format(C_TEST, C_INFO))},
                 C_INFO:
                 {_CNAME: C_INFO,
                  _CHELP: ("Usage: {0} {1} [ module_name module_name."
                           "function_name ]\n"
                           "       {0} {2} [ sample_input ]\n\n"
                           "Retrieves information on the given object. "
                           "Subcommands:\n\n"
                           "{1}\n\nRetrieves information on a module or "
                           "function. If a module is specified, then a list of "
                           "functions in the module is returned. If a function "
                           "is specified, then the docstring for that function "
                           "is displayed using Python's help() command. If no "
                           "arguments are given, then a list of all modules in "
                           "{3} will be displayed, with loading status.\n\n"
                           "{2}\n\nRetrieves information on the sample inputs "
                           "provided in the script. If an input name is "
                           "specified, its associated descriptive blurb will be"
                           " returned. If no input name is specified, then a "
                           "list of all the sample inputs is returned.\n"
                           "".format(C_INFO, C_INFO_SRC, C_INFO_INP,
                                     _PACKAGE_NAME))}
}

## graph examples ##

# suffix 'al' denotes adjacency list, suffix 'am' denotes adjacency matrix.
# prefix 'w' denotes weighted, prefix 'u' denotes that unweighted graph.

# directed acyclic graphs and names
u_dag01_al = [[1, 2, 4], [], [3, 4, 5], [], [3, 5], []]
u_dag01_al__name = "u_dag01_al"
u_dag01_am = [[False, True, True, False, True, False],
              [False, False, False, False, False, False],
              [False, False, False, True, True, True],
              [False, False, False, False, False, False],
              [False, False, False, True, False, True],
              [False, False, False, False, False, False]]
u_dag01_am__name = "u_dag01_am"
u_dag02_al = [[1, 2, 3, 4, 5], [3], [4, 5], [5], [], []]
u_dag02_al__name = "u_dag02_al"
u_dag02_am = [[False, True, True, True, True, True],
              [False, False, False, True, False, False],
              [False, False, False, False, True, True],
              [False, False, False, False, False, True],
              [False, False, False, False, False, False],
              [False, False, False, False, False, False]]
u_dag02_am__name = "u_dag02_am"

# directed graphs with cycles

# for indexing example names, values, and descriptions
_ENAME = "_ename"
_EVALUE = "_evalue"
_EBLURB = "_eblurb"

# dictionary of sample inputs, indexed by variable name.
_INPUT_LIST = {u_dag01_al__name:
               {_ENAME: u_dag01_al__name, _EVALUE: u_dag01_al,
                _EBLURB: ("Directed acyclic graph 1, adjacency list form. "
                          "Has 6 vertices.\n\nView:\n{0}\n".format(u_dag01_al))},
               u_dag01_am__name:
               {_ENAME: u_dag01_al__name, _EVALUE: u_dag01_am,
                _EBLURB: ("Directed acyclic graph 1, adjacency matrix form"
                          ". Has 6 vertices.\n\nView:\n{0}\n"
                          "".format(str(u_dag01_am).replace("],", "],\n")))},
               u_dag02_al__name:
               {_ENAME: u_dag02_al__name, _EVALUE: u_dag02_al,
                _EBLURB: ("Directed acyclic graph 2, adjacency list form. "
                          "Has 6 vertices.\n\nView:\n{0}\n".format(u_dag02_al))},
               u_dag02_am__name:
               {_ENAME: u_dag02_am__name, _EVALUE: u_dag02_am,
                _EBLURB: ("Directed acyclic graph 2, adjacency matrix form"
                          ". Has 6 vertices.\n\nView:\n{0}\n"
                          "".format(str(u_dag02_am).replace("],", "],\n")))}
}

### utility functions ###

# string formatter; can specify width. returns arg as string block (with \n) as
# a formatted string block that is 80 chars wide per line. textwrap extension.
def _strwrap(s, width = 80):
    # split by newlines, proxy for paragraph breaks
    paras = s.split("\n")
    # for each paragraph in paras
    for i in range(len(paras)):
        # if the paragraph is an empty string, ignore
        if paras[i] == "": pass
        # else wrap lines without replacing whitespace
        else:
            # break into list of strings, then join by newline
            hlines = textwrap.wrap(paras[i], width = width,
                                   replace_whitespace = False)
            paras[i] = "\n".join(hlines)
    # return all strings in paras joined by newlines
    return "\n".join(paras)

# prints standard "unknown fatal error" message. DOES NOT EXIT, only prints the
# error message. change file if necessary.
def _ufatal(fname, file = sys.stderr):
    print("{0}: error: unknown fatal error\n".format(fname), file = file)

# standard input splitter. first attempts to split off function arguments; else
# will just split by whitespace. important because the test command takes a
# different input format from the other commands.
def _argsplit(s):
    # attempt to split the string by "<"
    tokens = s.split("<")
    # if the length is 0, just return empty list
    if len(tokens) == 0:
        return []
    # else if the length is 1, return tokens split by spaces
    elif len(tokens) == 1:
        return tokens[0].split()
    # else if there are more than 2 tokens, there is a syntax error, so reflect
    # an error and then return empty list (input loop will skip rest of loop)
    elif len(tokens) > 2:
        print("{0}: syntax error: too many '<'-delineated tokens."
              "".format(_PROGNAME))
        return []
    # else split first token by spaces, split second token by commas
    preargs = tokens[0].split()
    # if there are not exactly two 2 preargs, print error and return []
    if len(preargs) != 2:
        print("{0}: syntax error: 2 pre-'<' arguments required, {1} received"
              "".format(_PROGNAME, len(preargs)))
        return []
    postargs = tokens[1].split(",")
    # strip whitespace from all preargs and postargs
    for i in range(len(preargs)): preargs[i] = preargs[i].strip()
    for i in range(len(postargs)): postargs[i] = postargs[i].strip()
    # add first prearg (command name) to new list of tokens with the rest of the
    # preargs in a list, followed by the postargs in a list
    tokens = [preargs[0], preargs[1:], postargs]
    # return tokens (format: [command_name, [prearg_1, ...], [postarg_1, ...]]
    return tokens

### functions to implement interpreter commands ###

# help command
def _help(args):
    # get number of arguments in args
    argc = len(args)
    # if no arguments in the arg list, just print the list of commands
    if argc == 0:
        # build list of commands (_CNAME only) and sort; return as string
        clist = []
        for ent in _COMMAND_LIST.values():
            # add indent to each string (4 spaces)
            clist.append("    " + ent[_CNAME])
        clist.sort()
        clist = "\n".join(clist)
        print("List of commands: \n\n{0}\n\nFor info on {1}, type '{1} {1}'"
              "".format(clist, C_HELP))
    # for one argument, try to find the help blurb if it is a known command
    elif argc == 1:
        # key to _COMMAND_LIST
        ckey = None
        # try to get the single argument as key to _COMMAND_LIST
        try: ckey = args[0]
        # catch any exception that occurs and return
        except (IndexError, TypeError):
            print("{0}: error: invalid arg type; string expected".format(C_HELP),
                  file = sys.stderr)
            return
        # try to see if ckey is in _COMMAND_LIST; if not error and return
        try: ckey = _COMMAND_LIST[ckey][_CNAME]
        except KeyError:
            print("{0}: error: unknown command '{1}'".format(C_HELP, ckey))
            return
        except:
            _ufatal(C_HELP)
            return
        # since it has been found, print the formatted help string
        print(_strwrap(_COMMAND_LIST[ckey][_CHELP]))
    # else too many arguments
    else:
        print("{0}: error: too many arguments. type '{0} {0}' for info on {0}."
              "".format(C_HELP))

# test command. argument list: ["test", [arg1, ...], [func_arg1, ...]]
# if the first arglist has more than one element, then there's something wrong
def _test(args):
    # get number of arguments in args
    argc = len(args)
    # if number of elements in args is less than 2, print error
    if argc < 2:
        print("{0}: error: not enough arguments. type '{1} {0}' for usage."
              "".format(C_TEST, C_HELP))
    # else if there are two lists in args
    elif argc == 2:
        # module reference, function reference
        mref = fref = None
        # try to split module and function names apart
        refs = args[0][0].split(".")
        # if there are not exactly two arguments, print error and exit
        if len(refs) != 2:
            print("{0}: error: 2 names (module, function) required, {1} "
                  "received".format(C_TEST, len(refs)))
            return
        # make refs
        mref, fref = refs
        # set absolute module name
        mref = _PACKAGE_NAME + "." + mref
        # check if the module has already been imported or not (absolute name)
        try: mref = _IMPORT_LIST[mref]
        except KeyError:
            print("{0}: loading module {1}: ".format(C_TEST, mref), end = "")
            # if it is not found, then try to to import the module
            try: mref = importlib.import_module(mref)
            except ImportError:
                print("failed\n{0}: error: unknown module '{1}'"
                      "".format(C_TEST, mref))
                return
            except:
                _ufatal(C_TEST)
                return
            # if import was successful, key mref into _IMPORT_LIST by its name
            _IMPORT_LIST[mref.__name__] = mref
            print("loaded")
        # if other error occurred during dictionary lookup
        except:
            _ufatal(C_TEST)
            return
        # check if function is in module (is attribute)
        try: fref = getattr(mref, fref)
        except AttributeError:
            print("{0}: error: function '{1}' not found in module '{2}'"
                  "".format(C_TEST, fref, mref.__name__))
            return
        except:
            _ufatal(C_TEST)
            return
        # join arguments with commas and send to eval (note: SAFETY CONCERN!)
        jargs = "(" + ", ".join(args[1]) + ")"
        print("> eval {0}.{1}{2}".format(mref.__name__, fref.__name__, jargs))
        # return value
        rval = None
        # try to execute
        try: rval = eval("mref." + fref.__name__ + jargs)
        # catch exception message and print it with exception class
        except Exception as err:
            print(_strwrap("{0}: caught {1}. message:\n{2}"
                           "".format(C_TEST, err.__class__, err)))
            return
        # else print formatted output
        print(_strwrap("> output: " + str(rval)))
    # too many arguments, so print error again
    else:
        print("{0}: error: too many arguments. type '{1} {0}' for usage."
              "".format(C_TEST, C_HELP))
    return

# info command.
def _info(args):
    # get number of arguments in args
    argc = len(args)
    # if number of elements in args is less than 1, print error
    if argc < 1:
        print("{0}: error: not enough arguments. type '{1} {0}' for usage."
              "".format(C_INFO, C_HELP))
    # else if there are one or two arguments
    elif (argc == 1) or (argc == 2):
        # if the first argument is C_INFO_SRC (module/function stuff)
        if args[0] == C_INFO_SRC:
            # if there is only one argument, print a list of the modules
            if argc == 1:
                # get module info for all modules in the package
                modinfo = list(pkgutil.iter_modules([_PACKAGE_PATH +
                                                     _PACKAGE_NAME]))
                # for each module, get its indented name and load status
                for i in range(len(modinfo)):
                    ment = modinfo[i][1]
                    # check if this module has been loaded already
                    try:
                        _ = _IMPORT_LIST[_PACKAGE_NAME + "." + ment]
                        # 5 spaces, then 6 spaces
                        ment = "     True      " + ment
                    except KeyError:
                        # 5 spaces, then 5 spaces
                        ment = "     False     " + ment
                    except:
                        _ufatal(C_INFO)
                        return
                    modinfo[i] = ment
                # sort the list and join by newline
                modinfo.sort()
                modlist = "\n".join(modinfo)
                # print out list of modules, including load status
                print("List of modules:\n\n    loaded?\n{0}".format(modlist))
            # else there are two arguments, so try to retrieve info on the
            # requested function/module
            else:
                # module reference, function reference
                mref = fref = None
                # try to split module and function names apart
                refs = args[1].split(".")
                # set absolute module name
                mref = _PACKAGE_NAME + "." + refs[0]
                # check if the module has been imported or not (same method
                # as in the test function that we implemented)
                try: mref = _IMPORT_LIST[mref]
                # if key error, then we have to load it
                except KeyError:
                    print("{0}: loading module {1}: ".format(C_INFO, mref),
                          end = "")
                    # try to import the module and catch any errors
                    try: mref = importlib.import_module(mref)
                    except ImportError:
                        print("failed\n{0}: error: unknown module '{1}'"
                              "".format(C_INFO, mref))
                        return
                    except:
                        _ufatal(C_INFO)
                        return
                    # if import was successful, key mref into _IMPORT_LIST by
                    # its absolute name
                    _IMPORT_LIST[mref.__name__] = mref
                    print("loaded")
                # handles any other dictionary lookup error
                except:
                    _ufatal(C_INFO)
                    return
                # if we get to this point, then mref points to the loaded module
                # if there is only one element in refs, then we care only about
                # the module, and we return the list of functions associated
                if len(refs) == 1:
                    flist = inspect.getmembers(mref, inspect.isfunction)
                    # for each (name, function pointer) tuple, we extract the
                    # name and the function signature using inspect
                    for i in range(len(flist)):
                        # append 4 spaces as indent too
                        flist[i] = "    " + flist[i][0] + str(
                            inspect.signature(flist[i][1]))
                    # sort and join by newline
                    flist.sort()
                    flist = "\n".join(flist)
                    # print out the wrapped list of functions in the module
                    print(_strwrap("List of functions in module {0}:\n\n{1}\n"
                          "".format(mref.__name__, flist)))
                # else if there are two elements, then this is a function
                elif len(refs) == 2:
                    fref = refs[1]
                    # try to see if this function exists or now
                    try: fref = getattr(mref, fref)
                    # if this is not an attribute of the module
                    except AttributeError:
                        print("{0}: function '{1}' not found in module '{2}'"
                              "".format(C_INFO, fref, mref.__name__))
                        return
                    except:
                        _ufatal(C_INFO)
                        return
                    # print function signature and docstring (if any)
                    fdoc = fref.__doc__
                    if fdoc.strip() == "":
                        fdoc = "\nNo docstring associated with function {0}\n"
                        "".format(fref.__name__)
                    print("Info on function {0} in module {1}:\n\n{0}{2}{3}"
                          "".format(fref.__name__, mref.__name__,
                                    str(inspect.signature(fref)), fdoc))
                # else introspection error; can only introspect to module or
                # function level, not any deeper than that
                else:
                    print("{0}: error: cannot introspect beyond function level"
                          "".format(C_INFO))
                    return
        # else if the first argument is C_INFO_INP (input example stuff)
        elif args[0] == C_INFO_INP:
            # if there is only one argument
            if argc == 1:
                # get sorted list from _INPUT_LIST keys and add 4-space indents
                ilist = sorted(list(_INPUT_LIST.keys()))
                for i in range(len(ilist)):
                    ilist[i] = "    " + ilist[i]
                # join by newline
                ilist = "\n".join(ilist)
                # print out list of sample inputs
                print("List of sample inputs:\n\n{0}".format(ilist))
            # else there are two arguments, so try to retrieve the requested
            # example input
            else:
                # try to find the dictionary entry by key
                ient = args[1]
                try: ient = _INPUT_LIST[ient]
                except KeyError:
                    print("{0}: error: sample input '{1}' not in input list"
                          "".format(C_INFO, ient))
                    return
                except:
                    _ufatal(C_INFO)
                    return
                # if successful, print info and view
                print(_strwrap("Info on sample input {0}:\n\n{1}"
                      "".format(ient[_ENAME], ient[_EBLURB])))
        # else unknown subcommand, so print error and exit
        else:
            print("{0}: error: unknown subcommmand '{1}' type '{2} {0}' for "
                  "usage.".format(C_INFO, args[0], C_HELP))
            return
        # if there was only one argument, print this line too
        if argc == 1:
            print("\nFor info on {0}, type '{1} {0}'".format(C_INFO, C_HELP))
    # too many arguments, so print error again
    else:
        print("{0}: error: too many arguments. type '{1} {0}' for usage."
              "".format(C_INFO, C_HELP))
    return

# main
if __name__ == "__main__":
    # get number of args
    argc = len(sys.argv)
    # normal run if there are no args
    if argc == 1:
        pass
    # else if the single argument is the help flag
    elif (argc == 2) and (sys.argv[1] == _HELP_FLAG):
        print(_strwrap(_HELP_STR))
        quit()
    # else print error and exit
    else:
        print("{0}: error: too many arguments. type '{0} {1}' for usage."
              "".format(_PROGNAME, _HELP_FLAG), file = sys.stderr)
        quit(1)
    # old stuff for testing bfs
    src = 0
    print("graph.bfs({0}, {1},\n          get_path = True) ->\n{2}".format(
        src, u_dag01_al, graph.bfs(src, u_dag01_al, get_path = True)))
    print("graph.bfs({0}, {1},\n          is_adjm = True, get_path = True,) ->"
          "\n{2}".format(src, u_dag01_am,
                         graph.bfs(src, u_dag01_am, is_adjm = True,
                                   get_path = True)))
    #    del graph # can be used to unload a module
    print(list(inspect.getfullargspec(graph.bfs)))
    # return function pointer (callable)
    thismodule = graph
    print(getattr(thismodule, "bfs")(src, u_dag01_al, get_path = True))
    print(str(inspect.signature(graph.bfs)).strip("()"))
    # print some informative message here

    # if the package is not in the same directory, print error and exit
    if os.path.isdir(_PACKAGE_PATH + _PACKAGE_NAME) == False:
        print(_strwrap("{0}: fatal error: is is required that package {1} and "
                       "{0} be located in the same directory."
                       "".format(_PROGNAME, _PACKAGE_NAME)), file = sys.stderr)
        quit(1)
    # main interpreter line
    while True:
        # prompt for input, save to string, parse arguments (crudely)
        arglist = _argsplit(input("$ "))
        # if line is empty, continue loop
        if len(arglist) == 0: continue
        # else check if the first argument is in _COMMAND_LIST
        try: arglist[0] = _COMMAND_LIST[arglist[0]][_CNAME]
        # if not, print error and continue loop
        except KeyError:
            print("{0}: unknown command '{1}'. type '{2}' for command list."
                  "".format(_PROGNAME, arglist[0], C_HELP))
            continue
        # if the command is C_EXIT or C_QUIT, exit if there are no extra args
        if (arglist[0] == C_EXIT) or (arglist[0] == C_QUIT):
            if len(arglist) > 1:
                print("{0}: extraneous arguments after exit command\n"
                      "".format(_PROGNAME))
                continue
            # else just quit
            quit()
        # else if the command is the help command, pass its args to _help()
        elif arglist[0] == C_HELP: _help(arglist[1:])
        # else if the command is the test command
        elif arglist[0] == C_TEST: _test(arglist[1:])
            # else if the command is the info command
        elif arglist[0] == C_INFO: _info(arglist[1:])
