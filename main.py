import aiohttp
import asyncio
import datetime
import sys
import json

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="


class CurrencyFetcher:
    def __init__(self, days: int):
        if days > 10:
            raise ValueError("Cannot fetch data for more than 10 days")
        self.days = days

    async def fetch_currency(self, session, date: str):
        try:
            async with session.get(API_URL + date) as response:
                data = await response.json()
                return self.parse_response(data)
        except Exception as e:
            print(f"Error fetching data for {date}: {e}")
            return None

    def parse_response(self, data):
        date = data["date"]
        eur = next( (rate for rate in data["exchangeRate"] if rate["currency"] == "EUR"), None)
        usd = next((rate for rate in data["exchangeRate"] if rate["currency"] == "USD"), None)

        # Повертаємо словник з курсами для дати
        return {
            date: {
                "EUR": (
                    {"sale": eur["saleRate"], "purchase": eur["purchaseRate"]}
                    if eur
                    else {}),
                "USD": ({"sale": usd["saleRate"], "purchase": usd["purchaseRate"]}
                    if usd
                    else {})}}

    async def get_exchange_rates(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            # Створюємо список запитів для кожної дати
            for i in range(self.days):
                date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime(
                    "%d.%m.%Y"
                )
                tasks.append(self.fetch_currency(session, date))

            # Виконуємо всі запити та отримуємо результати
            results = await asyncio.gather(*tasks)
            # Повертаємо список словників з результатами
            return [result for result in results if result]


async def main(days: int):
    fetcher = CurrencyFetcher(days)
    results = await fetcher.get_exchange_rates()

    # Виводимо результат у потрібному форматі
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    # Перевіряємо аргументи командного рядка
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    else:
        days = 2 # Якщо аргумент не переданий, за замовчуванням беремо 1 день

    # Запускаємо асинхронну функцію
    asyncio.run(main(days))
