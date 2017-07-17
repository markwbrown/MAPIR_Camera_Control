import sys
import hid
import Connect
import MAPIR_Enums
shutterlist = ["1/32000",
 "1/16000",
 "1/8000",
 "1/6000",
 "1/4000",
 "1/2000",
 "1/1600",
 "1/1250",
 "1/1000",
 "1/800",
 "1/640",
 "1/500",
 "1/400",
 "1/320",
 "1/250",
 "1/200",
 "1/160",
 "1/125",
 "1/100",
 "1/80",
 "1/60",
 "1/50",
 "1/40",
 "1/30",
 "1/25",
 "1/20",
 "1/15",
 "1/12",
 "1/10",
 "1/8",
 "1/6.4",
 "1/5",
 "1/4",
 "1/3.2",
 "1/2.5",
 "1/2",
 "1"]
path = Connect.connect_Kernel()
if sys.argv[1] == '-l':
    for count, shut in enumerate(shutterlist):
        print(count + ". " + shut)
else:
    SHUTTER = int(sys.argv[1])
    buf = [0] * 512
    buf[0] = 5
    buf[1] = 111
    buf[2] = SHUTTER

    dev = hid.device()
    dev.open_path(path)
    q = dev.write(buf)
    dev.close()