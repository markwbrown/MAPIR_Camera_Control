import hid


def connect_Kernel():
    all_cameras = hid.enumerate(0x525, 0xa4ac)
    if all_cameras == []:
        print("Unable to locate device. Please make sure the device is connected and try again.")
    return all_cameras[0]['path']

