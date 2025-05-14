import os
from flask import Flask, jsonify, request, send_from_directory
from twilio.rest import Client
from datetime import datetime, timedelta


app = Flask(__name__)

account_sid = 'AC52238e1364629657cfedc72c6fcdc23'
auth_token = 'ab606a004940ee0e47158cb7d7fee32'
client = Client(account_sid, auth_token)

def get_monthly_call_usage_with_daily_breakdown(month, year):
    total_duration_seconds = 0
    current_day = datetime(year, month, 1)
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    daily_breakdown = []
    while current_day < next_month:
        next_day = current_day + timedelta(days=1)
        calls = client.calls.list(
            start_time_after=current_day,
            start_time_before=next_day,
            limit=1000
        )
        daily_duration_seconds = sum(int(record.duration) for record in calls if record.duration)
        daily_minutes = daily_duration_seconds / 60
        total_duration_seconds += daily_duration_seconds
        daily_breakdown.append({
            "date": current_day.strftime('%Y-%m-%d'),
            "minutes": round(daily_minutes, 2)
        })
        current_day = next_day
    total_minutes = total_duration_seconds / 60
    return {
        "total_minutes": round(total_minutes, 2),
        "daily_breakdown": daily_breakdown
    }

@app.route('/api/call-usage')
def call_usage():
    month = int(request.args.get('month', datetime.now().month))
    year = int(request.args.get('year', datetime.now().year))
    data = get_monthly_call_usage_with_daily_breakdown(month, year)
    return jsonify(data)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
