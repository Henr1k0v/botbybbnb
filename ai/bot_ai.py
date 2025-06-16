import asyncio
import requests
import joblib
import pandas as pd
from telegram import Bot
from datetime import datetime
import os

BOT_TOKEN = '6474837212:AAEhd-Jd0dul-A5K6fTjkTXHgUxfEBvjDH4'
CHAT_ID = '646569774'
bot = Bot(token=BOT_TOKEN)

model = joblib.load('profit_predictor.pkl')
budget_uah = 10000
csv_file = 'history.csv'

# --- Створити CSV, якщо його ще нема ---
if not os.path.exists(csv_file):
    with open(csv_file, 'w') as f:
        f.write('date,binance_buy,binance_sell,bybit_buy,bybit_sell,profit_bnb2byb,profit_byb2bnb,profit_bnb2bnb,profit_byb2byb\n')

async def get_binance_price(trade_type: str) -> float:
    data = {
        "proMerchantAds": False,
        "page": 1,
        "rows": 1,
        "payTypes": [],
        "countries": [],
        "publisherType": None,
        "asset": "USDT",
        "fiat": "UAH",
        "tradeType": trade_type
    }
    response = requests.post("https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search", json=data)
    response.raise_for_status()
    return float(response.json()['data'][0]['adv']['price'])

async def get_bybit_price(side: str) -> float:
    url = "https://api2.bybit.com/fiat/otc/item/online"
    data = {
        "tokenId": "USDT",
        "currencyId": "UAH",
        "payment": [],
        "side": side,  # '1' = BUY, '0' = SELL
        "size": "1",
        "page": "1",
        "amount": "",
        "authMaker": False,
        "canTrade": False
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
    if "result" in result and "items" in result["result"] and result["result"]["items"]:
        return float(result["result"]["items"][0]["price"])
    else:
        raise Exception("Bybit: no price data")

async def check_prices():
    while True:
        try:
            # --- Отримуємо ціни ---
            bnb_buy = await get_binance_price("BUY")
            bnb_sell = await get_binance_price("SELL")
            byb_buy = await get_bybit_price("1")
            byb_sell = await get_bybit_price("0")

            # --- AI-оцінка прибутку ---
            prof_bnb2byb = model.predict(pd.DataFrame([[bnb_buy, byb_sell]], columns=['buy_rate','sell_rate']))[0]
            prof_byb2bnb = model.predict(pd.DataFrame([[byb_buy, bnb_sell]], columns=['buy_rate','sell_rate']))[0]
            prof_bnb2bnb = model.predict(pd.DataFrame([[bnb_buy, bnb_sell]], columns=['buy_rate','sell_rate']))[0]
            prof_byb2byb = model.predict(pd.DataFrame([[byb_buy, byb_sell]], columns=['buy_rate','sell_rate']))[0]

            # --- Запис у CSV ---
            with open(csv_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()},{bnb_buy},{bnb_sell},{byb_buy},{byb_sell},"
                        f"{prof_bnb2byb:.2f},{prof_byb2bnb:.2f},{prof_bnb2bnb:.2f},{prof_byb2byb:.2f}\n")

            # --- Формування повідомлень ---
            msgs = []

            if prof_bnb2byb > 5:
                usdt = budget_uah / bnb_buy
                msgs.append(
                    f"🔥 Binance → Bybit\nКупити за: {bnb_buy:.2f}₴\nПродати за: {byb_sell:.2f}₴\n"
                    f"AI прибуток: {prof_bnb2byb:.2f}% | ≈ {usdt:.2f} USDT"
                )
            if prof_byb2bnb > 5:
                usdt = budget_uah / byb_buy
                msgs.append(
                    f"🔥 Bybit → Binance\nКупити за: {byb_buy:.2f}₴\nПродати за: {bnb_sell:.2f}₴\n"
                    f"AI прибуток: {prof_byb2bnb:.2f}% | ≈ {usdt:.2f} USDT"
                )
            if prof_bnb2bnb > 5:
                usdt = budget_uah / bnb_buy
                msgs.append(
                    f"⚠️ Binance → Binance\nBUY: {bnb_buy:.2f}₴ → SELL: {bnb_sell:.2f}₴\n"
                    f"AI прибуток: {prof_bnb2bnb:.2f}% | ≈ {usdt:.2f} USDT"
                )
            if prof_byb2byb > 5:
                usdt = budget_uah / byb_buy
                msgs.append(
                    f"⚠️ Bybit → Bybit\nBUY: {byb_buy:.2f}₴ → SELL: {byb_sell:.2f}₴\n"
                    f"AI прибуток: {prof_byb2byb:.2f}% | ≈ {usdt:.2f} USDT"
                )

            # --- Надсилання у Telegram ---
            if msgs:
                full_message = "\n\n".join(msgs)
                print(full_message)
                await bot.send_message(chat_id=CHAT_ID, text=full_message)
            else:
                print(f"{datetime.now().time()} ➤ Прибуток <5% — повідомлення не надсилається.")

        except Exception as e:
            print(f"❌ Error: {e}")
            await bot.send_message(chat_id=CHAT_ID, text=f"❌ Помилка: {e}")

        await asyncio.sleep(5)

async def main():
    await check_prices()

if __name__ == "__main__":
    asyncio.run(main())
