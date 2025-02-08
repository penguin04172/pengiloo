import asyncio

import models
from network.openwrt import UbusClient

SWITCH_CONFIG_BACKOFF_DURATION = 5
SWITCH_CONFIG_PAUSE_DURATION_SEC = 2
SWITCH_TEAM_GATEWAY_ADDRESS = 4

VLAN_IDS = [10, 20, 30, 40, 50, 60]

server_ip_address = '10.0.100.5'


class Switch:
    def __init__(self, address, password):
        self._ubus = UbusClient(host=address, password=password)
        self._lock = asyncio.Lock()
        self.status = 'UNKNOWN'
        self.config_backoff_duration = SWITCH_CONFIG_BACKOFF_DURATION
        self.config_pause_duration_sec = SWITCH_CONFIG_PAUSE_DURATION_SEC

    async def configure_team_ethernet(self, teams: list[models.Team]):
        async with self._lock:
            self.status = 'CONFIGURING'
            await self._ubus.login()
            for vlan in VLAN_IDS:
                await self._ubus.generate_ethernet_configs(
                    None,
                    vlan,
                )
            await self._ubus.commit_ethernet_configs()
            await asyncio.sleep(self.config_pause_duration_sec)

            team_changed = False

            async def add_team_to_vlan(team, vlan):
                if team is None:
                    return

                await self._ubus.generate_ethernet_configs(team.id, vlan)
                nonlocal team_changed
                team_changed = True
                return

            for i in range(6):
                await add_team_to_vlan(teams[i], VLAN_IDS[i])

            if team_changed:
                await self._ubus.commit_ethernet_configs()
                await asyncio.sleep(self.config_backoff_duration)
