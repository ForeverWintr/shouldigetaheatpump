from pendulum import Date
import aiohttp


async def get_weather_data(start: Date, end: Date):
    """Get historical weather data"""

    51.11516647256088, -114.06747997399614
    async with aiohttp.ClientSession() as session:
        async with session.get("http://httpbin.org/get") as resp:
            print(resp.status)
            print(await resp.text())
