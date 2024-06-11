from typing import List


class MiniGame:

    def __init__(self, inputs: List[str], player_idx: int):
        self.gpu = inputs[0]
        self.reg_0 = int(inputs[1])
        self.reg_1 = int(inputs[2])
        self.reg_2 = int(inputs[3])
        self.reg_3 = int(inputs[4])
        self.reg_4 = int(inputs[5])
        self.reg_5 = int(inputs[6])
        self.reg_6 = int(inputs[7])
        self.player_idx = player_idx

    def play(self):
        pass


class HurdleRace(MiniGame):

    def __init__(self, inputs: List[str], player_idx: int):
        super().__init__(inputs, player_idx)

        self.player_position = [self.reg_0, self.reg_1, self.reg_2][self.player_idx]
        self.safe_sections = [len(safe_section) for safe_section in
                              self.gpu[self.player_position:len(self.gpu)].split('#')]

    def play(self):
        current_section = self.safe_sections[0]

        if current_section == 1:
            print("UP")
        elif current_section == 2:
            print("LEFT")
        elif current_section == 3:
            print("DOWN")
        elif current_section > 3:
            print("RIGHT")
        else:
            print("LEFT")
