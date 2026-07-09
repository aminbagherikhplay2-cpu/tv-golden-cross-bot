import ccxt
import pandas as pd

from indicators import (
    add_indicators,
    is_golden_cross,
    is_strong_signal,
)

from telegram import send_message
send_message("🤖 ربات شروع به اجرا کرد...")

EXCHANGES = [
    "binance",
    "okx",
    "kucoin",
    "mexc",
    "gate",
    "bitget",
    "htx",
    "bingx",
    "bitmart",
    "kraken",
]

def connect_exchange():

    for name in EXCHANGES:

        try:

            exchange = getattr(ccxt, name)({
                "enableRateLimit": True,
            })

            exchange.load_markets()

            send_message(f"✅ اتصال به {name} برقرار شد.")

            return exchange

        except Exception:

            continue

    raise Exception("No exchange available")

exchange = connect_exchange()

def get_all_symbols():

    symbols = {}

    for name in EXCHANGES:

        try:

            ex = getattr(ccxt, name)({
                "enableRateLimit": True,
            })
            exchange_cache[name] = ex

            markets = ex.load_markets()

            count = 0

            for symbol in markets:

                market = markets[symbol]

                if (
                    market["spot"]
                    and market["active"]
                    and market["quote"] == "USDT"
                ):

                    if symbol not in symbols:
                        symbols[symbol] = name
                        count += 1

            send_message(f"✅ {name}: {count} ارز اضافه شد")

        except Exception:

            send_message(f"❌ {name}: خطا")

    send_message(f"📊 تعداد کل ارزهای منحصربه‌فرد: {len(symbols)}")

    return symbols

exchange_cache = {}
all_symbols = get_all_symbols()

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

    send_message(f"📋 لیست ارزها:\n\n{symbols}")

    return symbols


def get_dataframe(symbol):

    exchange = exchange_cache[all_symbols[symbol]]

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
    


for symbol in all_symbols:

    try:

        df = get_dataframe(symbol)

        if is_golden_cross(df):
            golden.append(symbol)

        if is_strong_signal(df):
            strong.append(symbol)

        print(symbol)

    except Exception as e:
        print(symbol, e)


message1 = f"🔍 تعداد ارزهای اسکن شده: {len(all_symbols)}\n\n"
message1 += "📈 <b>Golden Cross امروز</b>\n\n"

if len(golden) == 0:
    message1 += "❌ هیچ Golden Cross جدیدی پیدا نشد."
else:
    for s in sorted(golden):
        exchange_name = all_symbols[s]
        message1 += f"✅ {s} ({exchange_name.upper()})\n"

send_message(message1)

message2 = "⭐ <b>سیگنال‌های منتخب</b>\n\n"

if len(strong) == 0:
    message2 += "❌ هیچ سیگنال قدرتمندی پیدا نشد."
else:
    for s in sorted(strong):
        message2 += f"🚀 {s}\n"

send_message(message2)
send_message("✅ ربات با موفقیت اجرا شد.")
