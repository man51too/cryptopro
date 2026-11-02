#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""report.py — گزارش دوره‌ای تتر و بازدهی (GitHub Actions).

منبع: موتور AXIOM Delta روی botkeep (REST /metrics + /export/trades) — بدون محدودیت جغرافیایی Bybit.
Config از env: AXIOM_ACCESS_KEY, TG_TOKEN, TG_CHAT
Dedup: اگر آخرین گزارش کمتر از ۴.۵ ساعت قبل ثبت شده باشد، ارسال نمی‌کند (SKIP_RECENT).
"""
import csv
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

ENGINE_BASE = "https://cryptopro.bot-keep.xyz"
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


def fetch_text(url, timeout=60, tries=2):
    last = ""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:200]
            last = f"HTTP {e.code}: {body}"
            if e.code == 401:
                break
        except Exception as e:
            last = str(e)
        time.sleep(5 * (i + 1))
    raise RuntimeError(f"fetch failed ({url.split('?')[0]}): {last}")


def parse_metrics(text):
    out = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-z_]+)(\{[^}]*\})?\s+([-0-9.eE+]+)\s*$", line.strip())
        if m:
            out[m.group(1)] = float(m.group(3))
    return out


def parse_trades(csv_text):
    out = []
    rdr = csv.DictReader(io.StringIO(csv_text))
    for row in rdr:
        et = (row.get("exitTime") or "").strip()
        if not et:
            continue
        try:
            t = datetime.fromisoformat(et.replace("Z", "+00:00")).timestamp()
        except Exception:
            continue
        out.append((t, fnum(row.get("pnl"), 0.0) or 0.0))
    return out


def win_stats(trades, now_s, win_s):
    cut = now_s - win_s
    pnls = [p for t, p in trades if t >= cut]
    n = len(pnls)
    total = sum(pnls)
    wins = sum(1 for p in pnls if p > 0)
    wr = (wins / n * 100.0) if n else 0.0
    return total, n, wr


def load_last_ts():
    try:
        with open(HIST_PATH, "r", encoding="utf-8") as f:
            h = json.load(f)
        return h[-1].get("t", 0) if h else 0
    except Exception:
        return 0


def save_history(equity, now_s):
    h = []
    if os.path.exists(HIST_PATH):
        try:
            with open(HIST_PATH, "r", encoding="utf-8") as f:
                h = json.load(f)
        except Exception:
            h = []
    h.append({"t": now_s, "eq": round(equity, 4)})
    tmp = HIST_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(h[-400:], f, ensure_ascii=False)
    os.replace(tmp, HIST_PATH)


def build_text(m, trades, now_s, prev_eq, prev_ts):
    dt = datetime.now(TZ)
    jy, jm, jd = g2j(dt.year, dt.month, dt.day)
    eq = m.get("axiom_equity_usdt", 0.0)
    total_pnl = m.get("axiom_total_pnl_usdt", 0.0)
    upnl = m.get("axiom_unrealized_pnl_usdt", 0.0)
    day_pnl = m.get("axiom_day_pnl_usdt", 0.0)
    dd_max = m.get("axiom_drawdown_max", 0.0)
    open_pos = int(m.get("axiom_open_positions", 0))
    n_closed = int(m.get("axiom_trades_closed_total", 0))
    wr_all = m.get("axiom_win_rate", 0.0) * 100.0
    pf = m.get("axiom_profit_factor", 0.0)
    gross = m.get("axiom_gross_exposure", 0.0)

    L = []
    L.append("📊 <b>گزارش دوره‌ای کریپتوپرو — تتر و بازدهی</b>")
    L.append(f"🗓 {fa(jy)}/{fa(f'{jm:02d}')}/{fa(f'{jd:02d}')} • 🕐 {fa(dt.strftime('%H:%M'))} (تهران)")
    L.append("")
    L.append("💰 <b>موجودی (Bybit دمو — موتور AXIOM)</b>")
    L.append(f"• ارزش کل حساب: <b>{amt(eq)} USDT</b>")
    start_eq = eq - total_pnl
    line = f"• سود کل از شروع: {money(total_pnl)} USDT"
    if start_eq > 1:
        line += f" ({pct(total_pnl / start_eq * 100)})"
    L.append(line)
    L.append(f"• سود امروز: {money(day_pnl)} USDT")
    L.append(f"• سود/زیان شناور: {money(upnl)} USDT")
    if gross > 0:
        L.append(f"• حجم درگیر: {amt(gross)} USDT | پوزیشن باز: {fa(open_pos)}")
    L.append(f"• حداکثر افت سرمایه: {fa(round(dd_max * 100, 2))}٪")
    L.append("")
    L.append("📈 <b>بازدهی دوره‌ای</b> (سود محقق‌شدهٔ معاملات)")
    for label, win in WINDOWS:
        pnl, n, wr = win_stats(trades, now_s, win)
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
    L.append("🎯 <b>عملکرد کلی موتور</b>")
    L.append(f"• معاملات بسته‌شده: {fa(n_closed)} | وین‌ریت: {fa(round(wr_all, 1))}٪")
    L.append(f"• پروفیت فکتور: {fa(round(pf, 2))}")
    if prev_eq and now_s - prev_ts > 300:
        d = eq - prev_eq
        line = f"🔄 نسبت به گزارش قبلی: {money(d)} USDT"
        if prev_eq > 1:
            line += f" ({pct(d / prev_eq * 100)})"
        L.append(line)
    L.append("")
    L.append("🤖 CryptoPro • ارسال خودکار هر ۵ ساعت")
    return "\n".join(L)


def send_tg(text):
    import urllib.parse
    data = urllib.parse.urlencode({
        "chat_id": os.environ.get("TG_CHAT", ""),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    last = ""
    for _ in range(3):
        try:
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{os.environ.get('TG_TOKEN', '')}/sendMessage",
                data=data)
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
    key = (os.environ.get("AXIOM_ACCESS_KEY") or "").strip()
    if not key:
        raise RuntimeError("missing env AXIOM_ACCESS_KEY")
    if not os.environ.get("TG_TOKEN") or not os.environ.get("TG_CHAT"):
        raise RuntimeError("missing env TG_TOKEN/TG_CHAT")

    # Dedup: اگر گزارش جدیدی طی ۴.۵ ساعت گذشته ثبت شده، ارسال نکن
    last_ts = load_last_ts()
    if time.time() - last_ts < 4.5 * 3600:
        print("SKIP_RECENT")
        return 0

    now_s = int(time.time())
    m = parse_metrics(fetch_text(f"{ENGINE_BASE}/metrics?key={key}", timeout=30))
    if "axiom_equity_usdt" not in m:
        raise RuntimeError("metrics ok but no equity field")
    csv_text = fetch_text(f"{ENGINE_BASE}/export/trades?key={key}", timeout=90)
    trades = parse_trades(csv_text)

    prev_eq = 0.0
    try:
        with open(HIST_PATH, "r", encoding="utf-8") as f:
            h = json.load(f)
        prev_eq = fnum(h[-1].get("eq"), 0.0) if h else 0.0
    except Exception:
        pass

    text = build_text(m, trades, now_s, prev_eq, last_ts)
    save_history(m["axiom_equity_usdt"], now_s)
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
