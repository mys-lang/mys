SRCS += src/pcre2_auto_possess.c
SRCS += src/pcre2_chartables.c
SRCS += src/pcre2_compile.c
SRCS += src/pcre2_config.c
SRCS += src/pcre2_context.c
SRCS += src/pcre2_convert.c
SRCS += src/pcre2_dfa_match.c
SRCS += src/pcre2_error.c
SRCS += src/pcre2_extuni.c
SRCS += src/pcre2_find_bracket.c
SRCS += src/pcre2_jit_compile.c
SRCS += src/pcre2_maketables.c
SRCS += src/pcre2_match.c
SRCS += src/pcre2_match_data.c
SRCS += src/pcre2_newline.c
SRCS += src/pcre2_ord2utf.c
SRCS += src/pcre2_pattern_info.c
SRCS += src/pcre2_script_run.c
SRCS += src/pcre2_serialize.c
SRCS += src/pcre2_string_utils.c
SRCS += src/pcre2_study.c
SRCS += src/pcre2_substitute.c
SRCS += src/pcre2_substring.c
SRCS += src/pcre2_tables.c
SRCS += src/pcre2_ucd.c
SRCS += src/pcre2_valid_utf.c
SRCS += src/pcre2_xclass.c

OBJS = $(SRCS:%.c=%.o)

LIB = libpcre2.a

CFLAGS += -Iinclude
CFLAGS += -DHAVE_CONFIG_H
CFLAGS += -DPCRE2_CODE_UNIT_WIDTH=32
CFLAGS += -O2
CFLAGS += -ffunction-sections
CFLAGS += -fdata-sections
# CFLAGS += -flto

all: $(LIB)

$(LIB): $(OBJS)
	ar -r $@ $^

clean:
	rm -f $(LIB) $(OBJS)
