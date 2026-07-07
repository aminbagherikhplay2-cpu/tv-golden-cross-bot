import pandas as pd


def add_indicators(df):
    df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()

    delta = df["close"].diff()

    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()

    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()

    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()

    df["AVG_VOLUME"] = df["volume"].rolling(20).mean()

    return df


def is_golden_cross(df):
    if len(df) < 201:
        return False

    prev = df.iloc[-2]
    last = df.iloc[-1]

    return (
        prev["EMA50"] <= prev["EMA200"]
        and last["EMA50"] > last["EMA200"]
    )


def is_strong_signal(df):
    if not is_golden_cross(df):
        return False

    last = df.iloc[-1]

    return (
        55 <= last["RSI"] <= 70
        and last["MACD"] > last["MACD_SIGNAL"]
        and last["volume"] > last["AVG_VOLUME"] * 1.5
    )
