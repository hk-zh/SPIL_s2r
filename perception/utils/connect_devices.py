import pyrealsense2 as rs

connected_devices = []
realsense_ctx = rs.context()
# get serial numbers of connected devices:
for i in range(len(realsense_ctx.devices)):
    detected_camera = realsense_ctx.devices[i].get_info(
        rs.camera_info.serial_number)
    connected_devices.append(detected_camera)
print(connected_devices)