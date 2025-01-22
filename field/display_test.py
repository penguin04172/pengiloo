import asyncio
import unittest
from datetime import datetime, timedelta

import models

from .display import (
    DISPLAY_PURGE_TTL_MIN,
    Display,
    DisplayConfiguration,
    DisplayType,
    display_from_url,
)
from .test_helper import setup_test_arena_with_parameter


class TestDisplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        models.db.bind(provider='sqlite', filename=':memory:', create_db=True)
        models.db.generate_mapping(create_tables=True)

    @classmethod
    def tearDownClass(cls) -> None:
        models.db.disconnect()

    def setUp(self) -> None:
        models.db.create_tables(True)

    def tearDown(self) -> None:
        models.db.drop_all_tables(with_all_data=True)

    def test_display_from_url(self):
        query = dict[str, list[str]]()
        with self.assertRaises(ValueError):
            display_from_url('/display', query)

        query['display_id'] = ['123']
        with self.assertRaises(ValueError):
            display_from_url('/blorpy', query)

        display = display_from_url('/display/websocket', query)
        self.assertEqual(display.type, DisplayType.PLACEHOLDER)
        display = display_from_url('/displays/alliance_station/websocket', query)
        self.assertEqual(display.type, DisplayType.ALLIANCE_STATION)
        display = display_from_url('/displays/announcer/websocket', query)
        self.assertEqual(display.type, DisplayType.ANNOUNCER)
        display = display_from_url('/displays/audience/websocket', query)
        self.assertEqual(display.type, DisplayType.AUDIENCE)
        display = display_from_url('/displays/field_monitor/websocket', query)
        self.assertEqual(display.type, DisplayType.FIELD_MONITOR)
        display = display_from_url('/displays/rankings/websocket', query)
        self.assertEqual(display.type, DisplayType.RANKINGS)

        query['nickname'] = ['Test']
        query['key1'] = ['value1']
        query['key2'] = ['value2']
        query['color'] = ['#0f0']
        display = display_from_url('/display/websocket', query)
        self.assertEqual(display.nickname, 'Test')
        self.assertEqual(len(display.configuration), 3)
        self.assertEqual(display.configuration['key1'], 'value1')
        self.assertEqual(display.configuration['key2'], 'value2')
        self.assertEqual(display.configuration['color'], '#0f0')

    def test_display_to_url(self):
        display = Display(
            DisplayConfiguration(
                '123', 'Test', DisplayType.RANKINGS, {'f': '1', 'z': '#fff', 'a': '3', 'c': '4'}
            )
        )
        self.assertEqual(
            display.to_url(), '/displays/rankings?display_id=123&nickname=Test&a=3&c=4&f=1&z=#fff'
        )

    def test_next_display(self):
        arena = setup_test_arena_with_parameter(self)
        self.assertEqual(arena.next_display_id(), '100')

        display_config = DisplayConfiguration('100', type=DisplayType.PLACEHOLDER)
        asyncio.run(arena.register_display(display_config, '1.2.3.4'))
        self.assertEqual(arena.next_display_id(), '101')

    def test_display_register_unregister(self):
        arena = setup_test_arena_with_parameter(self)

        display_config = DisplayConfiguration('123', 'placeholder', DisplayType.PLACEHOLDER, {})
        asyncio.run(arena.register_display(display_config, '1.2.3.4'))
        self.assertIn('123', arena.displays)
        self.assertEqual('placeholder', arena.displays['123'].display_configuration.nickname)
        self.assertEqual(DisplayType.PLACEHOLDER, arena.displays['123'].display_configuration.type)
        self.assertEqual(1, arena.displays['123'].connection_count)
        self.assertEqual('1.2.3.4', arena.displays['123'].ip_address)
        notifier = arena.displays['123'].notifier

        display_config2 = DisplayConfiguration('123', 'rankings', DisplayType.RANKINGS, {})
        asyncio.run(arena.register_display(display_config2, '2.3.4.5'))
        self.assertIn('123', arena.displays)
        self.assertEqual('rankings', arena.displays['123'].display_configuration.nickname)
        self.assertEqual(DisplayType.RANKINGS, arena.displays['123'].display_configuration.type)
        self.assertEqual(2, arena.displays['123'].connection_count)
        self.assertEqual('2.3.4.5', arena.displays['123'].ip_address)
        self.assertEqual(notifier, arena.displays['123'].notifier)

        display_config3 = DisplayConfiguration('124', '', DisplayType.FIELD_MONITOR, {})
        asyncio.run(arena.register_display(display_config3, '3.4.5.6'))
        self.assertIn('124', arena.displays)
        self.assertEqual(1, arena.displays['124'].connection_count)

        display_config4 = DisplayConfiguration(
            '123', 'alliance', DisplayType.ALLIANCE_STATION, {'station': 'B2'}
        )
        asyncio.run(arena.update_display(display_config4))
        self.assertIn('123', arena.displays)
        self.assertEqual('alliance', arena.displays['123'].display_configuration.nickname)
        self.assertEqual(
            DisplayType.ALLIANCE_STATION, arena.displays['123'].display_configuration.type
        )
        self.assertEqual(2, arena.displays['123'].connection_count)

        asyncio.run(arena.mark_display_disconnect(display_config.id))
        asyncio.run(arena.mark_display_disconnect(display_config3.id))
        self.assertIn('124', arena.displays)
        self.assertEqual(0, arena.displays['124'].connection_count)
        self.assertIn('123', arena.displays)
        self.assertEqual(1, arena.displays['123'].connection_count)

    def test_display_update_error(self):
        arena = setup_test_arena_with_parameter(self)
        display_config = DisplayConfiguration('123', {})
        with self.assertRaises(ValueError):
            asyncio.run(arena.update_display(display_config))

    def test_display_purge(self):
        arena = setup_test_arena_with_parameter(self)

        display_config = DisplayConfiguration('123', '', DisplayType.PLACEHOLDER, {})
        asyncio.run(arena.register_display(display_config, '1.2.3.4'))
        self.assertIn('123', arena.displays)
        asyncio.run(arena.mark_display_disconnect(display_config.id))
        self.assertNotIn('123', arena.displays)

        display_config.nickname = 'Test'
        asyncio.run(arena.register_display(display_config, '1.2.3.4'))
        self.assertIn('123', arena.displays)
        asyncio.run(arena.mark_display_disconnect(display_config.id))
        self.assertIn('123', arena.displays)

        display_config = DisplayConfiguration('124', '', DisplayType.FIELD_MONITOR, {})
        asyncio.run(arena.register_display(display_config, '1.2.3.4'))
        self.assertIn('124', arena.displays)
        asyncio.run(arena.mark_display_disconnect(display_config.id))
        self.assertIn('124', arena.displays)
        asyncio.run(arena.purge_disconnected_displays())
        self.assertIn('124', arena.displays)

        asyncio.run(arena.register_display(display_config, '1.2.3.4'))
        self.assertIn('124', arena.displays)
        asyncio.run(arena.mark_display_disconnect(display_config.id))
        arena.displays['124'].last_connected_time = datetime.now() - timedelta(
            minutes=DISPLAY_PURGE_TTL_MIN
        )
        asyncio.run(arena.purge_disconnected_displays())
        self.assertNotIn('124', arena.displays)

        display_config.nickname = 'Test'
        asyncio.run(arena.register_display(display_config, '1.2.3.4'))
        self.assertIn('124', arena.displays)
        asyncio.run(arena.mark_display_disconnect(display_config.id))
        arena.displays['124'].last_connected_time = datetime.now() - timedelta(
            minutes=DISPLAY_PURGE_TTL_MIN
        )
        asyncio.run(arena.purge_disconnected_displays())
        self.assertIn('124', arena.displays)
