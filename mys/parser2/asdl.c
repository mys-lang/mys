#include <Python.h>
#include "Mys-asdl.h"

MYS_GENERATE_ASDL_SEQ_CONSTRUCTOR(generic, void*);
MYS_GENERATE_ASDL_SEQ_CONSTRUCTOR(identifier, PyObject*);
MYS_GENERATE_ASDL_SEQ_CONSTRUCTOR(int, int);
