import asyncio
import aiohttp
import os
import logging


class FrigateAPIWatcher:
    def __init__(self, frigate_url: str, esp_url: str, poll_interval: int = 3):
        self.frigate_url = frigate_url.rstrip('/')
        self.esp_url = esp_url
        self.poll_interval = poll_interval
        self.session = aiohttp.ClientSession()
        self.seen_event_ids = set()
        self.logger = logging.getLogger("FrigateWatcher")

    async def _trigger_beep(self, camera: str):
        try:
            self.logger.info(f"🔔 Событие от {camera}, шлём на ESP")
            async with self.session.get(self.esp_url, timeout=2) as resp:
                self.logger.info(f"✅ ESP ответил: {resp.status}")
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка при обращении к ESP: {e}")

    async def _poll_events(self):
        url = f"{self.frigate_url}/api/events?limit=10&has_snapshot=1"
        try:
            async with self.session.get(url, timeout=5) as resp:
                if resp.status != 200:
                    self.logger.error(f"❌ Ошибка запроса: {resp.status}")
                    return
                events = await resp.json()

                for event in events:
                    event_id = event.get("id")
                    camera = event.get("camera")
                    label = event.get("label")
                    end_time = event.get("end_time")

                    if (
                        camera == "Ruby2_Enter"
                        and label == "person"
                        and event_id not in self.seen_event_ids
                        and end_time is None
                    ):
                        self.seen_event_ids.add(event_id)
                        await self._trigger_beep(camera)

        except Exception as e:
            self.logger.error(f"❌ Ошибка при получении событий: {e}")

    async def run(self):
        self.logger.info("🚀 Запуск цикла опроса Frigate")
        while True:
            await self._poll_events()
            await asyncio.sleep(self.poll_interval)

    async def close(self):
        await self.session.close()


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    frigate_url = os.getenv("FRIGATE_URL", "http://127.0.0.1:5000")
    esp_url = os.getenv("ESP_URL", "http://10.0.0.252/beep")

    logging.info(f"Используем:\n - Frigate: {frigate_url}\n - ESP: {esp_url}")

    watcher = FrigateAPIWatcher(
        frigate_url=frigate_url,
        esp_url=esp_url,
    )
    try:
        await watcher.run()
    finally:
        await watcher.close()


if __name__ == "__main__":
    asyncio.run(main())
