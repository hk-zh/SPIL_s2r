from control.controller import Controller
from perception.perception import Perception
from language.instruction import Instruction
from policy.policy import Policy
from frankx import Robot
import keyboard
import numpy as np
from utils.utils import sim2real_frame, sim2real_frame_single
from pynput.keyboard import Key, Listener

class Agent:
    def __init__(self, host):
        self.robot = Robot(host)
        self.controller = Controller(self.robot)
        try:
            self.gripper_obs = Perception(device_name='gripper')
            self.static_obs = Perception(device_name='static')
        except Exception:
            print('Cameras not found')
        self.instruction = Instruction()
        self.policy = Policy(model='SPIL')
        self.ep_len = 48
        self.setup()

    def setup(self):
        # Set up the velocity acceleration jerk
        self.robot.velocity_rel = 0.05
        self.robot.acceleration_rel = 0.01
        self.robot.jerk_rel = 0.02
        self.gripper_obs.pipeline_start()
        self.static_obs.pipeline_start()

    @staticmethod
    def _process_obs(static_obs, gripper_obs):
        return {
                    'rgb_obs': {
                        'rgb_static': static_obs,
                        'rgb_gripper': gripper_obs
                    },
                    'depth_obs': {},
                    'robot_obs': {},
                    'robot_obs_raw': {}
                }
        # we set depth_obs, robot_obs, robot_obs_raw to None since we don't need it.

    @staticmethod
    def _process_goal(goal):
        return {
            'lang': goal
        }
        # just add a wrapper

    def rollout(self, goal):
        goal = self._process_goal(goal)
        for step in range(self.ep_len):
            self.gripper_obs.streaming()
            self.static_obs.streaming()
            obs = self._process_obs(self.static_obs.get_current_obs(), self.gripper_obs.get_current_obs())
            action = self.policy.step(obs, goal)
            self.controller.move_skill(sim2real_frame(action))
            if cont is False:
                break

    def get_next_task(self):
        return self.instruction.get_language_goal()


if __name__ == '__main__':
    agent = Agent(host='Host IP')
    agent.controller.home()
    goal = agent.get_next_task()
    agent.rollout(goal)


