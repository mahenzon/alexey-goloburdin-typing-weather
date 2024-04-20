import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Protocol
from typing import TypedDict

from weather_api_service import Weather
from weather_formatter import format_weather


class WeatherStorage(Protocol):
    """Interface for any storage saving weather"""

    def save(self, weather: Weather) -> None:
        raise NotImplementedError


class PlainFileWeatherStorage:
    """Store weather in plain text file"""

    def __init__(self, file: Path) -> None:
        self._file = file

    def save(self, weather: Weather) -> None:
        now = datetime.now(tz=timezone.utc)
        formatted_weather = format_weather(weather)
        with self._file.open("a") as f:
            f.write(f"{now}\n{formatted_weather}\n")


class HistoryRecord(TypedDict):
    date: str
    weather: str


class JSONFileWeatherStorage:
    """Store weather in JSON file"""

    def __init__(self, jsonfile: Path) -> None:
        self._jsonfile = jsonfile
        self._init_storage()

    def save(self, weather: Weather) -> None:
        history = self._read_history()
        history.append(
            {
                "date": str(datetime.now(tz=timezone.utc)),
                "weather": format_weather(weather),
            },
        )
        self._write(history)

    def _init_storage(self) -> None:
        if not self._jsonfile.exists():
            self._jsonfile.write_text("[]")

    def _read_history(self) -> list[HistoryRecord]:
        with self._jsonfile.open() as f:
            return json.load(f)

    def _write(self, history: list[HistoryRecord]) -> None:
        with self._jsonfile.open("w") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)


def save_weather(weather: Weather, storage: WeatherStorage) -> None:
    """Saves weather in the storage"""
    storage.save(weather)
