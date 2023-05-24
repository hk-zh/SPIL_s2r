import hydra
from pathlib import Path
import numpy as np
from .utils.utils import get_model


class Policy:
    def __init__(self, model: str):
        self.model = get_model(model)
        self.model.action_decoder.gripper_control = False # we just want the relative action
        self.skill_len = 5

    def step(self, obs, goal):
        skill = []
        for i in range(self.skill_len):
            action = self.model.step(obs, goal).numpy()
            skill.append(action)
        return np.clip(np.array(skill).squeeze(), a_min=-1., a_max=1.)

    def step2(self, obs, goal):
        action = self.model.step(obs, goal).numpy()
        return np.clip(action.squeeze(), a_max=1., a_min=-1.)

    def reset(self):
        self.model.reset()



