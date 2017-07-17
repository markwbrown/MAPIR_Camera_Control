import sys
import hid
import Connect
import MAPIR_Enums
path = Connect.connect_Kernel()
ISO = int(sys.argv[1]) / 100

buf = [0] * 512
buf[0] = 5
buf[1] = 143
buf[2] = ISO

dev = hid.device()
dev.open_path(path)
q = dev.write(buf)
dev.close()