#include "Python.h"
#include <ctype.h>
#include "ast.h"

static PyObject *
builtin_compile_impl(PyObject *source,
                     PyObject *filename,
                     const char *mode,
                     int flags,
                     int dont_inherit,
                     int optimize,
                     int feature_version)
/*[clinic end generated code: output=b0c09c84f116d3d7 input=40171fb92c1d580d]*/
{
    PyObject *source_copy;
    const char *str;
    int compile_mode = -1;
    int is_ast;
    int start[] = {Py_file_input, Py_eval_input, Py_single_input, Py_func_type_input};
    PyObject *result;

    PyCompilerFlags cf = _PyCompilerFlags_INIT;
    cf.cf_flags = flags | PyCF_SOURCE_IS_UTF8;
    if (feature_version >= 0 && (flags & PyCF_ONLY_AST)) {
        cf.cf_feature_version = feature_version;
    }

    if (flags &
        ~(PyCF_MASK | PyCF_MASK_OBSOLETE | PyCF_COMPILE_MASK))
    {
        PyErr_SetString(PyExc_ValueError,
                        "compile(): unrecognised flags");
        goto error;
    }
    /* XXX Warn if (supplied_flags & PyCF_MASK_OBSOLETE) != 0? */

    if (optimize < -1 || optimize > 2) {
        PyErr_SetString(PyExc_ValueError,
                        "compile(): invalid optimize value");
        goto error;
    }

    if (!dont_inherit) {
        PyEval_MergeCompilerFlags(&cf);
    }

    if (strcmp(mode, "exec") == 0)
        compile_mode = 0;
    else if (strcmp(mode, "eval") == 0)
        compile_mode = 1;
    else if (strcmp(mode, "single") == 0)
        compile_mode = 2;
    else if (strcmp(mode, "func_type") == 0) {
        if (!(flags & PyCF_ONLY_AST)) {
            PyErr_SetString(PyExc_ValueError,
                            "compile() mode 'func_type' requires flag PyCF_ONLY_AST");
            goto error;
        }
        compile_mode = 3;
    }
    else {
        const char *msg;
        if (flags & PyCF_ONLY_AST)
            msg = "compile() mode must be 'exec', 'eval', 'single' or 'func_type'";
        else
            msg = "compile() mode must be 'exec', 'eval' or 'single'";
        PyErr_SetString(PyExc_ValueError, msg);
        goto error;
    }

    is_ast = PyAST_Check(source);
    if (is_ast == -1)
        goto error;
    if (is_ast) {
        if (flags & PyCF_ONLY_AST) {
            Py_INCREF(source);
            result = source;
        }
        else {
            PyArena *arena;
            mod_ty mod;

            arena = PyArena_New();
            if (arena == NULL)
                goto error;
            mod = PyAST_obj2mod(source, arena, compile_mode);
            if (mod == NULL) {
                PyArena_Free(arena);
                goto error;
            }
            if (!PyAST_Validate(mod)) {
                PyArena_Free(arena);
                goto error;
            }
            result = (PyObject*)PyAST_CompileObject(mod, filename,
                                                    &cf, optimize, arena);
            PyArena_Free(arena);
        }
        goto finally;
    }

    str = _Py_SourceAsString(source, "compile", "string, bytes or AST", &cf, &source_copy);
    if (str == NULL)
        goto error;

    result = Py_CompileStringObject(str, filename, start[compile_mode], &cf, optimize);

    Py_XDECREF(source_copy);
    goto finally;

error:
    result = NULL;
finally:
    Py_DECREF(filename);
    return result;
}

PyDoc_STRVAR(compile___doc__,
             "compile(source)\n"
             "--\n"
             "\n");

static PyObject *m_compile(PyObject *module_p, PyObject *args_p)
{
    PyObject *source_p;
    PyObject *filename_p;
    int res;

    res = PyArg_ParseTuple(args_p, "OO", &source_p, &filename_p);

    if (res == 0) {
        return (NULL);
    }

    return builtin_compile_impl(source_p,
                                filename_p,
                                "exec",
                                PyCF_ONLY_AST,
                                0,
                                0,
                                -1);
}

static struct PyMethodDef methods[] = {
    {
        "compile",
        (PyCFunction)m_compile,
        METH_VARARGS,
        compile___doc__
    },
    { NULL }
};

static PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "mys.parser._compile",
    .m_doc = "compile",
    .m_size = -1,
    .m_methods = methods
};

PyMODINIT_FUNC PyInit__compile(void)
{
    PyObject *module_p;

    module_p = PyModule_Create(&module);

    if (module_p == NULL) {
        return (NULL);
    }

    return (module_p);
}
