from datetime import datetime
from enum import IntEnum

from ws.notifier import Notifier

MIN_DISPLAY_ID = 100
DISPLAY_PURGE_TTL_MIN = 30


class DisplayType(IntEnum):
    INVALID = 0
    PLACEHOLDER = 1
    ALLIANCE_STATION = 2
    ANNOUNCER = 3
    AUDIENCE = 4
    BRACKET = 5
    FIELD_MONITOR = 6
    LOGO = 7
    QUEUEING = 8
    RANKINGS = 9
    TWITCH_STREAM = 10
    WALL = 11
    WEBPAGE = 12


display_type_names = {
    DisplayType.PLACEHOLDER: 'Placeholder',
    DisplayType.ALLIANCE_STATION: 'Alliance Station',
    DisplayType.ANNOUNCER: 'Announcer',
    DisplayType.AUDIENCE: 'Audience',
    DisplayType.BRACKET: 'Bracket',
    DisplayType.FIELD_MONITOR: 'Field Monitor',
    DisplayType.LOGO: 'Logo',
    DisplayType.QUEUEING: 'Queueing',
    DisplayType.RANKINGS: 'Ranking',
    DisplayType.TWITCH_STREAM: 'Twitch Stream',
    DisplayType.WALL: 'Wall',
    DisplayType.WEBPAGE: 'Webpage',
}

display_type_paths = {
    DisplayType.PLACEHOLDER: '/display',
    DisplayType.ALLIANCE_STATION: '/displays/alliance_station',
    DisplayType.ANNOUNCER: '/displays/announcer',
    DisplayType.AUDIENCE: '/displays/audience',
    DisplayType.BRACKET: '/displays/bracket',
    DisplayType.FIELD_MONITOR: '/displays/field_monitor',
    DisplayType.LOGO: '/displays/logo',
    DisplayType.QUEUEING: '/displays/queueing',
    DisplayType.RANKINGS: '/displays/rankings',
    DisplayType.TWITCH_STREAM: '/displays/twitch',
    DisplayType.WALL: '/displays/wall',
    DisplayType.WEBPAGE: '/displays/webpage',
}


class DisplayConfiguration:
    id: str
    nickname: str = ''
    type: DisplayType = DisplayType.INVALID
    configuration: dict[str, str] = {}

    def __init__(
        self,
        id: str,
        nickname: str = '',
        type: DisplayType = DisplayType.INVALID,
        configuration: dict[str, str] = None,
    ):
        self.id = id
        self.nickname = nickname
        self.type = type
        self.configuration = configuration


class Display:
    display_configuration: DisplayConfiguration
    ip_address: str
    connection_count: int = 0
    notifier: Notifier = None
    last_connected_time: datetime

    def __init__(
        self,
        display_configuration: DisplayConfiguration,
        ip_address: str = '',
        last_connected_time: datetime = datetime.fromtimestamp(0),
    ):
        self.display_configuration = display_configuration
        self.ip_address = ip_address
        self.last_connected_time = last_connected_time

    def to_url(self) -> str:
        path = f'{display_type_paths[self.display_configuration.type]}'
        path += f'?display_id={self.display_configuration.id}'
        path += (
            f'&nickname={self.display_configuration.nickname}'
            if self.display_configuration.nickname
            else ''
        )

        keys = sorted(self.display_configuration.configuration.keys())
        for key in keys:
            path += f'&{key}={self.display_configuration.configuration[key]}'

        return path

    def generate_display_cononfiguration_message(self):
        return self.to_url()


class DisplayMixin:
    displays: dict[str, Display]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def next_display_id(self) -> str:
        display_id = MIN_DISPLAY_ID
        while str(display_id) in self.displays:
            display_id += 1
        return str(display_id)

    async def register_display(self, config: DisplayConfiguration, ip_address: str) -> Display:
        display = self.displays.get(config.id)

        if display is not None and config.type == DisplayType.PLACEHOLDER:
            self.displays[config.id].connection_count += 1
            self.displays[config.id].ip_address = ip_address

        else:
            if display is None:
                display = Display(
                    display_configuration=config,
                    ip_address=ip_address,
                    last_connected_time=datetime.now(),
                )
                display.notifier = Notifier(
                    'display', display.generate_display_cononfiguration_message
                )
                self.displays[config.id] = display

            display.display_configuration = config
            display.ip_address = ip_address
            display.connection_count += 1
            display.last_connected_time = datetime.now()
            await display.notifier.notify()

        await self.display_configuration_notifier.notify()
        return display

    async def update_display(self, config: DisplayConfiguration):
        display = self.displays.get(config.id)
        if display is None:
            raise ValueError(f'Display {config.id} not found')

        if vars(display.display_configuration) != vars(config):
            display.display_configuration = config
            await display.notifier.notify()
            await self.display_configuration_notifier.notify()

    async def mark_display_disconnect(self, display_id: str):
        display = self.displays.get(display_id)
        if display is not None:
            if (
                display.connection_count == 1
                and display.display_configuration.type == DisplayType.PLACEHOLDER
                and display.display_configuration.nickname == ''
                and len(display.display_configuration.configuration) == 0
            ):
                del self.displays[display.display_configuration.id]
            else:
                display.connection_count -= 1

            display.last_connected_time = datetime.now()
            await self.display_configuration_notifier.notify()

    async def purge_disconnected_displays(self):
        deleted = False
        for i in list(self.displays.keys()):
            if (
                self.displays[i].connection_count == 0
                and self.displays[i].display_configuration.nickname == ''
                and (datetime.now() - self.displays[i].last_connected_time).total_seconds()
                >= DISPLAY_PURGE_TTL_MIN * 60
            ):
                del self.displays[i]
                deleted = True

        if deleted:
            await self.display_configuration_notifier.notify()


def display_from_url(path: str, query: dict[str, list[str]]):
    if 'display_id' not in query:
        raise ValueError('Display ID not specified')

    display_configuration = DisplayConfiguration(
        id=query['display_id'][0],
        nickname=query.get('nickname', [''])[0],
        type=DisplayType.INVALID,
        configuration={
            key: value[0] for key, value in query.items() if key not in ['display_id', 'nickname']
        },
    )

    for display_type, display_path in display_type_paths.items():
        if path == f'/api{display_path}/websocket':
            display_configuration.type = display_type
            break

    if display_configuration.type == DisplayType.INVALID:
        raise ValueError(f'Could not determine display type from {path}')

    return display_configuration
