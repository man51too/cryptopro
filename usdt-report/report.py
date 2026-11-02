#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""report.py — گزارش دوره‌ای تتر و بازدهی (اجرای مخصوص GitHub Actions).

- منبع داده: Bybit Demo API (مستقیم از رانر GitHub — IP آزاد)
- خروجی: پیام فارسی حرفه‌ای → تلگرام
- تاریخچه: usdt-report/history.json (برای مقایسه با گزارش قبلی)

Config از env: BYBIT_KEY, BYBIT_SECRET, TG_TOKEN, TG_CHAT
"""
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API_KEY = os.environ.get("BYBIT_KEY", "")
API_SECRET = os.environ.get("BYBIT_SECRET", "")
TG_TOKEN = os.environ.get("TG_TOKEN", "")
TG_CHAT = os.environ.get("TG_CHAT", "")
BYBIT_BASE = "https://api-demo.bybit.com"
HERE = os.path.dirname(os.path.abspath(__file__))
HIST_PATH = os.path.join(HERE, "history.json")
TZ = timezone(timedelta(hours=3, minutes=30))  # Asia/Tehran (بدون DST)

WINDOWS = [("۱ ساعت", 3600), ("۲۴ ساعت", 86400), ("۷ روز", 7 * 86400), ("۳۰ روز", 30 * 86400)]
FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def fa(x):
    return str(x).translate(FA)


def fnum(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def amt(v):
    return f"{v:,.2f}"


def money(v):
    return f"{'+' if v >= 0 else '-'}{abs(v):,.2f}"


def pct(p):
    return f"{'+' if p >= 0 else '-'}{abs(p):.2f}%"


def g2j(gy, gm, gd):
    """گرگوری → جلالی (استاندارد، تست‌شده)."""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100
            + (gy2 + 399) // 400 + gd + g_d_m[gm - 1])
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return jy, jm, jd


def http_json(url, data=None, headers=None, timeout=25, tries=3):
    last = ""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            try:
                return json.loads(body)
            except Exception:
                last = f"HTTP {e.code}: {body[:160]}"
        except Exception as e:
            last = str(e)
        time.sleep(4 * (i + 1))
    raise RuntimeError(f"request failed ({url[:70]}): {last}")


def bybit_get(path, params=None):
    qs = urllib.parse.urlencode(params or {})
    for attempt in range(2):
        ts = str(int(time.time() * 1000))
        if attempt == 1:
            try:
                t = http_json(BYBIT_BASE + "/v5/market/time", timeout=10, tries=2)
                ts = str(int(t["result"]["timeSecond"]) * 1000)
            except Exception:
                pass
        recv = "5000"
        sign = hmac.new(API_SECRET.encode(), (ts + API_KEY + recv + qs).encode(),
                        hashlib.sha256).hexdigest()
        headers = {
            "X-BAPI-API-KEY": API_KEY,
            "X-BAPI-TIMESTAMP": ts,
            "X-BAPI-RECV-WINDOW": recv,
            "X-BAPI-SIGN": sign,
        }
        d = http_json(BYBIT_BASE + path + ("?" + qs if qs else ""), headers=headers, tries=2)
        if d.get("retCode") == 0:
            return d.get("result") or {}
        if d.get("retCode") in (10001, 10002):
            continue
        raise RuntimeError(f"Bybit {path}: retCode={d.get('retCode')} {d.get('retMsg')}")
    raise RuntimeError(f"Bybit {path}: time sync failed")


def get_wallet():
    last_err = None
    for acct_type in ("UNIFIED", "CONTRACT"):
        try:
            res = bybit_get("/v5/account/wallet-balance", {"accountType": acct_type})
        except RuntimeError as e:
            last_err = e
            continue
        rows = res.get("list") or []
        if not rows:
            continue
        acct = rows[0]
        usdt = next((c for c in (acct.get("coin") or []) if c.get("coin") == "USDT"), {})
        if not usdt and not acct.get("totalEquity"):
            continue
        free = fnum(usdt.get("availableToWithdraw"))
        if free is None:
            free = fnum(usdt.get("availableBalance"))
        if free is None:
            free = fnum(acct.get("totalAvailableBalance"))
        if free is None:
            free = fnum(usdt.get("walletBalance"), 0.0)
        equity = fnum(usdt.get("equity"))
        if equity is None:
            equity = fnum(acct.get("totalEquity"), 0.0)
        return {
            "equity": equity,
            "free": free,
            "margin": fnum(usdt.get("totalPositionIM"), 0.0) + fnum(usdt.get("totalOrderIM"), 0.0),
            "upnl": fnum(usdt.get("unrealisedPnl"), 0.0),
            "cum": fnum(usdt.get("cumRealisedPnl"), 0.0),
        }
    raise RuntimeError(f"wallet-balance failed: {last_err}")


def get_positions():
    res = bybit_get("/v5/position/list", {"category": "linear", "settleCoin": "USDT"})
    out = []
    for p in res.get("list") or []:
        if abs(fnum(p.get("size"), 0.0)) < 1e-12:
            continue
        out.append({
            "symbol": p.get("symbol", "?"),
            "side": p.get("side", "?"),
            "upnl": fnum(p.get("unrealisedPnl"), 0.0),
        })
    out.sort(key=lambda x: abs(x["upnl"]), reverse=True)
    return out


def fetch_closed(now_ms):
    start = now_ms - 31 * 86400 * 1000
    out, cursor, pages = [], "", 0
    while pages < 12:
        params = {"category": "linear", "startTime": start, "endTime": now_ms, "limit": 200}
        if cursor:
            params["cursor"] = cursor
        res = bybit_get("/v5/position/closed-pnl", params)
        lst = res.get("list") or []
        out.extend(lst)
        cursor = res.get("nextPageCursor") or ""
        pages += 1
        if not cursor or not lst:
            break
    return out


def win_stats(recs, now_s, win_s):
    cut = now_s - win_s
    pnls = [fnum(r.get("closedPnl"), 0.0) for r in recs
            if fnum(r.get("createdTime"), 0.0) / 1000.0 >= cut]
    n = len(pnls)
    total = sum(pnls)
    wins = sum(1 for p in pnls if p > 0)
    wr = (wins / n * 100.0) if n else 0.0
    return total, n, wr


def update_history(equity, now_s):
    hist = []
    if os.path.exists(HIST_PATH):
        try:
            with open(HIST_PATH, "r", encoding="utf-8") as f:
                hist = json.load(f)
        except Exception:
            hist = []
    prev = hist[-1] if hist else None
    hist.append({"t": now_s, "eq": round(equity, 4)})
    try:
        hist = hist[-400:]
        tmp = HIST_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(hist, f, ensure_ascii=False)
        os.replace(tmp, HIST_PATH)
    except Exception:
        pass
    return prev


def build_text(w, positions, recs, now_s, prev):
    dt = datetime.now(TZ)
    jy, jm, jd = g2j(dt.year, dt.month, dt.day)
    eq = w["equity"]
    L = []
    L.append("📊 <b>گزارش دوره‌ای کریپتوپرو — تتر و بازدهی</b>")
    L.append(f"🗓 {fa(jy)}/{fa(f'{jm:02d}')}/{fa(f'{jd:02d}')} • 🕐 {fa(dt.strftime('%H:%M'))} (تهران)")
    L.append("")
    L.append("💠 <b>موجودی (Bybit — حساب دمو)</b>")
    L.append(f"• ارزش کل حساب: <b>{amt(eq)} USDT</b>")
    L.append(f"• موجودی آزاد: {amt(w['free'])} USDT")
    L.append(f"• مارجین درگیر: {amt(w['margin'])} USDT")
    L.append(f"• سود/زیان شناور: {money(w['upnl'])} USDT")
    L.append(f"• سود تجمعی کل: {money(w['cum'])} USDT")
    L.append("")
    L.append("📈 <b>بازدهی دوره‌ای</b> (سود محقق‌شدهٔ معاملات)")
    for label, win in WINDOWS:
        pnl, n, wr = win_stats(recs, now_s, win)
        base = eq - pnl
        line = f"• {label}: {money(pnl)} USDT"
        if base > 1:
            line += f" ({pct(pnl / base * 100)})"
        if n:
            line += f" | {fa(n)} معامله | برد {fa(round(wr))}٪"
        else:
            line += " | بدون معامله"
        L.append(line)
    L.append("")
    if positions:
        L.append(f"📍 <b>پوزیشن‌های باز</b> ({fa(len(positions))}):")
        for p in positions[:8]:
            arrow = "🔼" if p["side"] == "Buy" else "🔽"
            side_fa = "خرید" if p["side"] == "Buy" else "فروش"
            L.append(f"• {p['symbol']} {arrow} {side_fa} | {money(p['upnl'])} USDT")
        if len(positions) > 8:
            L.append(f"• و {fa(len(positions) - 8)} پوزیشن دیگر…")
    else:
        L.append("📍 پوزیشن بازی وجود ندارد")
    L.append("")
    if prev and now_s - prev.get("t", 0) > 300:
        pe = fnum(prev.get("eq"), 0.0)
        d = eq - pe
        line = f"🔄 نسبت به گزارش قبلی: {money(d)} USDT"
        if pe > 1:
            line += f" ({pct(d / pe * 100)})"
        L.append(line)
    L.append("🤖 CryptoPro • ارسال خودکار هر ۵ ساعت")
    return "\n".join(L)


def send_tg(text):
    data = urllib.parse.urlencode({
        "chat_id": TG_CHAT, "text": text,
        "parse_mode": "HTML", "disable_web_page_preview": "true",
    }).encode()
    last = ""
    for _ in range(3):
        try:
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data=data)
            with urllib.request.urlopen(req, timeout=25) as r:
                out = json.loads(r.read().decode())
            if out.get("ok"):
                return True
            last = f"{out.get('error_code')}: {out.get('description')}"
            if out.get("error_code") == 429:
                time.sleep(40)
                continue
            break
        except Exception as e:
            last = str(e)
            time.sleep(8)
    raise RuntimeError("telegram send failed: " + last)


def main():
    missing = [k for k, v in (("BYBIT_KEY", API_KEY), ("BYBIT_SECRET", API_SECRET),
                              ("TG_TOKEN", TG_TOKEN), ("TG_CHAT", TG_CHAT)) if not v]
    if missing:
        raise RuntimeError(f"missing env: {','.join(missing)}")
    now_ms = int(time.time() * 1000)
    now_s = now_ms // 1000
    w = get_wallet()
    positions = get_positions()
    recs = fetch_closed(now_ms)
    prev = update_history(w["equity"], now_s)
    text = build_text(w, positions, recs, now_s, prev)
    send_tg(text)
    print("TELEGRAM_OK")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"REPORT_FAIL: {e}")
        sys.exit(1)
