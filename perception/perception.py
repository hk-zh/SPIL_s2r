import cv2
import numpy as np
import pyrealsense2 as rs
import torch

from .utils.utils import instantiate_transforms, instantiate_transforms_imshow

# device list
DEVICE_NAME_LIST = ["gripper", "static"]
CONNECTED_DEVICES = {
    DEVICE_NAME_LIST[0]:
        {
            'id': '213322072488',
            'transform':
                {
                    'crop': (480, 480),
                    'shift': (0, 0),
                    'resize': (84, 84),
                    'flip':
                        {
                            'dims': (1, 2),
                            'flip': True
                        },
                    'normalize':
                        {
                            'mean': [0.48145466, 0.4578275, 0.40821073],
                            'std': [0.26862954, 0.26130258, 0.27577711]
                        }
                }
        },
    DEVICE_NAME_LIST[1]:
        {
            'id': '207222072877',
            'transform':
                {
                    'crop': (480, 480),
                    'shift': (0, 0),
                    'resize': (200, 200),
                    'flip':
                        {
                            'dims': 1,
                            'flip': False
                        },
                    'normalize':
                        {
                            'mean': [0.48145466, 0.4578275, 0.40821073],
                            'std': [0.26862954, 0.26130258, 0.27577711]
                        }
                }
        }
}



class Perception:
    def __init__(self, device_name):
        realsense_ctx = rs.context()
        # The context encapsulates all the devices and sensors, and provides some additional functionalities.

        # Configure depth and color streams
        self.pipeline = []
        self.config = []
        for i in range(len(realsense_ctx.devices)):
            self.pipeline.append(rs.pipeline())  # one pipeline for each device
            self.config.append(rs.config())  # one config for each device
            self.config[i].enable_device(CONNECTED_DEVICES[DEVICE_NAME_LIST[i]]['id'])

            # Get device product line for setting a supporting resolution
            pipeline_wrapper = rs.pipeline_wrapper(self.pipeline[i])
            pipeline_profile = self.config[i].resolve(pipeline_wrapper)
            device = pipeline_profile.get_device()
            device_product_line = str(device.get_info(rs.camera_info.product_line))

            self.config[i].enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

            if device_product_line == 'L500':
                self.config[i].enable_stream(rs.stream.color, 960, 540, rs.format.rgb8, 30)
            else:
                self.config[i].enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)

        self.classes = [[], [], [], []]
        self.device_name = device_name
        self.transform_data = CONNECTED_DEVICES[device_name]['transform']
        self.transform = instantiate_transforms(self.transform_data)
        self.transform_imshow = instantiate_transforms_imshow(self.transform_data)

    def pipeline_start(self):
        index = DEVICE_NAME_LIST.index(self.device_name)
        self.pipeline[index].start(self.config[index])
        for i in range(50):
            self.pipeline[index].wait_for_frames()

    def pipeline_close(self):
        index = DEVICE_NAME_LIST.index(self.device_name)
        self.pipeline[index].stop()

    def _get_raw_img(self):
        index = DEVICE_NAME_LIST.index(self.device_name)
        frames = self.pipeline[index].wait_for_frames()
        align = rs.align(rs.stream.color)
        frames = align.process(frames)
        color_frame = frames.get_color_frame()
        img = np.asanyarray(color_frame.get_data())
        return img

    def streaming(self):
        img = self._get_raw_img()
        img = torch.from_numpy(img).byte().permute([2, 0, 1])
        img = self.transform_imshow(img)
        cv2.namedWindow(self.device_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.device_name, 600, 600)
        img_rgb = img.permute([1, 2, 0]).numpy()
        im_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        cv2.imshow(self.device_name, im_bgr)
        cv2.waitKey(10)

    def get_current_img(self):
        img = self._get_raw_img().copy()
        img = torch.from_numpy(img).byte().permute([2, 0, 1])
        img = self.transform(img)
        return img

    def get_current_obs(self):
        img = self.get_current_img()
        # cv2.namedWindow(self.device_name, cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(self.device_name, 600, 600)
        # cv2.imshow(self.device_name, img)
        # cv2.waitKey(10)
        return img[None, None, :]  # batch size, sequence length dimension


if __name__ == '__main__':
    camera1 = Perception(device_name='gripper')
    camera2 = Perception(device_name='static')
    camera1.pipeline_start()
    camera2.pipeline_start()
    try:
        while True:
            camera1.streaming()
            camera2.streaming()
    finally:
        # camera1.pipeline_close()
        # camera2.pipeline_close()
        cv2.destroyAllWindows()
