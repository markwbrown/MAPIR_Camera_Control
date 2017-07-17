
import hid
import Connect
import MAPIR_Enums
path = Connect.connect_Kernel()

buf = [0] * 512
buf[0] = 3
buf[1] = 13
buf[2] = 1

dev = hid.device()
dev.open_path(path)
q = dev.write(buf)
dev.close()