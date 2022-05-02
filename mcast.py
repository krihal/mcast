import binascii
import getopt
import socket
import sys


def usage():
    name = sys.argv[0]
    print(
        f"Usage: {name} -g <group 244.1.1.1>  -p <port 1234> -t <ttl 2> -s or -c")
    print(f"       echo test | {name} -g 224.1.1.1 -p 1234 -t 20 -s")
    print(f"       {name} -g 224.1.1.1 -p 1234 -c")
    sys.exit(0)


def run_server(group, port, ttl):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    print("Sending...")

    try:
        for line in sys.stdin:
            sock.sendto(str.encode(line), (group, port))
    except KeyboardInterrupt:
        print("Bye!")
        sys.exit(0)


def run_client(group, port, ttl):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except AttributeError:
        pass

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    sock.bind((group, port))

    host = socket.gethostbyname(socket.gethostname())
    sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,
                    socket.inet_aton(host))
    sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                    socket.inet_aton(group) + socket.inet_aton(host))

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            data_len = int(len(data))
            got_from = addr[0] + ":" + str(addr[1])
        except socket.error as e:
            hexdata = binascii.hexlify(data)

            print(f"Expection: {e}")
            print("Data = %s" % hexdata)
        except KeyboardInterrupt:
            print("Bye!")
            sys.exit(0)

        print(f"Got {data_len} bytes from {got_from}")


def main(argv):
    group = None
    port = None
    ttl = 255

    server = False
    client = False

    try:
        opts, args = getopt.getopt(argv, "g: p: t: h s c")
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt == "-g":
            group = arg
        if opt == "-p":
            try:
                port = int(arg)
            except ValueError:
                usage()
        if opt == "-t":
            try:
                ttl = int(arg)
            except ValueError:
                usage()
        if opt == "-h":
            usage()
        if opt == "-s":
            server = True
        if opt == "-c":
            client = True

    if not group or not port:
        usage()
    if server and client:
        usage()

    if server:
        run_server(group, port, ttl)

    if client:
        run_client(group, port, ttl)


if __name__ == "__main__":
    main(sys.argv[1:])
