SRCS += src/fs-poll.c
SRCS += src/idna.c
SRCS += src/inet.c
SRCS += src/random.c
SRCS += src/strscpy.c
SRCS += src/threadpool.c
SRCS += src/timer.c
SRCS += src/uv-data-getter-setters.c
SRCS += src/uv-common.c
SRCS += src/version.c
SRCS += src/unix/async.c
SRCS += src/unix/core.c
SRCS += src/unix/dl.c
SRCS += src/unix/fs.c
SRCS += src/unix/getaddrinfo.c
SRCS += src/unix/getnameinfo.c
SRCS += src/unix/loop-watcher.c
SRCS += src/unix/loop.c
SRCS += src/unix/pipe.c
SRCS += src/unix/poll.c
SRCS += src/unix/process.c
SRCS += src/unix/random-devurandom.c
SRCS += src/unix/signal.c
SRCS += src/unix/stream.c
SRCS += src/unix/tcp.c
SRCS += src/unix/thread.c
SRCS += src/unix/tty.c
SRCS += src/unix/udp.c

ifeq ($(SYSTEM), Darwin)
SRCS += src/unix/bsd-ifaddrs.c
SRCS += src/unix/darwin-proctitle.c
SRCS += src/unix/darwin.c
SRCS += src/unix/fsevents.c
SRCS += src/unix/proctitle.c
SRCS += src/unix/kqueue.c
SRCS += src/unix/random-getentropy.c
endif

ifeq ($(SYSTEM), Linux)
SRCS += src/unix/linux-core.c
SRCS += src/unix/linux-inotify.c
SRCS += src/unix/linux-syscalls.c
SRCS += src/unix/procfs-exepath.c
SRCS += src/unix/proctitle.c
SRCS += src/unix/random-getrandom.c
SRCS += src/unix/random-sysctl-linux.c
SRCS += src/unix/epoll.c
endif

ifeq ($(SYSTEM), Cygwin)
SRCS += src/unix/cygwin.c
SRCS += src/unix/bsd-ifaddrs.c
SRCS += src/unix/no-fsevents.c
SRCS += src/unix/no-proctitle.c
SRCS += src/unix/posix-hrtime.c
SRCS += src/unix/posix-poll.c
SRCS += src/unix/procfs-exepath.c
SRCS += src/unix/sysinfo-loadavg.c
SRCS += src/unix/sysinfo-memory.c
endif

OBJS = $(SRCS:%.c=%.o)

LIB = libuv.a

CFLAGS += -Iinclude
CFLAGS += -Isrc
CFLAGS += -D_GNU_SOURCE
CFLAGS += -O2
CFLAGS += -ffunction-sections
CFLAGS += -fdata-sections
# CFLAGS += -flto

all: $(LIB)

$(LIB): $(OBJS)
	ar -r $@ $^

clean:
	rm -f $(LIB) $(OBJS)
