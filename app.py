# app.py
from flask import Flask, render_template, request, jsonify
import requests
import sqlite3
import datetime

app = Flask(__name__)

# 套利計算
def analyze_arbitrage(rA, rB, total):
    a_ratio = rB / (rA + rB)
    b_ratio = rA / (rA + rB)
    A = total * a_ratio
    B = total * b_ratio
    win_A = A * rA - (A + B)
    win_B = B * rB - (A + B)
    return {
        'bet_A': round(A, 2),
        'bet_B': round(B, 2),
        'profit_A': round(win_A, 2),
        'profit_B': round(win_B, 2),
        'is_safe': win_A > 0 and win_B > 0
    }

# 初始化資料庫
conn = sqlite3.connect('history.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    sport TEXT,
    oddsA REAL,
    oddsB REAL,
    total REAL,
    betA REAL,
    betB REAL,
    profitA REAL,
    profitB REAL,
    is_safe INTEGER
)''')
conn.commit()

# 主頁面
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    sport_list = ['tennis', 'football', 'basketball', 'baseball', 'volleyball']
    if request.method == 'POST':
        try:
            rA = float(request.form['rA'])
            rB = float(request.form['rB'])
            total = float(request.form['total'])
            sport = request.form.get('sport', 'tennis')
            result = analyze_arbitrage(rA, rB, total)
            c.execute("""
                INSERT INTO history (timestamp, sport, oddsA, oddsB, total, betA, betB, profitA, profitB, is_safe)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (datetime.datetime.now().isoformat(), sport, rA, rB, total,
                 result['bet_A'], result['bet_B'], result['profit_A'], result['profit_B'], int(result['is_safe'])))
            conn.commit()
        except:
            result = 'error'
    return render_template('index.html', result=result, sports=sport_list)

# 回傳指定運動項目多場比賽供前端選擇
@app.route('/get_matches')
def get_matches():
    sport = request.args.get('sport', 'tennis')
    url = "https://www.sportslottery.com.tw/web/guest/json/sport/schedule.json"
    matches = []
    try:
        res = requests.get(url)
        data = res.json()
        for match in data.get('page', {}).get('contentItems', []):
            if match.get('eventSportName', '').lower() == sport.lower():
                try:
                    odds1 = float(match.get('odds1', 0))
                    odds2 = float(match.get('odds2', 0))
                    name1 = match.get('competitorName1', '').strip()
                    name2 = match.get('competitorName2', '').strip()
                    if name1 and name2 and odds1 > 1 and odds2 > 1:
                        matches.append({
                            'id': f"{name1} vs {name2}",
                            'team1': name1,
                            'team2': name2,
                            'odds1': odds1,
                            'odds2': odds2
                        })
                except:
                    continue
        return jsonify(matches[:10])
    except:
        return jsonify([])

# 歷史紀錄頁面
@app.route('/history')
def history():
    c.execute("SELECT timestamp, sport, oddsA, oddsB, total, betA, betB, profitA, profitB, is_safe FROM history ORDER BY id DESC")
    rows = c.fetchall()
    return render_template('history.html', rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
