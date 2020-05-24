from __future__ import unicode_literals

import textwrap


from . import utils
from .registry import Registry
from .utils import quote

if False:  # pylint: disable=using-constant-test
    from .decls.declarations import Declaration  # pylint: disable=unused-import
    from typing import (  # pylint: disable=unused-import
        List, Optional, Text, Tuple, Union)


def expose_as(
        toplevel_declarations,  # type: List[Declaration]
        output_files,  # type: List[Text]
        module,  # type: Text
        doc=None,  # type: Optional[Text]
        isystem=None,  # type: Optional[List[Text]]
        includes=None,  # type: Optional[List[Text]]
        tags=None,  # type: Optional[List[Text]]
):
    # type: (...) -> Text
    tpl = textwrap.dedent("""
    #ifndef __GENPYBIND_GENERATED__
    #define __GENPYBIND_GENERATED__
    #endif

    #include <sstream>
    #include <pybind11/pybind11.h>
    #include <pybind11/stl.h>
    {isystem}

    {includes}

    namespace py = pybind11;

    template <typename T>
    struct genpybind_stringstream_helper
    {{
        std::string operator()(T const& value) const {{
            std::stringstream tmp;
            tmp << value;
            return tmp.str();
        }}
    }};

    // If `T` is registered with pybind11 the corresponding Python type is returned.
    // Else a warning is emitted and None is returned.
    template <typename T>
    py::object genpybind_get_type_object() {{
        std::type_info const &tp = typeid(T);
        auto tinfo = py::detail::get_type_info(tp, /*throw_if_missing=*/false);
        if (!tinfo) {{
            std::string name = tp.name();
            py::detail::clean_type_id(name);
            PyErr_WarnFormat(PyExc_Warning, /*stack_level=*/7,
                             "Reference to unknown type '%s'", name.c_str());
            return pybind11::none();
        }}
        return py::reinterpret_borrow<py::object>((PyObject *)tinfo->type);
    }}

    {functions}
    {function_declarations}

    PYBIND11_MODULE({module}, {var}) {{
    {var}.doc() = {doc};
    {statements}
    }}
    """).strip()

    split_tpl = textwrap.dedent("""
    #ifndef __GENPYBIND_GENERATED__
    #define __GENPYBIND_GENERATED__
    #endif

    #include <sstream>
    #include <pybind11/pybind11.h>
    #include <pybind11/stl.h>
    {isystem}

    {includes}

    namespace py = pybind11;

    template <typename T>
    struct genpybind_stringstream_helper
    {{
        inline std::string operator()(T const& value) const {{
            std::stringstream tmp;
            tmp << value;
            return tmp.str();
        }}
    }};

    template <typename T>
    inline py::object genpybind_get_type_object()
    {{
        auto tinfo = py::detail::get_type_info(
            typeid(T), /*throw_if_missing=*/true);
        return py::reinterpret_borrow<py::object>((PyObject*)tinfo->type);
    }}

    {functions}
    """).strip()

    var = "m"
    registry = Registry(tags=tags)

    statements = []  # type: List[Text]
    pending_declarations = []  # type: List[Tuple[Declaration, Text]]
    postamble_declarations = []  # type: List[Tuple[Declaration, Text]]
    functions = []
    functions_prefix= []

    def handle_return(declaration, value, postamble_only=False):
        # type: (Declaration, Union[None, Text, Tuple[Declaration, Text]], bool) -> None
        """
        expose() may either yield a string containing a statement to be emitted or
        a pair of a declaration and the identifier of the parent scope to use.
        In the latter case it will be added to a list of pending declarations on which
        expose_later() is called after all other normal declarations have been processed.
        If in addition the returned declaration has a truthy "postamble" attribute, it
        will be processed even later.
        """
        if value is None:
            return
        if not isinstance(value, tuple):
            assert utils.is_string(value)
            statements.append(value)
            return
        declaration, _ = value
        is_postamble = getattr(declaration, "postamble", None)
        if postamble_only or is_postamble:
            postamble_declarations.append(value)
            return
        pending_declarations.append(value)

    for declaration in toplevel_declarations:
        for value in utils.flatten(declaration.expose(var, registry)):
            handle_return(declaration, value)
        function = "\n".join(statements)
        if function.strip():
            functions.append(function)
        statements = []

    while pending_declarations:
        declaration, parent = pending_declarations.pop(0)
        for value in utils.flatten(declaration.expose_later(var, parent, registry)):
            handle_return(declaration, value)

    while postamble_declarations:
        declaration, parent = postamble_declarations.pop(0)
        for value in utils.flatten(declaration.expose_later(var, parent, registry)):
            handle_return(declaration, value, postamble_only=True)

    def find_recursive_attribute(name, lines, parent_names = []):
        for line in lines:
            # find definition
            if line.startswith("auto {}".format(name)):
                args = line.split('=')[1].split('(')[1].split(')')[0].split(', ')
                if args[0] == var:
                    # found outmost parent
                    return [args[1]] + parent_names
                else:
                    # not yet found outmost parent
                    return find_recursive_attribute(args[0], lines, [args[1]] + parent_names)
        raise Exception("Did not find definition of {}".format(name))

    def is_attr(line):
      return line.split('.')[1].startswith("attr")

    remaining_statements = []
    functions_appends = ["" for i in range(len(functions))]
    for statement in statements:
        lines = statement.split('\n')
        remaining_lines = []
        for line in lines:
            name = line.split('.')[0]
            if line.startswith("genpybind"):
                if is_attr(line):
                    # attr can't be reordered, make it use the module to get the object
                    parent_names = find_recursive_attribute(name, ("\n".join(functions)).split("\n"))
                    split = line.split('.')
                    split[0] = var + "".join([".attr({})".format(attr) for attr in parent_names])
                    remaining_lines.append(".".join(split))
                else:
                    found = False
                    # non-attr can be reordered into function defining symbol, do it
                    for f, function in enumerate(functions):
                        if function.find(name) != -1:
                            functions_appends[f] += line + "\n"
                            found = True
                            break
                    if not found:
                        remaining_lines.append(line)
            else:
                remaining_lines.append(line)
        remaining_statements.append("\n".join(remaining_lines))

    functions = [functions[i] + "\n" + functions_appends[i] for i in range(len(functions))]

    # find undefined py::module uses
    # first find all module definitions, record and remove them
    modules = []
    module_names = []
    module_definitions = []
    for f in range(len(functions)):
        for line in functions[f].split('\n'):
            if line.startswith("py::module"):
                modules.append(line.split(' ')[1])
                module_names.append(line.split('"')[1])
                module_definitions.append(line)
                functions[f] = functions[f].replace(line, "")

    # prepend dynamic acquisition of used but not defined module
    for m, name in zip(modules, module_names):
        for f in range(len(functions)):
            if functions[f].find(m) != -1:
                functions[f] = "auto {} = static_cast<py::module>({}.attr(\"{}\"));\n".format(
                    m, var, name) + functions[f]


    function_def = "void function_{}(py::module& {})\n{{\n{}\n}}\n"
    function_decl = "void function_{}(py::module&);"
    function_call = "function_{}({});"

    functions = [function_def.format(i, var, functions[i]) for i in range(len(functions))]
    remaining_statements = [function_call.format(i, var) for i in range(len(functions))] + \
        remaining_statements
    function_declarations = [function_decl.format(i) for i in range(len(functions))]

    # split functions such that the linecount-difference is smaller than max(linecounts)
    functions_linecounts = [f.count('\n') for f in functions]
    if len(functions): # FIXME: needs redesign, as not pretty
        functions_linecounts, functions = map(list, zip(*sorted(zip(functions_linecounts, functions))))
    split_functions = [[] for i in range(len(output_files))]
    split_functions_linecounts = [0] * len(output_files)
    for function, function_linecount in zip(reversed(functions), reversed(functions_linecounts)):
        to_index = split_functions_linecounts.index(min(split_functions_linecounts))
        split_functions[to_index].append(function)
        split_functions_linecounts[to_index] += function_linecount
    # sort split_functions in order to have PYBIND11_MODULE in first file with minimal line count
    split_functions_linecounts, split_functions = map(list, zip(*sorted(zip(split_functions_linecounts, split_functions))))

    # prepend remaining statements with module definitions
    remaining_statements = module_definitions + remaining_statements

    print(tpl.format(
        module=module,
        name=quote(module),
        doc=quote(doc),
        isystem="\n".join('#include <{}>'.format(f) for f in isystem or []),
        includes="\n".join('#include {}'.format(quote(f)) for f in includes or []),
        var=var,
        functions="\n".join(split_functions[0]),
        function_declarations="\n".join(function_declarations),
        statements="\n".join(remaining_statements)
    ), file=open(output_files[0], 'w'))

    for i, output_file in enumerate(output_files[1:]):
        print(split_tpl.format(
            isystem="\n".join('#include <{}>'.format(f) for f in isystem or []),
            includes="\n".join('#include {}'.format(quote(f)) for f in includes or []),
            functions="\n".join(split_functions[i + 1])
        ), file=open(output_file, 'w'))
