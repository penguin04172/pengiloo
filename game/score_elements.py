from enum import IntEnum

import numpy as np
from pydantic import BaseModel


class BranchLevel(IntEnum):
    LEVEL_2 = 0
    LEVEL_3 = 1
    LEVEL_4 = 2
    LEVEL_TROUGH = 3
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
    BranchLevel.LEVEL_2: 4,
    BranchLevel.LEVEL_3: 6,
    BranchLevel.LEVEL_4: 7,
    BranchLevel.LEVEL_TROUGH: 3,
}

teleop_reef_points = {
    BranchLevel.LEVEL_2: 3,
    BranchLevel.LEVEL_3: 4,
    BranchLevel.LEVEL_4: 5,
    BranchLevel.LEVEL_TROUGH: 2,
}

auto_reef_points_arr = np.array(list(auto_reef_points.values())[:3])
teleop_reef_points_arr = np.array(list(teleop_reef_points.values())[:3])


class Coral(BaseModel):
    auto_trough_coral: int = 0
    total_trough_coral: int = 0
    branches_auto: list[list[bool]] = [
        [False] * (BranchLevel.COUNT - 1) for _ in range(BranchLocation.COUNT)
    ]
    branches: list[list[bool]] = [
        [False] * (BranchLevel.COUNT - 1) for _ in range(BranchLocation.COUNT)
    ]
    branch_algaes: list[list[bool]] = [[False] * 2 for _ in range(BranchLocation.COUNT)]

    def coral_statuses(self) -> tuple[np.ndarray, np.ndarray]:
        """
        計算：
        1. 每個 Level 的總 Coral 數量
        2. Auto Coral 得分
        3. Teleop Coral 得分
        """
        # 轉換為 NumPy 陣列以加速計算
        branches_arr = np.array(self.branches, dtype=bool)  # 分支上是否有 Coral
        auto_arr = np.array(self.branches_auto, dtype=bool)  # 自動得分的 Coral
        algae_arr = np.zeros_like(branches_arr, dtype=bool)  # 預設所有位置沒有 Algae

        # 設定 Algae 影響 (每兩個 Branch 共享 Algae 狀態)
        for loc in range(BranchLocation.COUNT):
            algae_arr[loc, :2] = self.branch_algaes[loc // 2]  # 只影響 LEVEL_2 和 LEVEL_3

        # 計算總 Coral 數量（沒有 Algae 才算）
        total_corals = branches_arr & ~algae_arr
        auto_corals = auto_arr & total_corals  # 只有同時是 auto_scoring 且 valid coral 才算 Auto
        teleop_corals = total_corals ^ auto_corals  # Teleop = 總 coral - Auto coral

        return auto_corals, teleop_corals

    def num_coral_each_level_scored(
        self, auto_corals: np.ndarray, teleop_corals: np.ndarray
    ) -> np.ndarray:
        levels = np.sum(auto_corals | teleop_corals, axis=0)
        levels = np.hstack((levels, self.total_trough_coral))
        return levels

    def total_coral_scored(self, auto_corals: np.ndarray, teleop_corals: np.ndarray) -> int:
        return int((auto_corals | teleop_corals).sum() + self.total_trough_coral)

    def coral_points(self, auto_corals: np.ndarray, teleop_corals: np.ndarray) -> tuple[int, int]:
        # 直接用 NumPy 向量化計算
        auto_levels_score = np.sum(auto_corals, axis=0) * auto_reef_points_arr
        teleop_levels_score = np.sum(teleop_corals, axis=0) * teleop_reef_points_arr

        # 總分計算（避免 .item()，直接用 sum()）
        auto_score = (
            auto_levels_score.sum()
            + min(self.auto_trough_coral, self.total_trough_coral)
            * auto_reef_points[BranchLevel.LEVEL_TROUGH]
        )
        teleop_score = (
            teleop_levels_score.sum()
            + max(self.total_trough_coral - self.auto_trough_coral, 0)
            * teleop_reef_points[BranchLevel.LEVEL_TROUGH]
        )

        return int(auto_score), int(teleop_score)


class Algae(BaseModel):
    auto_processor_algae: int = 0
    auto_net_algae: int = 0
    teleop_processor_algae: int = 0
    total_net_algae: int = 0

    def auto_algae_points(self) -> int:
        auto_net = min(self.auto_net_algae, self.total_net_algae)
        return 6 * self.auto_processor_algae + 4 * auto_net

    def teleop_algae_points(self) -> int:
        return 6 * self.teleop_processor_algae + 4 * max(
            (self.total_net_algae - self.auto_net_algae), 0
        )

    def total_algae_points(self) -> int:
        return self.auto_algae_points() + self.teleop_algae_points()

    def num_processor_algae_scored(self) -> int:
        return self.auto_processor_algae + self.teleop_processor_algae

    def num_net_algae_scored(self) -> int:
        return self.total_net_algae

    def total_algae_scored(self) -> int:
        return self.num_processor_algae_scored() + self.num_net_algae_scored()


class ScoreElements(Algae, Coral):
    def __post_init__(self):
        pass
