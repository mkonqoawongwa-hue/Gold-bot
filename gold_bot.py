hi import yfinance as yf
import pandas as pd
import requests, time
from datetime import datetime
by
# ====== YOUR LIVE DETAILS - ALREADY FILLED ======
PHONE = "+27685933351"
APIKEY = "9118355"
# =================================================

def send_wa(msg):
    txt = f"GOLD V8 {datetime.now().strftime('%H:%M')} {msg}"
    txt_enc = txt.replace(" ", "%20").replace("\n", "%0A")
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={txt_enc}&apikey={APIKEY}"
    requests.get(url, timeout=15)
    print(f"SENT: {msg}")

def get_data(interval, period):
    df = yf.download("GC=F", interval=interval, period=period, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    return df

def bull_eng(df):
    o1, c1 = df['Open'].iloc[-2], df['Close'].iloc[-2]
    o2, c2 = df['Open'].iloc[-1], df['Close'].iloc[-1]
    return c1 < o1 and c2 > o2 and c2 > o1 and o2 < c1

def bear_eng(df):
    o1, c1 = df['Open'].iloc[-2], df['Close'].iloc[-2]
    o2, c2 = df['Open'].iloc[-1], df['Close'].iloc[-1]
    return c1 > o1 and c2 < o2 and o2 > c1 and c2 < o1

def is_overlap():
    h = datetime.now().hour  # SAST = GMT+2
    return h in [15,16]  # 15:30-17:00 best

def run():
    send_wa("BOT ONLINE - V8 FINAL ACTIVE - 5m+15m Sniper ALL DAY + Scalper OVERLAP 15:30-17:00 - Monitoring XAUUSD for 3rd touch + engulfing + BO Retest - FundedNext $15k")
    
    scalp_today = 0
    last_alert = 0
    last_day = datetime.now().day
    
    while True:
        try:
            now = datetime.now()
            if now.day != last_day:
                scalp_today = 0
                last_day = now.day

            h1 = get_data("1h", "10d")
            h4 = get_data("4h", "20d")
            m15 = get_data("15m", "5d")
            m5 = get_data("5m", "2d")
            
            if h1.empty or m5.empty:
                time.sleep(300); continue
            
            h1['EMA200'] = h1['Close'].ewm(span=200).mean()
            is_bull = float(h1['Close'].iloc[-1]) > float(h1['EMA200'].iloc[-1])
            trend = "UP" if is_bull else "DOWN"
            
            last_high = float(h1['High'].tail(20).max())
            last_low = float(h1['Low'].tail(20).min())
            price = float(m5['Close'].iloc[-1])
            
            touches = sum(abs(h1['Low'].tail(60) - h1['EMA200'].tail(60)) < 6) if is_bull else sum(abs(h1['High'].tail(60) - h1['EMA200'].tail(60)) < 6)
            
            if time.time() - last_alert < 600:
                time.sleep(60); continue

            # SNIPER - 5m/15m - ALL SESSIONS
            if is_bull and touches >= 2 and (bull_eng(m5) or bull_eng(m15)):
                send_wa(f"✅ SNIPER BUY - 5m/15m - HIGH PROB - Trend {trend} WITH trend - 3rd Touch {touches} + Bull Engulfing 5m:{bull_eng(m5)} 15m:{bull_eng(m15)} H4:{bull_eng(h4)} - Price {price:.2f} - BUY XAUUSD - SL $2 below - TP 1:2.5 - Lot 0.30 - Will ping BE at +$4")
                last_alert = time.time()
            
            if not is_bull and touches >= 2 and (bear_eng(m5) or bear_eng(m15)):
                send_wa(f"✅ SNIPER SELL - 5m/15m - Trend {trend} - 3rd Touch + Bear Engulf - Price {price:.2f} - SELL XAUUSD - SL $2 - TP 1:2.5 Lot 0.30")
                last_alert = time.time()

            # SCALPER - OVERLAP ONLY 15:30-17:00
            if is_overlap() and scalp_today < 3:
                m5_high = float(m5['High'].tail(20).max())
                m5_low = float(m5['Low'].tail(20).min())
                if is_bull and price > m5_high and bull_eng(m5):
                    send_wa(f"⚡ SCALP BUY - OVERLAP 15:30-17:00 - Breakout {m5_high:.2f} + Engulf - Price {price:.2f} - BUY QUICK - SL $1.5 TP 1:1.5 Lot 0.15")
                    scalp_today += 1
                    last_alert = time.time()
                if not is_bull and price < m5_low and bear_eng(m5):
                    send_wa(f"⚡ SCALP SELL - OVERLAP - Breakdown {m5_low:.2f} - Price {price:.2f} - SELL QUICK SL $1.5 TP 1:1.5 Lot 0.15")
                    scalp_today += 1
                    last_alert = time.time()

            # BO+RETEST - ALLOWED FLIP
            if float(m15['Close'].iloc[-1]) > last_high + 2 and bull_eng(m15):
                send_wa(f"⚠️ BO+RETEST BUY FLIP - Res {last_high:.2f} BROKEN - Price {price:.2f} - BUY NOW")
                last_alert = time.time()
            if float(m15['Close'].iloc[-1]) < last_low - 2 and bear_eng(m15):
                send_wa(f"⚠️ BO+RETEST SELL FLIP - Sup {last_low:.2f} BROKEN - SELL NOW {price:.2f}")
                last_alert = time.time()

        except Exception as e:
            print("Error", e)
        time.sleep(300)

if __name__ == "__main__":
    run()
