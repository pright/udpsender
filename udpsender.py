#!/usr/bin/env python

import sys
import getopt
import os
import time
import socket
import threading
import select


TIME_SLICE = 0.1  # seconds


class Sender(threading.Thread):

    def __init__(self,
                 fname,
                 addr,
                 loop=False,
                 psize=1316,
                 bitrate=4 * 1024 * 1024):
        super(Sender, self).__init__()
        self.fname = fname
        self.addr = addr
        self.loop = loop
        self.psize = psize
        self.bitrate = bitrate

        print 'File name: ', self.fname
        ip, port = self.addr
        print 'IP: ', ip
        print 'Port: ', port
        print 'Loop: ', self.loop
        print 'Packet size: ', self.psize
        print 'Bit rate: ', self.bitrate
        print ''
        self.skip_send = False
        self.exit = False

    def run(self):
        global TIME_SLICE
        try:
            if self.fname is None:
                f = sys.stdin
            else:
                f = open(self.fname, 'r')
        except IOError as err:
            print 'Exception: ', err
            return

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        byterate = self.bitrate / 8
        bps = byterate * TIME_SLICE  # bps = bytes_per_slice
        pps = int(round(bps / self.psize))  # pps = packets_per_slice

        if pps <= 1:
            pack_rate = float(byterate) / self.psize
            TIME_SLICE = 1 / pack_rate
            pps = 1

        count = 0
        while not self.exit:
            if not count:
                start_time = time.clock()

            if self.fname is None:
                if select.select([f], [], [], TIME_SLICE)[0]:
                    data = f.read(self.psize)
                else:
                    continue
            else:
                data = f.read(self.psize)

            if not len(data):
                if self.loop:
                    f.seek(0)
                    continue
                else:
                    break

            if not self.skip_send:
                try:
                    s.sendto(data, self.addr)
                except Exception as e:
                    print str(e)

            count += 1
            if count == pps:
                count = 0

                cur_time = time.clock()
                send_time = cur_time - start_time
                wait_time = TIME_SLICE - send_time
                if wait_time > 0:
                    time.sleep(wait_time)

                # print 's', send_time
                # print 'w', wait_time

        s.close()
        f.close()

    def stop(self):
        self.exit = True

    def skip(self):
        self.skip_send = True

    def resume(self):
        self.skip_send = False


def usage():
    str = '''\
    Usage:   udpsender.py [opts] [ip][:port]
    Options:
        -h, --help:                     Show this usage info.

        -i file, --input=file:          Reads data to be transmitted from file.
                                        If this parameter is not supplied,
                                        data to be transmitted is read from stdin
                                        instead.

        -l, --loop:                     Send file in loop mode.

        -p packSize, --pack=packSize:   Choose the packet size. Default is 1316.

        -b bitrate, --bitrate=bitrate:  Limits bandwidth used by udpsender.
                                        Bitrate may be expressed in bits per 
                                        second(-b 20000000), kilobits per 
                                        second(-b 20000k) or megabits per 
                                        second(-b 20m).

        ip:                             Use the given ip address for sending the 
                                        data. Default is 224.222.222.222.

        port:                           Use the given port for sending the data.
                                        Default is 36300.
    '''

    print str


def main():
    fname = None
    ip = '224.222.222.222'
    port = 36300
    loop = False
    pack = 1316
    bitrate = 4 * 1024 * 1024

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'hi:lp:b:',
                                   ['help', 'input=', 'loop', 'pack=', 'bitrate='])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(1)

    for o, v in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-i', '--input'):
            fname = v
        elif o in ('-l', '--loop'):
            loop = True
        elif o in ('-p', '--pack'):
            pack = int(v)
        elif o in ('-b', '--bitrate'):
            if v[-1] in ('m', 'M'):
                bitrate = float(v[:-1]) * 1024 * 1024
            elif v[-1] in ('k', 'K'):
                bitrate = float(v[:-1]) * 1024
            elif v:
                bitrate = float(v)
        else:
            usage()
            sys.exit(2)

    if fname is None:
        loop = False

    if len(args) > 1:
        usage()
        sys.exit(3)
    elif len(args) == 1:
        if ':' in args[0]:
            ip, port = args[0].split(':')
            port = int(port)
        else:
            ip = args[0]

    s = Sender(fname, (ip, port), loop, pack, bitrate)
    s.start()

    try:
        while True:
            s.join(float(TIME_SLICE) / 1000)
            time.sleep(0.1)
            if not s.is_alive():
                break
    except KeyboardInterrupt:
        s.stop()

if __name__ == '__main__':
    main()
