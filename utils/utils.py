from pathlib import Path
from typing import Dict, List, Union
import os

import numpy as np


def get_all_checkpoints(experiment_folder: Path) -> List:
    if experiment_folder.is_dir():
        checkpoint_folder = experiment_folder / "saved_models"
        if checkpoint_folder.is_dir():
            checkpoints = sorted(Path(checkpoint_folder).iterdir(), key=lambda chk: chk.stat().st_mtime)
            if len(checkpoints):
                return [chk for chk in checkpoints if chk.suffix == ".ckpt"]
    return []


def get_last_checkpoint(experiment_folder: Path) -> Union[Path, None]:
    # return newest checkpoint according to creation time
    checkpoints = get_all_checkpoints(experiment_folder)
    if len(checkpoints):
        return checkpoints[-1]
    return None


def format_sftp_path(path):
    """
    When using network mount from nautilus, format path
    """
    if path.as_posix().startswith("sftp"):
        uid = os.getuid()
        path = Path(f"/run/user/{uid}/gvfs/sftp:host={path.as_posix()[6:]}")
    return path


def sim2real_frame_single(action):
    return np.array([-action[0] * 0.02,
                     -action[1] * 0.02,
                     action[2] * 0.02,
                     action[5] * 0.05,
                     action[3] * 0.05,
                     action[4] * 0.05,
                     action[6]])


def sim2real_frame(action):
    """
    convert the relative action of sim environment to real world environment
    action: numpy array form with the shape of (H, 7)
    """
    return np.stack((-action[:, 0] * 0.03,
                     action[:, 1] * 0.03,
                     -action[:, 2] * 0.035,
                     -action[:, 5] * 0.05,
                     -action[:, 3] * 0.05,
                     action[:, 4] * 0.05,
                     action[:, 6]), axis=-1)
