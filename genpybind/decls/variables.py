from clang.cindex import CursorKind

from .. import cutils
from ..utils import quote
from .declarations import Declaration


class FieldOrVar(Declaration):
    __slots__ = (
        "_writable",
    )

    def __init__(self, *args, **kwargs):
        super(FieldOrVar, self).__init__(*args, **kwargs)
        self._writable = True

    @property
    def writable(self):
        if self.is_field_or_static() and self.cursor.type.is_const_qualified():
            return False
        return self._writable

    def set_writable(self, value=True):
        if not self.is_field_or_static() and not value:
            raise RuntimeError(
                "'readonly' annotation not supported for {}".format(self))
        self._writable = bool(value)

    def set_readonly(self, value=True):
        self.set_writable(not value)

    def set_readwrite(self, value=True):
        self.set_writable(value)

    def is_field_or_static(self):
        return cutils.first_parent_by_kind(
            self.cursor, [CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL]) is not None

    def statements(self, parent, registry):
        if self.is_field_or_static():
            qualifier = "readwrite" if self.writable else "readonly"
            if self.cursor.kind == CursorKind.VAR_DECL:
                qualifier = "{}_static".format(qualifier)
            yield "{parent}.def_{qualifier}({name}, &{field});".format(
                qualifier=qualifier,
                field=self.fully_qualified_name,
                parent=parent,
                name=quote(self.expose_as),
            )
            return

        yield "{parent}.attr({name}) = {var};".format(
            parent=parent,
            name=quote(self.expose_as),
            var=self.fully_qualified_name,
        )