from flask import Flask, render_template_string, request, redirect, url_for
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>SQLgard</title>
<style>
    body{background:#0e1117;color:#c9d1d9;font-family:sans-serif;text-align:center}
    h1{color:white}
    button{padding:10px 20px;font-weight:bold;border:none;border-radius:5px;margin:5px;cursor:pointer}
    .turno{background:white;color:black}
    .reset{background:#4caf50;color:white}
    table{width:85%;margin:20px auto;background:#161b22;border-collapse:collapse}
    th{background:#21262d;padding:10px}
    td{padding:10px;border-bottom:1px solid #30363d}
    .caido{color:#ff4b4b}
    .barra{background:#333;width:100px;height:10px;border-radius:5px}
    .fill{height:100%;border-radius:5px}
</style>
</head>
<body>
    <h1> SQLgard</h1>
    <h2> Uma nevoa venenosa drena a vida de todos os herois... </h2>
    <form action="/turno" method="post" style="display:inline">
        <button class="turno">PRÓXIMO TURNO</button>
    </form>
    <form action="/reset" method="post" style="display:inline">
        <button class="reset">RESETAR</button>
    </form>
    
    <table>
        <tr><th>Nome</th><th>Classe</th><th>HP</th><th>Status</th></tr>
        {% for id,nome,classe,hp_atual,hp_max,status in herois %}
        {% set pct = (hp_atual/hp_max*100)|int if hp_max>0 else 0 %}
        <tr {% if status=='CAÍDO' %}class="caido"{% endif %}>
            <td><b>{{nome}}</b></td>
            <td>{{classe}}</td>
            <td>{{hp_atual}}/{{hp_max}} 
                <div class="barra"><div class="fill" style="width:{{pct}}%;background:{{'#4caf50' if pct>50 else '#f1c40f' if pct>20 else '#ff4b4b'}}"></div></div>
            </td>
            <td><b>{{status}}</b></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def get_db():
    return oracledb.connect(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), dsn=os.getenv("DB_DSN"))

@app.route('/')
def index():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM TB_HEROIS ORDER BY id_heroi")
            return render_template_string(HTML_TEMPLATE, herois=cur.fetchall())

@app.route('/turno', methods=['POST'])
def turno():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE TB_HEROIS SET hp_atual = GREATEST(0, hp_atual-20), status = CASE WHEN hp_atual-20 <= 0 THEN 'CAÍDO' ELSE status END WHERE status='ATIVO'")
            conn.commit()
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE TB_HEROIS SET hp_atual = hp_max, status = 'ATIVO'")
            conn.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)