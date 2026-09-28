#!/usr/bin/env bash
# ============================================================
# Phoenix Guardian — نگهبان فونیکس (v7.7)
# نگهبان بیرونیِ همیشه‌روشن برای پلتفرم z.ai
#
# منطق (هر ۵ دقیقه با GitHub Actions):
#   ۱) سلامت پلتفرم را چک می‌کند (GET /api/cron?src=github — پینگ ثبت + ترمیم موتور)
#   ۲) اگر قطع بود → ۳ پینگ پیاپی اضطراری (بیدارسازی سرتاب سرد) → بازبینی
#   ۳) اگر برنگشت → API رسمی ری‌استارت workspace زد z.ai را صدا می‌زند
#   ۴) ۹۰ ثانیه صبر و بازبینی → اگر برگشت: پیام «احیای خودکار»
#   ۵) اگر برنگشت: هشدار تلگرام با لینک بیداری دستی
#   ۶) همهٔ رخدادها در guardian-state.json ثبت و commit می‌شود
#
# محرمانه‌های لازم (Repository Secrets):
#   PLATFORM_URL   آدرس پلتفرم        (مثال: https://xxxx.space-z.ai)
#   ZAI_TOKEN      توکن z.ai          (اختیاری — از Local Storage مرورگر)
#   ZAI_CHAT_ID    شناسه چت z.ai      (از آدرس صفحه چت)
#   TG_BOT_TOKEN   توکن ربات تلگرام
#   TG_CHAT_ID     شناسه چت تلگرام
# ============================================================
set -uo pipefail

PLATFORM_URL="${PLATFORM_URL:-}"
ZAI_TOKEN="${ZAI_TOKEN:-}"
ZAI_CHAT_ID="${ZAI_CHAT_ID:-}"
TG_BOT_TOKEN="${TG_BOT_TOKEN:-}"
TG_CHAT_ID="${TG_CHAT_ID:-}"

STATE_FILE="guardian-state.json"
WAKE_URL="${WAKE_URL:-https://chat.z.ai/api/v1/web-dev/workspaces/restart}"
REPEAT_ALERT_SEC="${REPEAT_ALERT_SEC:-1800}"   # تکرار هشدار قطعی: هر ۳۰ دقیقه
WAKE_WAIT_SEC="${WAKE_WAIT_SEC:-90}"        # مهلت بوت شدن موتور پس از بیدارسازی
EVENTS_MAX="${EVENTS_MAX:-30}"
# ---- v7.7 ----
HEALTH_PATH="${HEALTH_PATH:-/api/cron?src=github}"   # اندپوینت ثبت-کنندهٔ پینگ (به‌جای /api/health)
CHECK_RETRY_SEC="${CHECK_RETRY_SEC:-10}"     # وقفهٔ بین تلاش‌های چک سلامت
BURST_GAP_SEC="${BURST_GAP_SEC:-12}"         # فاصلهٔ پینگ‌های اضطراری
BURST_CONFIRM_SEC="${BURST_CONFIRM_SEC:-15}" # مهلت تثبیت پس از بیداری با پینگ
GUARD_UA="phoenix-guardian/7.7"              # شناسهٔ UA برای آمار پلتفرم

now_iso()  { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
now_epoch() { date +%s; }
log() { echo "[phoenix $(now_iso)] $*"; }

# ---------- تلگرام ----------
tg_send() { # $1 = متن HTML
  [ -z "${TG_BOT_TOKEN}" ] || [ -z "${TG_CHAT_ID}" ] && return 0
  curl -sS -m 20 -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg c "${TG_CHAT_ID}" --arg t "$1" '{chat_id:$c, text:$t, parse_mode:"HTML"}')" \
    >/dev/null 2>&1 || true
}

# ---------- پیام آزمایشی (اجرای دستی workflow_dispatch با notify_test=true) ----------
if [ "${NOTIFY_TEST:-}" = "true" ]; then
  tg_send "🧪 <b>تست نگهبان فونیکس</b>

✅ اتصال تلگرام سالم است — این یک پیام آزمایشی است.
🕐 $(now_iso)
⚙️ چرخهٔ نگهبانی معمولی نیز همین حالا اجرا شد."
fi

# ---------- سلامت پلتفرم ----------
# v7.7 — اندپوینت /api/cron?src=github به‌جای /api/health، سه مزیت:
#   ۱) همیشه ۲۰۰ برمی‌گرداند (health تا بوت موتور 503 می‌دهد → هشدار کاذب)
#   ۲) پینگ در آمار پلتفرم ثبت می‌شود (لایهٔ نگه‌دارندهٔ چهارم)
#   ۳) موتور خفته را خودترمیم می‌کند
# تحمل سرتاب سرد (~۴۰ ثانیه): ۳ تلاش × ۳۰ ثانیه با وقفه
check_health() {
  local code i
  for i in 1 2 3; do
    code=$(curl -sS -m 30 -A "${GUARD_UA}" -o /tmp/phoenix_check.json -w '%{http_code}' \
      "${PLATFORM_URL%/}${HEALTH_PATH}" 2>/dev/null || echo 000)
    if [ "${code}" = "200" ] && grep -q '"pong"' /tmp/phoenix_check.json 2>/dev/null; then
      return 0
    fi
    [ "${i}" = "3" ] && break
    sleep "${CHECK_RETRY_SEC}"
  done
  return 1
}

# ---------- پینگ اضطراری: بیدارسازی سرور خفته (سرتاب سرد FC) ----------
burst_ping() {
  local i
  for i in 1 2 3; do
    curl -sS -m 25 -A "${GUARD_UA}" -o /dev/null \
      "${PLATFORM_URL%/}${HEALTH_PATH}" 2>/dev/null || true
    sleep "${BURST_GAP_SEC}"
  done
}

# ---------- بیدارسازی: نردبان دو مرحله‌ای ----------
WAKE_METHOD="none"
try_wake() {
  # مرحلهٔ ۱ — پینگ‌های پیاپی: هر GET خودش درخواست بیدارکننده است
  burst_ping
  if check_health; then
    WAKE_METHOD="ping-burst"
    log "woke via GET burst"
    return 0
  fi
  # مرحلهٔ ۲ — API رسمی ری‌استارت z.ai
  if [ -z "${ZAI_TOKEN}" ] || [ -z "${ZAI_CHAT_ID}" ]; then
    log "wake skipped: ZAI_TOKEN/ZAI_CHAT_ID not configured"
    return 2   # تنظیم نشده
  fi
  local code body
  code=$(curl -sS -m 30 -o /tmp/phoenix_wake.json -w '%{http_code}' \
    -X POST "${WAKE_URL}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${ZAI_TOKEN}" \
    -d "$(jq -n --arg c "${ZAI_CHAT_ID}" '{chatId:$c}')" 2>/dev/null || echo 000)
  body=$(head -c 300 /tmp/phoenix_wake.json 2>/dev/null || true)
  log "wake http=${code} body=${body}"
  if [ "${code}" = "200" ]; then WAKE_METHOD="zai-restart"; return 0; fi
  if [ "${code}" = "401" ]; then return 3; fi   # توکن منقضی
  return 1
}

# ---------- بارگذاری وضعیت ----------
if [ -f "${STATE_FILE}" ] && jq -e . "${STATE_FILE}" >/dev/null 2>&1; then
  STATE=$(cat "${STATE_FILE}")
else
  STATE='{"state":"unknown","since":null,"lastCheck":null,"lastAlertAt":null,"lastWake401AlertAt":null,"events":[]}'
fi

prev_state=$(jq -r '.state'      <<<"${STATE}")
prev_since=$(jq -r '.since // ""' <<<"${STATE}")
last_alert=$(jq -r '.lastAlertAt // ""' <<<"${STATE}")
last_401=$(jq -r '.lastWake401AlertAt // ""' <<<"${STATE}")
events=$(jq -c '.events // []'    <<<"${STATE}")

ts=$(now_iso)
ts_e=$(now_epoch)
down_min=0
if [ -n "${prev_since}" ]; then
  down_min=$(( (ts_e - $(date -d "${prev_since}" +%s)) / 60 ))
fi

add_event() { # $1=type $2=extra-json
  local extra="${2:-}"
  [ -z "${extra}" ] && extra='{}'
  events=$(jq -c --arg t "$1" --arg at "${ts}" --argjson extra "${extra}" \
    '. + [{type:$t, at:$at} + $extra] | .[-'"${EVENTS_MAX}"':]' <<<"${events}")
}

log "cycle start: prev=${prev_state} up-check..."

# ============================================================
# چرخهٔ اصلی
# ============================================================
if check_health; then
  log "platform UP"
  if [ "${prev_state}" = "down" ]; then
    # 🌅 بازگشت پس از قطعی
    tg_send "🌅 <b>فونیکس: پلتفرم بازگشت</b>

✅ پلتفرم دوباره آنلاین است.
⏱ مدت قطعی: <b>${down_min} دقیقه</b>
🕐 زمان بازگشت: ${ts}
⚙️ موتور تحلیل، سیگنال‌ها و معاملات کاغذی به‌صورت خودکار ادامه یافتند."
    add_event "recovered" "{\"downMin\":${down_min}}"
  fi
  NEW_STATE=$(jq -n --arg ts "${ts}" --argjson events "${events}" \
    --argjson keep_since "$(if [ "${prev_state}" = "up" ] && [ -n "${prev_since}" ]; then jq -Rn --arg s "${prev_since}" '$s'; else jq -Rn --arg s "${ts}" '$s'; fi)" \
    '{state:"up", since:$keep_since, lastCheck:$ts, lastAlertAt:null, lastWake401AlertAt:null, events:$events}')

# ------------------------------------------------------------
else
  log "platform DOWN — attempting wake..."
  wake_rc=1
  if [ "${prev_state}" != "down" ]; then
    add_event "down_started" "{}"
  fi

  try_wake; wake_rc=$?

  if [ "${wake_rc}" = "0" ]; then
    wait_sec="${WAKE_WAIT_SEC}"
    [ "${WAKE_METHOD}" = "ping-burst" ] && wait_sec="${BURST_CONFIRM_SEC}"
    log "wake ok (${WAKE_METHOD}) — waiting ${wait_sec}s for engine boot..."
    sleep "${wait_sec}"
    if check_health; then
      # 🌅 احیای خودکار موفق
      log "AUTO-RECOVERED (${WAKE_METHOD})"
      if [ "${WAKE_METHOD}" = "ping-burst" ]; then
        recover_how="• سرورِ خفته با پینگ‌های پیاپی نگهبان بیدار شد ✅"
      else
        recover_how="• قطعی تشخیص داده شد → API ری‌استارت z.ai صدا زده شد → پلتفرم بیدار شد ✅"
      fi
      tg_send "🌅 <b>فونیکس: احیای خودکار موفق</b>

🤖 نگهبان فونیکس خوابِ سندباکس را شکست:
${recover_how}
⏱ مدت قطعی: <b>${down_min} دقیقه</b>
🕐 زمان احیا: ${ts}
⚙️ موتور تحلیل، سیگنال‌ها و معاملات کاغذی ادامه یافتند."
      add_event "auto_recovered" "{\"downMin\":${down_min}}"
      NEW_STATE=$(jq -n --arg ts "${ts}" --argjson events "${events}" \
        '{state:"up", since:$ts, lastCheck:$ts, lastAlertAt:null, lastWake401AlertAt:null, events:$events}')
    else
      log "still down after wake"
      NEW_STATE="STILL_DOWN"
    fi
  else
    log "wake failed (rc=${wake_rc})"
    NEW_STATE="STILL_DOWN"
  fi

  # ---------- هنوز پایین است ----------
  if [ "${NEW_STATE}" = "STILL_DOWN" ]; then
    should_alert=1
    if [ -n "${last_alert}" ]; then
      last_alert_e=$(date -d "${last_alert}" +%s 2>/dev/null || echo 0)
      if [ $((ts_e - last_alert_e)) -lt ${REPEAT_ALERT_SEC} ]; then should_alert=0; fi
    fi
    if [ "${should_alert}" = "1" ]; then
      manual_link="https://chat.z.ai"
      [ -n "${ZAI_CHAT_ID}" ] && manual_link="https://chat.z.ai/c/${ZAI_CHAT_ID}"
      hint=""
      if [ "${wake_rc}" = "2" ]; then
        hint="⚠️ پینگ‌های اضطراری جواب نداد و بیدارسازی رسمی تنظیم نشده — ZAI_TOKEN را در Secrets بسازید (F12 ← Application ← Local Storage ← token)."
      elif [ "${wake_rc}" = "3" ]; then
        hint="🔑 توکن z.ai منقضی شده — توکن جدید را در Secret با نام ZAI_TOKEN جایگزین کنید."
      fi
      tg_send "🚨 <b>فونیکس: پلتفرم قطع است</b>

⏱ مدت قطعی تاکنون: <b>${down_min} دقیقه</b>
🕐 ${ts}
${hint}

👈 <b>بیداری دستی (۱ دقیقه):</b> چت z.ai را باز کنید و هر متنی بفرستید:
${manual_link}

با بازگشت پلتفرم، پیام تأیید دریافت می‌کنید."
    fi
    NEW_STATE=$(jq -n --arg ts "${ts}" --argjson events "${events}" \
      --arg since "$(if [ "${prev_state}" = "down" ] && [ -n "${prev_since}" ]; then echo "${prev_since}"; else echo "${ts}"; fi)" \
      --arg alert "$(if [ "${should_alert}" = "1" ]; then echo "${ts}"; else echo "${last_alert}"; fi)" \
      '{state:"down", since:$since, lastCheck:$ts, lastAlertAt:$alert, lastWake401AlertAt:null, events:$events}')
  fi
fi

# ============================================================
# ذخیره + commit (فقط اگر تغییری کرده باشد)
# ============================================================
if ! [ -f "${STATE_FILE}" ] || ! diff <(jq -S . "${STATE_FILE}" 2>/dev/null) <(jq -S . <<<"${NEW_STATE}") >/dev/null 2>&1; then
  printf '%s\n' "${NEW_STATE}" > "${STATE_FILE}"
  log "state updated: $(jq -r .state "${STATE_FILE}")"
  if [ -n "${GITHUB_WORKSPACE:-}" ]; then
    git config user.name  "phoenix-guardian[bot]"
    git config user.email "phoenix-guardian[bot]@users.noreply.github.com"
    git add "${STATE_FILE}"
    git commit -m "phoenix: $(jq -r .state "${STATE_FILE}") @ ${ts}" >/dev/null 2>&1 || true
    git push >/dev/null 2>&1 || log "git push failed (will retry next cycle)"
  fi
else
  # حتی بدون تغییر وضعیت، زمان آخرین بررسی را به‌روز کن
  NEW_STATE2=$(jq --arg ts "${ts}" '.lastCheck=$ts' <<<"${NEW_STATE}")
  if ! diff <(jq -S . "${STATE_FILE}" 2>/dev/null) <(jq -S . <<<"${NEW_STATE2}") >/dev/null 2>&1; then
    printf '%s\n' "${NEW_STATE2}" > "${STATE_FILE}"
    if [ -n "${GITHUB_WORKSPACE:-}" ]; then
      git config user.name  "phoenix-guardian[bot]"
      git config user.email "phoenix-guardian[bot]@users.noreply.github.com"
      git add "${STATE_FILE}"
      git commit -m "phoenix: check @ ${ts}" >/dev/null 2>&1 || true
      git push >/dev/null 2>&1 || log "git push failed (will retry next cycle)"
    fi
  fi
fi

log "cycle done: $(jq -r .state "${STATE_FILE}" 2>/dev/null)"

# تضمین نهایی: اگر state جدید معتبر نبود (باگ/خرابی)، state قبلی دست‌نخورده می‌ماند
if ! jq -e . "${STATE_FILE}" >/dev/null 2>&1; then
  log "FATAL: state file invalid after cycle"
  exit 1
fi
