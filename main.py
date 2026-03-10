from keep_alive import keep_alive
import yfinance as yf
import pandas as pd
import ta
import time
from telegram import Bot

# ------------ CONFIG ------------
symbol = "EURUSD=X"
interval = "1m"
period = "1d"

TELEGRAM_BOT_TOKEN = "8662158957:AAFaJCIWh_o199xP0eEDBXB0JPE7NicGwq"
TELEGRAM_CHAT_ID = "1003858378052"
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# ---------- CANDLE PATTERNS ----------
def candle_pattern(c, p):
    if p['Close'] < p['Open'] and c['Close'] > c['Open']:
        return "Bullish Engulfing"
    elif p['Close'] > p['Open'] and c['Close'] < c['Open']:
        return "Bearish Engulfing"
    return "No clear pattern"

# -------- MAIN LOOP --------
keep_alive()

while True:
    try:
        df = yf.download(symbol, interval=interval, period=period)
        
        # Indicators
        df['rsi'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        df['ema9'] = ta.trend.EMAIndicator(df['Close'], window=9).ema_indicator()
        df['ema21'] = ta.trend.EMAIndicator(df['Close'], window=21).ema_indicator()
        macd = ta.trend.MACD(df['Close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        df['stoch'] = stoch.stoch()

        # Price action
        recent_high = df['High'].iloc[-20:].max()
        recent_low = df['Low'].iloc[-20:].min()
        current_close = df['Close'].iloc[-1]
        
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        pattern = candle_pattern(last_candle, prev_candle)

        score = 0
        reasons = []

        if df['rsi'].iloc[-1] < 30:
            score += 1; reasons.append("RSI oversold")
        if df['ema9'].iloc[-1] > df['ema21'].iloc[-1]:
            score += 1; reasons.append("Uptrend EMA")
        if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
            score += 1; reasons.append("MACD bullish")
        if "Bullish" in pattern:
            score += 1; reasons.append("Bullish candle")

        result = "Bullish" if score >= 2 else "Neutral" if score == 1 else "Bearish"

        message = (
            f"Symbol: {symbol}\n"
            f"Close: {current_close}\n"
            f"Score: {score}\n"
            f"Bias: {result}\n"
            f"Reasons: {', '.join(reasons)}"
        )

        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print(message)

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
