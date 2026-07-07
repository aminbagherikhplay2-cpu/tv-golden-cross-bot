import ccxt
import pandas as pd

from indicators import (
    add_indicators,
    is_golden_cross,
    is_strong_signal,
)

from telegram import send_message

exchange = ccxt.bybit({
    "enableRateLimit": True,
})

golden = []
strong = []


def get_symbols():
    markets = exchange.load_markets()

    symbols = []

    for symbol in markets:

        market = markets[symbol]

        if (
            market["spot"]
            and market["active"]
            and market["quote"] == "USDT"
        ):
            symbols.append(symbol)

    return symbols
  def get_dataframe(symbol):

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe="1d",
        limit=250,
    )

    df = pd.DataFrame(
        ohlcv,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ],
    )

    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return add_indicators(df)


for symbol in get_symbols():

    try:

        df = get_dataframe(symbol)

        if is_golden_cross(df):
            golden.append(symbol)

        if is_strong_signal(df):
            strong.append(symbol)

        print(symbol)

    except Exception as e:

        print(symbol, e)
      message1 = "📈 <b>Golden Cross امروز</b>\n\n"

if len(golden) == 0:
    message1 += "❌ هیچ Golden Cross جدیدی پیدا نشد."
else:
    for s in sorted(golden):
        message1 += f"✅ {s}\n"

send_message(message1)


message2 = "⭐ <b>سیگنال‌های منتخب</b>\n\n"

if len(strong) == 0:
    message2 += "❌ هیچ سیگنال قدرتمندی پیدا نشد."
else:
    for s in sorted(strong):
        message2 += f"🚀 {s}\n"

send_message(message2)
