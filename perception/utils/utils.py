import numpy as np
import cv2
from skimage.transform import resize
import torch
from torchvision.transforms import Compose, CenterCrop, Normalize, Resize, ToTensor
from typing import Dict


class ScaleImageTensor(object):
    """
    Scale tensor of shape (B, C, H, W) containing images to [0, 1] range
    Args:
        tensor: tensor to be scaled
    Return:
        Tensor: Scaled tensor.
    """
    def __call__(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor.float().div(255)


class FlipImageTensor(object):
    """
    Flip the image according to the dimension
    Args:
        tensor: tensor to be flipped
        dim: flipping dimension
        flip: trigger to flip the image
    Return:
        processed tensor
    """
    def __init__(self, dims: int, flip: bool):
        self.dims = dims
        self.flip = flip

    def __call__(self, tensor: torch.Tensor) -> torch.Tensor:
        if self.flip:
            return tensor.flip(dims=self.dims)
        else:
            return tensor


def instantiate_transforms(transforms: Dict):
    return Compose([
                    CenterCrop(transforms['crop']),
                    Resize(transforms['resize']),
                    ScaleImageTensor(),
                    Normalize(**transforms['normalize']),
                    FlipImageTensor(**transforms['flip']),
                    ])


def instantiate_transforms_imshow(transforms: Dict):
    return Compose([
                    CenterCrop(transforms['crop']),
                    Resize(transforms['resize']),
                    ScaleImageTensor(),
                    FlipImageTensor(**transforms['flip'])
                    ])





