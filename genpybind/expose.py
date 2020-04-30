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
        module,  # type: Text
        doc=None,  # type: Optional[Text]
        isystem=None,  # type: Optional[List[Text]]
        includes=None,  # type: Optional[List[Text]]
        tags=None,  # type: Optional[List[Text]]
):
    # type: (...) -> Text
    tpl = textwrap.dedent("""
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

    template <typename T>
    py::object genpybind_get_type_object()
    {{
        auto tinfo = py::detail::get_type_info(
            typeid(T), /*throw_if_missing=*/true);
        return py::reinterpret_borrow<py::object>((PyObject*)tinfo->type);
    }}

    {functions}

    PYBIND11_MODULE({module}, {var}) {{
    {var}.doc() = {doc};
    {statements}
    }}
    """).strip()

    var = "m"
    registry = Registry(tags=tags)

    toplevel_index = 0
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
        function = "\n".join(s for s in statements)
        functions_prefix.append(
            "void function_{}(py::module& m)".format(toplevel_index) + "\n{\nstatic_cast<void>(m);\n")
        functions.append(function)
        toplevel_index += 1
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
            if line.startswith("auto {}".format(name)):
                args = line.split('=')[1].split('(')[1].split(')')[0].split(', ')
                if args[0] == 'm':
                    parent_names = [args[1]] + parent_names
                    return parent_names
                else:
                    parent_names = [args[1]] + parent_names
                    return find_recursive_attribute(args[0], lines, parent_names)
        raise Exception("Did not find definition of {}".format(name))

    for i in range(len(statements)):
        lines = statements[i].split('\n')
        l = 0
        for line in lines:
            global_type = line.split('.')[0]
            if global_type.startswith("genpybind") and not line.split('.')[1].startswith("attr"):
                # non-attr can be reordered, do it
                for f in range(len(functions)):
                    if functions[f].find(global_type) != -1:
                        print("/* non-attr: {} */".format(line))
                        functions[f] = functions[f] + "\n" + line + "\n"
                        lines.remove(line)
            if global_type.startswith("genpybind") and line.split('.')[1].startswith("attr"):
                # attr can't be reordered, make it use the module to get the object
                parent_names = find_recursive_attribute(global_type, ("\n".join(functions)).split("\n"))
                assert parent_names is not None
                print("/* attr: {} */".format(parent_names))
                split = line.split('.')
                # FIXME: nesting of types not working
                split[0] = "m" + "".join([".attr({})".format(attr) for attr in parent_names])
                lines[l] = ".".join(split)
            l += 1
        statements[i] = "\n".join(lines)

    for i in range(toplevel_index):
        functions[i] = functions_prefix[i] + functions[i] + "\n}\n"

    statements = ["function_{}(m);".format(i) for i in range(toplevel_index)] + statements

    return tpl.format(
        module=module,
        name=quote(module),
        doc=quote(doc),
        isystem="\n".join('#include <{}>'.format(f) for f in isystem or []),
        includes="\n".join('#include {}'.format(quote(f)) for f in includes or []),
        var=var,
        functions="\n".join(function for function in functions),
        statements="\n".join(statements)
    )
