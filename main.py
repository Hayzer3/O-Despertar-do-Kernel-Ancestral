import streamlit as st
import oracledb
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components


load_dotenv()

st.set_page_config(page_title="SQLgard - RPG Engine", layout="centered")

def get_db_connection():
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN")
    )


def processar_turno():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
   
                plsql = """
                DECLARE
                    v_dano_nevoa NUMBER := 20;
                BEGIN
                    FOR heroi IN (SELECT id_heroi, hp_atual FROM TB_HEROIS WHERE status = 'ATIVO') LOOP
                        IF (heroi.hp_atual - v_dano_nevoa) <= 0 THEN
                            UPDATE TB_HEROIS 
                            SET hp_atual = 0, status = 'CAÍDO' 
                            WHERE id_heroi = heroi.id_heroi;
                        ELSE
                            UPDATE TB_HEROIS 
                            SET hp_atual = hp_atual - v_dano_nevoa 
                            WHERE id_heroi = heroi.id_heroi;
                        END IF;
                    END LOOP;
                    COMMIT;
                END;
                """
                cur.execute(plsql)
                st.toast("A névoa venenosa drenou a vida dos heróis!", icon="🌫️")
    except Exception as e:
        st.error(f"Erro ao processar turno no banco: {e}")


st.title("SQLgard - RPG Engine")
st.subheader("O Despertar do Kernel Ancestral")
st.markdown("*Uma nevoa venenosa drena a vida de todos os herois...*")

if st.button("Proximo Turno", type="primary"):
    processar_turno()


try:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi")
            herois = cur.fetchall()

            html_tabela = """
            <style>
                table { width: 100%; border-collapse: collapse; font-family: sans-serif; color: white; }
                th { text-align: left; border-bottom: 2px solid #555; padding: 10px; color: #ccc; }
                td { padding: 12px; border-bottom: 1px solid #333; }
                .hp-bg { background: #444; width: 100px; height: 10px; border-radius: 5px; }
                .hp-fill { height: 100%; border-radius: 5px; transition: width 0.4s ease; }
                .status-caido { background-color: rgba(217, 67, 78, 0.15); color: #ff4b4b; font-weight: bold; }
            </style>
            <table>
                <tr>
                    <th>ID</th><th>Nome</th><th>Classe</th><th>HP</th><th>Barra HP</th><th>Status</th>
                </tr>
            """

            for h in herois:
                pct = (h[3]/h[4]) * 100
                cor_barra = "#4caf50" if pct > 50 else "#ffeb3b" if pct > 20 else "#f44336"

                estilo_linha = "class='status-caido'" if h[5] == 'CAÍDO' else ""

                html_tabela += f"""
                <tr {estilo_linha}>
                    <td>{h[0]}</td>
                    <td>{h[1]}</td>
                    <td>{h[2]}</td>
                    <td>{h[3]}/{h[4]}</td>
                    <td>
                        <div class="hp-bg">
                            <div class="hp-fill" style="width: {pct}%; background: {cor_barra};"></div>
                        </div>
                    </td>
                    <td>{h[5]}</td>
                </tr>
                """
            
            html_tabela += "</table>"
            
            # Renderiza o HTML final
            components.html(html_tabela, height=400)

except Exception as e:
    st.info("Aguardando conexão ou inicialização do banco de dados...")