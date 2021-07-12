#pragma once

namespace mys {

#if defined(MYS_TRACEBACK)
#    define __MYS_TRACEBACK_INIT()                      \
    TracebackEntry __traceback_entry;                   \
    __traceback_entry.info_p = NULL;                    \
    __traceback_entry.next_p = NULL;                    \
    mys::traceback_bottom_p = &__traceback_entry;       \
    mys::traceback_top_p = &__traceback_entry

#    define __MYS_TRACEBACK_ENTER()                             \
    mys::TracebackEntry __traceback_entry;                      \
    __traceback_entry.info_p = &__traceback_module_info;        \
    __traceback_entry.prev_p = mys::traceback_top_p;            \
    mys::traceback_top_p->next_p = &__traceback_entry;          \
    mys::traceback_top_p = &__traceback_entry

#    define __MYS_TRACEBACK_EXIT()                      \
    mys::traceback_top_p = __traceback_entry.prev_p

#    define __MYS_TRACEBACK_SET(index_)         \
    __traceback_entry.index = index_

#    define __MYS_TRACEBACK_RESTORE()           \
    mys::traceback_top_p = &__traceback_entry
#    define __MYS_TRACEBACK_EXIT_MAIN()         \
    traceback_bottom_p = &traceback_entry;      \
    traceback_top_p = &traceback_entry
#else
#    define __MYS_TRACEBACK_INIT()
#    define __MYS_TRACEBACK_ENTER()
#    define __MYS_TRACEBACK_EXIT()
#    define __MYS_TRACEBACK_SET(index_)
#    define __MYS_TRACEBACK_RESTORE()
#    define __MYS_TRACEBACK_EXIT_MAIN()
#endif

struct TracebackEntryInfo {
    const char *name_p;
    u32 line_number;
    const char *code_p;
};

struct TracebackModuleInfo {
    const char *path_p;
    TracebackEntryInfo *entries_info_p;
};

struct TracebackEntry {
    TracebackModuleInfo *info_p;
    u32 index;
    TracebackEntry *next_p;
    TracebackEntry *prev_p;
};

extern TracebackEntry *traceback_bottom_p;
extern TracebackEntry *traceback_top_p;

}
