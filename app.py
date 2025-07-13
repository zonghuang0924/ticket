from flask import Flask, render_template, request
import math

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            rA = float(request.form['rA'])
            rB = float(request.form['rB'])
            total = float(request.form['total'])
            result = analyze_arbitrage(rA, rB, total)
        except:
            result = 'error'
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
