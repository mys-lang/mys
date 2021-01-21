#ifndef MYS_HPP
#define MYS_HPP

#include "mys/common.hpp"
#include "mys/utils.hpp"

// Mys defined types
#include "mys/types/number.hpp"
#include "mys/types/bool.hpp"
#include "mys/types/char.hpp"
#include "mys/types/bytes.hpp"
#include "mys/types/string.hpp"
#include "mys/types/object.hpp"
#include "mys/types/tuple.hpp"
#include "mys/types/list.hpp"
#include "mys/types/dict.hpp"
#include "mys/types/generators.hpp"
#include "mys/types/regex.hpp"

// Errors and exception management
#include "mys/errors/base.hpp"
#include "mys/errors/assertion.hpp"
#include "mys/errors/index.hpp"
#include "mys/errors/key.hpp"
#include "mys/errors/none.hpp"
#include "mys/errors/not_implemented.hpp"
#include "mys/errors/system_exit.hpp"
#include "mys/errors/unreachable.hpp"
#include "mys/errors/value.hpp"

// Builtins, print, test and shared pointer functions
#include "mys/builtins.hpp"
#include "mys/test.hpp"
#include "mys/sharedptr.hpp"
#include "mys/printable/char.hpp"
#include "mys/printable/string.hpp"

#include "mys/fiber.hpp"

#endif
