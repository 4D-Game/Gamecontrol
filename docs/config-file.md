# Config file

The CrazyComet game adds some more parameters to the `config.toml` as already defined in the [SDK documentation](https://4d-game.github.io/sdk/gamecontrol-sdk/config-file/).

!!! INFO
    The structure of the config file should be the same for gamecontrol and display

**Example**
```toml
seats=[1]

team_A=[1, 2, 6]
team_B=[3, 4, 5]

[MQTT]
broker_ip="10.3.141.1"
```

- `list team_A`: List of players in team A
- `list team_B`: List of players in team B