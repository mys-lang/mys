#include "Mys-parser_interface.h"

#include "Mys-tokenizer.h"
#include "Mys-pegen.h"

mod_ty
Mys_PyParser_ASTFromStringObject(const char *str, PyObject* filename, int mode,
                            PyCompilerFlags *flags, Mys_PyArena *arena)
{
    if (PySys_Audit("compile", "yO", str, filename) < 0) {
        return NULL;
    }

    mod_ty result = _Mys_PyPegen_run_parser_from_string(str, mode, filename, flags, arena);
    return result;
}
