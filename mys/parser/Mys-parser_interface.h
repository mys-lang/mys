#ifndef Mys_Py_PEGENINTERFACE
#define Mys_Py_PEGENINTERFACE
#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "Mys-pyarena.h"

#ifndef Py_LIMITED_API
PyAPI_FUNC(struct _mod *) Mys_PyParser_ASTFromStringObject(
    const char *str,
    PyObject* filename,
    int mode,
    PyCompilerFlags *flags,
    Mys_PyArena *arena);
#endif /* !Py_LIMITED_API */

#ifdef __cplusplus
}
#endif
#endif /* !Py_PEGENINTERFACE */
