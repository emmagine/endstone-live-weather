import datetime, pytz, urllib.request

from endstone.plugin import Plugin


class LiveWeather(Plugin):
    api_version = "0.10"

    def on_enable(self) -> None:
        self.server.scheduler.run_task(self, self.sync_weather, 0, 5000)

    def sync_weather(self) -> None:
        self.server.dispatch_command(self.server.command_sender, f"weather {self.get_weather_vienna()} 5000")
        self.server.dispatch_command(self.server.command_sender, f"time set {self.get_vienna_ticks()}")

    @staticmethod
    def get_weather_vienna():
        url = "https://wttr.in/Vienna?format=%C&lang=en"

        with urllib.request.urlopen(url, timeout=5) as r:
            condition = r.read().decode().strip().lower()

        if "thunder" in condition or "storm" in condition:
            return "thunder"
        elif "rain" in condition:
            return "rain"
        else:
            return "clear"

    @staticmethod
    def get_vienna_ticks() -> int:
        now = datetime.datetime.now(pytz.timezone("Europe/Vienna"))
        seconds = now.hour * 3600 + now.minute * 60 + now.second
        return int((seconds / 86400) * 24000) % 24000
