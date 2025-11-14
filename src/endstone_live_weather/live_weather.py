import datetime
import urllib.request

from endstone.plugin import Plugin


class LiveWeather(Plugin):
    api_version = "0.10"

    def on_enable(self) -> None:
        self.server.scheduler.run_task(self, self.sync_weather, 0, 5000)

    def sync_weather(self) -> None:
        try:
            weather_mode = self.get_weather_vienna()
        except Exception as e:
            self.logger.warning(f"{e}")
            return

        try:
            self.server.dispatch_command(self.server.command_sender, f"weather {weather_mode} 5000")
        except Exception as e:
            self.logger.warning(f"{e}")

        try:
            ticks = self.get_time()
            self.server.dispatch_command(self.server.command_sender, f"time set {ticks}")
        except Exception as e:
            self.logger.warning(f"{e}")

    @staticmethod
    def get_weather_vienna() -> str:
        url = "https://wttr.in/Vienna?format=%C&lang=en"

        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                condition = r.read().decode().strip().lower()
        except Exception as e:
            raise RuntimeError(f"wttr.in request failed: {e}") from e

        if "thunder" in condition or "storm" in condition:
            return "thunder"
        elif "rain" in condition:
            return "rain"
        else:
            return "clear"

    @staticmethod
    def get_time() -> int:
        now = datetime.datetime.now()
        seconds = now.hour * 3600 + now.minute * 60 + now.second
        return int((seconds / 86400) * 24000) % 24000
