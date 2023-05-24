from .language_network import SBert


class Instruction:
    def __init__(self, language_model='paraphrase-MiniLM-L3-v2'):
        self.encoder = SBert(language_model)

    @staticmethod
    def _get_instruction():
        lang_input = [input("What should I do? \n")]
        return lang_input

    def get_language_goal(self):
        return self.encoder(self._get_instruction()).squeeze(1)

    def get_language_goal1(self, instruction):
        return self.encoder(instruction).squeeze(1).unsqueeze(0)

