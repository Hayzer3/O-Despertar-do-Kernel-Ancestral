from flask import Flask, render_template_string, request, redirect, url_for
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SQLgard - RPG Engine</title>
    <style>
        body { background: #0e1117; color: #c9d1d9; font-family: sans-serif; text-align: center; padding-top: 40px; }
        h1 { color: white; text-transform: uppercase; }
        .btn-container { margin-bottom: 20px; }
        button { padding: 10px 20px; font-weight: bold; border-radius: 5px; border: none; cursor: pointer; margin: 5px; }
        .btn-turno { background: white; color: black; }
        .btn-reset { background: #4caf50; color: white; }
        table { width: 85%; max-width: 900px; margin: 0 auto; border-collapse: collapse; background: #161b22; }
        th { background: #21262d; padding: 12px; color: #8b949e; }
        td { padding: 12px; border-bottom: 1px solid #30363d; }
        .status-caido { color: #ff4b4b; background: rgba(255,0,0,0.05); }
    </style>
</head>
<body>
    <h1>⚔️ SQLgard - RPG Engine</h1>
    <div class="btn-container">
        <form action="/turno" method="post" style="display:inline;">
            <button type="submit" class="btn-turno">PRÓXIMO TURNO</button>
        </form>
        <form action="/reset" method="post" style="display:inline;">
            <button type="submit" class="btn-reset">RESETAR</button>
        </form>
    </div>

    <table>
        <thead>
            <tr><th>Nome</th><th>Classe</th><th>HP</th><th>Barra</th><th>Status</th></tr>
        </thead>
        <tbody>
            {% for h in herois %}
                {% set pct = (h[3] / h[4] * 100) | int if h[4] > 0 else 0 %}
                {% set cor = '#4caf50' if pct > 50 else ('#f1c40f' if pct > 20 else '#ff4b4b') %}
            <tr class="{{ 'status-caido' if h[5] == 'CAÍDO' }}">
                <td style="font-weight: bold;">{{ h[1] }}</td>
                <td>{{ h[2] }}</td>
                <td>{{ h[3] }}/{{ h[4] }}</td>
                <td>
                    <div style="background: #333; width: 100px; height: 10px; border-radius: 5px; margin: 0 auto; overflow: hidden;">
                        <div style="width: {{ pct }}%; height: 100%; background-color: {{ cor }}; transition: width 0.5s;"></div>
                    </div>
                </td>
                <td style="font-weight: bold;">{{ h[5] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def get_db_connection():
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN")
    )

@app.route('/')
def index():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi")
                herois = cur.fetchall()
        # usamos render_template_string para ler a variável ali de cima
        return render_template_string(HTML_TEMPLATE, herois=herois)
    except Exception as e:
        return f"Erro ao conectar ao banco: {e}"

@app.route('/turno', methods=['POST'])
def turno():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                plsql = """
                BEGIN
                    FOR r IN (SELECT id_heroi, hp_atual FROM TB_HEROIS WHERE status = 'ATIVO') LOOP
                        IF (r.hp_atual - 20) <= 0 THEN
                            UPDATE TB_HEROIS SET hp_atual = 0, status = 'CAÍDO' WHERE id_heroi = r.id_heroi;
                        ELSE
                            UPDATE TB_HEROIS SET hp_atual = hp_atual - 20 WHERE id_heroi = r.id_heroi;
                        END IF;
                    END LOOP;
                    COMMIT;
                END;
                """
                cur.execute(plsql)
        return redirect(url_for('index'))
    except Exception as e:
        return f"Erro no Turno: {e}"

@app.route('/reset', methods=['POST'])
def reset():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE TB_HEROIS SET hp_atual = hp_max, status = 'ATIVO'")
                conn.commit()
        return redirect(url_for('index'))
    except Exception as e:
        return f"Erro ao resetar: {e}"

if __name__ == "__main__":
    app.run(debug=True)