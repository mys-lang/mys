#include "mys/memory.hpp"

namespace mys {

#ifdef MYS_MEMORY_STATISTICS
long long number_of_allocated_objects = 0;
long long number_of_object_decrements = 0;
long long number_of_object_frees = 0;
#endif

}
