#ifndef Mys_Py_PEGENINTERFACE
#define Mys_Py_PEGENINTERFACE
#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "Mys-pyarena.h"

#ifndef Py_LIMITED_API
PyAPI_FUNC(struct _mod *) Mys_PyParser_ASTFromString(
    const char *str,
    const char *filename,
    int mode,
    PyCompilerFlags *flags,
    Mys_PyArena *arena);
PyAPI_FUNC(struct _mod *) Mys_PyParser_ASTFromStringObject(
    const char *str,
    PyObject* filename,
    int mode,
    PyCompilerFlags *flags,
    Mys_PyArena *arena);
PyAPI_FUNC(struct _mod *) Mys_PyParser_ASTFromFile(
    FILE *fp,
    const char *filename,
    const char* enc,
    int mode,
    const char *ps1,
    const char *ps2,
    PyCompilerFlags *flags,
    int *errcode,
    Mys_PyArena *arena);
PyAPI_FUNC(struct _mod *) Mys_PyParser_ASTFromFileObject(
    FILE *fp,
    PyObject *filename_ob,
    const char *enc,
    int mode,
    const char *ps1,
    const char *ps2,
    PyCompilerFlags *flags,
    int *errcode,
    Mys_PyArena *arena);
PyAPI_FUNC(struct _mod *) Mys_PyParser_ASTFromFilename(
    const char *filename,
    int mode,
    PyCompilerFlags *flags,
    Mys_PyArena *arena);
#endif /* !Py_LIMITED_API */

#ifdef __cplusplus
}
#endif
#endif /* !Py_PEGENINTERFACE */
