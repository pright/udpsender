udpsender
=========
A simple utility to send data using udp.

### Usage:

```
udpsender.py [opts] [ip][:port]
Options:
    -h, --help:                     Show this usage info.

    -i file, --input=file:          Reads data to be transmitted from file.
                                    If this parameter is not supplied,
                                    data is read from stdin instead.

    -l, --loop:                     Send file in loop mode.

    -p packSize, --pack=packSize:   Choose the packet size. Default is 1472.

    -b bitrate, --bitrate=bitrate:  Limits bandwidth used by udpsender.
                                    Bitrate may be expressed in bits per 
                                    second(-b 20000000), kilobits per 
                                    second(-b 20000k) or megabits per 
                                    second(-b 20m).

    ip:                             Use the given ip address for sending the 
                                    data. Default is 224.222.222.222.

    port:                           Use the given port for sending the data.
                                    Default is 36300.
```
