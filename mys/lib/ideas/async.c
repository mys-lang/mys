/* libuv replacement ideas. */

struct udp_t {
    int fd;
};

void udp_init(struct udp_t *self_p)
{
    self_p->fd = socket(AF_INET, SOCK_DGRAM, 0);
    self_p->is_polled = false;
    self_p->is_reading = false;
}

int udp_read(struct udp_t *self_p, void *buf_p, size_t size)
{
    while (true) {
        int res = read(self_p->fd, buf_p, size);

        if (res == -1) {
            if (errno == EAGAIN) {
                if (!self_p->is_polled) {
                    epoll_ctl(mys::loop(), EPOLL_ADD, self_p->fd, self_p);
                    self_p->is_polled = true;
                }

                self_p->is_reading = true;
                mys::suspend();
                self_p->is_reading = false;
            } else {
                return -1;
            }
        } else {
            break;
        }
    }

    return 0;
}

int main()
{
    struct handle *handle_p;

    while (true) {
        int res = epoll_wait(&events);
        handle_p = (struct handle *)event.data.ptr;

        if (handle_p->is_reading) {
            handle_p->resume(handle_p);
        } else {
            epoll_ctl(EPOLL_DEL, handle_p->fd);
            handle_p->is_polled = false;
        }
    }
}
