#pragma once

namespace mys {

#if defined(MYS_TRACEBACK)
#    define __MYS_TRACEBACK_INIT()                              \
    mys::TracebackEntry __traceback_entry;                      \
    __traceback_entry.info_p = &__traceback_module_info;        \
    mys::traceback_tail_p->next_p = &__traceback_entry;         \
    mys::traceback_tail_p = &__traceback_entry;

#    define __MYS_TRACEBACK_SET(index_)         \
    mys::traceback_tail_p = &__traceback_entry; \
    __traceback_entry.index = index_;
#else
#    define __MYS_TRACEBACK_INIT()
#    define __MYS_TRACEBACK_SET(index_)
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
};

extern TracebackEntry *traceback_head_p;
extern TracebackEntry *traceback_tail_p;

}
