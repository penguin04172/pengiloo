from enum import IntEnum

from pydantic import BaseModel


class BranchLevel(IntEnum):
    LEVEL_TROUGH = 0
    LEVEL_2 = 1
    LEVEL_3 = 2
    LEVEL_4 = 3
    COUNT = 4


class BranchLocation(IntEnum):
    BRANCH_A = 0
    BRANCH_B = 1
    BRANCH_C = 2
    BRANCH_D = 3
    BRANCH_E = 4
    BRANCH_F = 5
    BRANCH_G = 6
    BRANCH_H = 7
    BRANCH_I = 8
    BRANCH_J = 9
    BRANCH_K = 10
    BRANCH_L = 11
    COUNT = 12


auto_reef_points = {
    BranchLevel.LEVEL_TROUGH: 3,
    BranchLevel.LEVEL_2: 4,
    BranchLevel.LEVEL_3: 6,
    BranchLevel.LEVEL_4: 7,
}

teleop_reef_points = {
    BranchLevel.LEVEL_TROUGH: 2,
    BranchLevel.LEVEL_2: 3,
    BranchLevel.LEVEL_3: 4,
    BranchLevel.LEVEL_4: 5,
}


class Coral(BaseModel):
    auto_trough_coral: int = 0
    teleop_trough_coral: int = 0
    auto_scoring: list[list[bool]] = [
        [False] * (BranchLevel.COUNT - 1) for _ in range(BranchLocation.COUNT)
    ]
    branches: list[list[bool]] = [
        [False] * (BranchLevel.COUNT - 1) for _ in range(BranchLocation.COUNT)
    ]
    branch_algaes: list[list[bool]] = [[False] * 2 for _ in range(BranchLocation.COUNT)]

    def num_auto_teleop_coral_scored(
        self, location: BranchLocation, level: BranchLevel
    ) -> tuple[int, int]:
        if (
            location < BranchLocation.BRANCH_A
            or location > BranchLocation.BRANCH_L
            or level < BranchLevel.LEVEL_2
            or level > BranchLevel.LEVEL_4
        ):
            return 0, 0

        level -= BranchLevel.LEVEL_2

        branch = self.branches[location][level]
        auto = self.auto_scoring[location][level]

        algae_state = self.branch_algaes[int(location / 2)][level] if 0 <= level < 2 else False

        total_corals = 1 if branch and not algae_state else 0
        auto_corals = 1 if auto and total_corals > 0 and not algae_state else 0

        return auto_corals, total_corals - auto_corals

    def num_coral_scored(self, location: BranchLocation, level: BranchLevel) -> int:
        auto_corals, teleop_corals = self.num_auto_teleop_coral_scored(location, level)
        return auto_corals + teleop_corals

    def num_coral_each_level_scored(self, level: BranchLevel) -> int:
        if level < BranchLevel.LEVEL_TROUGH or level > BranchLevel.LEVEL_4:
            return 0

        if level == BranchLevel.LEVEL_TROUGH:
            return self.auto_trough_coral + self.teleop_trough_coral
        else:
            return sum(
                self.num_coral_scored(location, level) for location in range(BranchLocation.COUNT)
            )

    def total_coral_scored(self) -> int:
        return sum(
            self.num_coral_each_level_scored(level)
            for level in range(BranchLevel.LEVEL_TROUGH, BranchLevel.COUNT)
        )

    def auto_coral_points(self) -> int:
        return (
            sum(
                (auto_reef_points[level] * self.num_auto_teleop_coral_scored(location, level)[0])
                for location in range(BranchLocation.COUNT)
                for level in range(BranchLevel.LEVEL_2, BranchLevel.COUNT)
            )
            + self.auto_trough_coral * auto_reef_points[BranchLevel.LEVEL_TROUGH]
        )

    def teleop_coral_points(self) -> int:
        return (
            sum(
                teleop_reef_points[level] * self.num_auto_teleop_coral_scored(location, level)[1]
                for location in range(BranchLocation.COUNT)
                for level in range(BranchLevel.LEVEL_2, BranchLevel.COUNT)
            )
            + self.teleop_trough_coral * teleop_reef_points[BranchLevel.LEVEL_TROUGH]
        )

    def total_coral_points(self) -> int:
        return self.auto_coral_points() + self.teleop_coral_points()


class Algae(BaseModel):
    auto_processor_algae: int = 0
    auto_net_algae: int = 0
    teleop_processor_algae: int = 0
    teleop_net_algae: int = 0

    def auto_algae_points(self) -> int:
        return 6 * self.auto_processor_algae + 4 * self.auto_net_algae

    def teleop_algae_points(self) -> int:
        return 6 * self.teleop_processor_algae + 4 * self.teleop_net_algae

    def total_algae_points(self) -> int:
        return self.auto_algae_points() + self.teleop_algae_points()

    def num_processor_algae_scored(self) -> int:
        return self.auto_processor_algae + self.teleop_processor_algae

    def num_net_algae_scored(self) -> int:
        return self.auto_net_algae + self.teleop_net_algae

    def total_algae_scored(self) -> int:
        return self.num_processor_algae_scored() + self.num_net_algae_scored()


class ScoreElements(Algae, Coral):
    def __post_init__(self):
        pass
        # for i in range(BranchLocation.COUNT):
        #     if i % 2 == 0:
        #         self.algaes[i][0] = True
        #     else:
        #         self.algaes[i][1] = True
