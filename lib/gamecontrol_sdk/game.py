import asyncio
import enum
import logging
from typing import Any, Coroutine, MutableMapping
import toml

from asyncio_mqtt.error import MqttError

from gamecontrol_sdk.game_io import GameIO, GameState
from gamecontrol_sdk.players import Players


class LogLevel(enum.Enum):
    """
        Different logging levels defiend by the logging module
    """

    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class Game:
    """
        Class to control the whole game. Inherit from this class and call `run()` to start your gamecontrol
    """

    config: MutableMapping[str, Any]
    _players: Players
    _is_running = False
    _game_io: GameIO
    _game_state = GameState.IDLE

    @property
    def game_io(self):
        """
           Instance of `GameIO` used to control the whole game loop
        """

        if self._is_running:
            return self._game_io
        raise Exception('Execute Game.run() before accessing game_io')

    @property
    def players(self):
        """
            Instance of `Player` used to acces player information
        """

        if self._is_running:
            return self._players
        raise Exception('Execute Game.run() befor accessing player')

    async def set_game_state(self, state: GameState):
        """
            Set `game_state` and execute the coresponding function

            Arguments:
                state: State to wich to switch
        """

        self._game_state = state

        if self._game_state == GameState.START:
            asyncio.create_task(self.on_pregame())
        if self._game_state == GameState.RUN:
            asyncio.create_task(self.on_start())
        if self._game_state == GameState.END:
            asyncio.create_task(self.on_end())

        asyncio.create_task(self._game_io.set_game_state(self._game_state))

    async def on_init(self):
        """
            Executed, when the game is startet with `Game.run()`
        """

        logging.info("ON INIT")

    async def on_pregame(self):
        """
            Executed, before a new game starts
        """

        logging.info("ON PREGAME")

    async def on_start(self):
        """
            Executed, when a new game starts
        """
        logging.info("ON START")

    async def on_end(self):
        """
            Executed, when the game ends
        """

        self._players.reset()

        logging.info("ON END")

    async def on_exit(self, err: Exception = None):
        """
            Executed, when the game loop is exited

            Arguments:
                err: Value of the exception when the game exited with none zero code
        """

        logging.info("ON EXIT")

        if err:
            logging.error(err)

    async def on_score(self):
        """
            Executed, when a player scores one or more points
        """

        logging.info("ON SCORE")

    async def _game_io_sub(self):
        """
            Subscribe to changes of the game state

            Arguments:
                mqtt_conf: GameIO configuration
        """

        async for topic, data in self._game_io.subscribe():
            logging.debug("Got Message from: %s with %s", topic, data)

            if (topic == "status/ready"):
                self._players.set_ready(data['seat'], data['ready'])
                await self._ready()
            elif (topic == "score") and self._game_state is GameState.RUN:
                self._players.set_score(data['seat'], data['score'])
                await self.on_score()

    async def _ready(self):
        """
            Check ready state and change `game_state`
        """

        all_ready = True
        for p_ready in self.players.ready.values():
            all_ready = all_ready and p_ready

        if all_ready:
            logging.debug("All ready")

        if all_ready:
            if self._game_state == GameState.IDLE:
                await self.set_game_state(GameState.START)
            elif self._game_state == GameState.START:
                await self.set_game_state(GameState.RUN)
            elif self._game_state == GameState.END:
                await self.set_game_state(GameState.IDLE)

            self._players.reset_ready()

    async def _run(self, conf_path: str):
        """
            Asynchronous `run` function
        """
        try:
            self.config = toml.load(conf_path)
            logging.debug(self.config)

            self._players = Players(self.config['seats'])

            self._game_io = GameIO(self.config['MQTT'])
            await self._game_io.connect()

            main_loop = asyncio.gather(
                self._game_io_sub()
            )

            await self.on_init()
            self._is_running = True

            # try:
            await main_loop
            await self.on_exit()
            # except Exception as err:
            #    await self.on_exit(err)
        except MqttError:
            logging.error("Couldn't connect to MQTT Client")
            logging.error("MQTT Config: %s", self.config['MQTT'])
        except FileNotFoundError:
            logging.error("No config found at: %s", conf_path)

    def run(self, conf_path: str = '/home/pi/Gamecontrol/config.toml', log_level: LogLevel = LogLevel.NOTSET):
        """
            Start the game engine

            Arguments:
                conf_path: Path to configuration.toml
                log_level: logging level
        """

        logging.getLogger().setLevel(log_level.value)

        asyncio.run(self._run(conf_path))
