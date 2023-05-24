from abc import ABC

from control.abstract_controller import AbstractController
from frankx import JointMotion, LinearRelativeMotion, Affine, LinearMotion, PathMotion
import numpy as np


class Controller(AbstractController, ABC):
    def __init__(self, robot):
        super().__init__(robot)
        self.gripper = robot.get_gripper()
        self.gripper.gripper_speed = 0.1
        self.gripper.gripper_force = 20
        self.gripper.release(0.08)
        self.gripper_state = 'open'

    def move_joints(self, joints):
        """
        :param joints: List of 7 joint values
        :return: void
        """
        joint_motion = JointMotion(joints)
        success = self.robot.move(joint_motion)
        if not success:
            self.robot.recover_from_errors()

    def move_relative_gripper(self, rel_action):
        """
        This function is used to move the gripper with delta action in its frame
        :param rel_action: a numpy array with the shape of (6) [x, y, z, r, p, y]
        :return: void
        """
        motion = LinearRelativeMotion(Affine(*rel_action.tolist()))
        success = self.robot.move(motion)
        if not success:
            self.robot.recover_from_errors()

    def move_relative_base(self, rel_action):
        """
        This function is used to move the gripper with delta action in the base frame
        :param rel_action: a numpy array with the shape of (6) [x, y, z, r, p, y]
        :return: void
        """
        current_pose = self.robot.current_pose()
        motion = LinearMotion(Affine(*rel_action.tolist()) * current_pose)
        success = self.robot.move(motion)
        if not success:
            self.robot.recover_from_errors()

    def move_relative_gripper_path(self, rel_actions):
        """
        This function is used to move the gripper according to a sequence of delta actions in its frame
        :param rel_actions: a numpy array with the shape of (6) [x, y, z, r, p, y]
        :return: void
        """
        N, _ = rel_actions.shape
        rel_actions_list = rel_actions.tolist()
        current_pose = self.robot.current_pose()
        c = 0.05 if current_pose.c > 0 else -0.05
        way_points = []
        for i in range(N):
            current_pose = current_pose * Affine(*rel_actions_list[i])
            current_pose = Affine(current_pose.x, current_pose.y, min(max(current_pose.z, 0.30), 0.58), current_pose.a, current_pose.b, c)
            way_points.append(current_pose)

        motion = PathMotion(way_points, blend_max_distance=0.05)
        success = self.robot.move(motion)
        if not success:
            self.robot.recover_from_errors()

    def move_relative_base_path(self, rel_actions):
        """
        This function is used to move the gripper according to a sequence of delta actions in the base frame
        :param rel_actions: a sequence of actions with the shape of (N,6)
        :return:void
        """
        N, _ = rel_actions.shape
        rel_actions_list = rel_actions.tolist()
        current_pose = self.robot.current_pose()
        way_points = []
        for i in range(N):
            way_points.append(Affine(*rel_actions_list[i]) * current_pose)
            current_pose = Affine(*rel_actions_list[i]) * current_pose

        motion = PathMotion(way_points, blend_max_distance=0.05)
        success = self.robot.move(motion)
        if not success:
            self.robot.recover_from_errors()

    def move_skill(self, skill):
        """
        This function is used to perform a skill with the shape of (H, 7). It refers to a sequence of actions with length
        :param skill: a sequence of actions with the shape of (H, 7)
        :return: void
        """
        H, _ = skill.shape
        g_actions = skill[:, 6]
        ee_actions = skill[:, :6]
        # self.move_gripper_async(g_actions[-1])
        self.move_relative_gripper_path(ee_actions)
        self.move_gripper(g_actions[-1])

    def move_step(self, action):
        self.move_gripper(action[6])
        self.move_relative_gripper(action[:6])

    def move_gripper(self, action):
        """
        :param action: one float value between [-1,1] indicate if open of close the gripper.
        :return: void
        """
        success = True
        if action > 0 and self.gripper_state == 'closed':
            success = self.gripper.move(0.08)
            self.gripper_state = 'open'
        elif action <= 0 and self.gripper_state == 'open':
            success = self.gripper.clamp()
            self.gripper_state = 'closed'
        if not success:
            self.robot.recover_from_errors()

    def move_gripper_async(self, action):
        if action > 0:
            self.gripper.move_unsafe_async(0.06)
        else:
            self.gripper.move_unsafe_async(0.0)

    def home(self):
        self.robot.set_default_behavior()
        self.robot.recover_from_errors()

        # Joint motion
        self.robot.move(JointMotion([-0.669, -0.652, 0.139, -2.210, 0.244, 1.919, 0.266]))
        # Define and move forwards
        # camera_frame = Affine(y=0.05)
        # home_pose = Affine(0.480, 0.0, 0.40)

        # self.robot.move(camera_frame, LinearMotion(home_pose))






