# Config File

To configure the game sdk a config.toml can be created. The path to it can be set when executing `Game.run(config_path="path/to/your/config.toml")`. The default path is `/home/pi/Gamecontrol/config.toml`

## Structure

**Example**
```toml
seats=[1,2,3]
```

- `list[int] seats`: List of controller id's