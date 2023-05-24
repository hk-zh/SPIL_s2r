from abc import abstractmethod


class AbstractController:
    def __init__(self, robot):
        self.robot = robot

    @abstractmethod
    def move_relative_cartesian(self, rel_actions):
        pass

    @abstractmethod
    def move_joints(self, joints):
        pass

    @abstractmethod
    def move_skill(self, skill):
        pass

    @abstractmethod
    def move_gripper(self, action):
        pass

    @abstractmethod
    def home(self):
        pass

