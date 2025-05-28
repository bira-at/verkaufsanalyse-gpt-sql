import streamlit as st
import sqlite3
import pandas as pd
#import openai
import plotly.express as px

# OpenAI API-Key aus Secrets laden
#openai.api_key = st.secrets["openai"]["api_key"]

# new
from openai import OpenAI

client = OpenAI(
  api_key=st.secrets["openai"]["api_key"],  # this is also the default, it can be omitted
)

st.title("Verkaufsanalyse per Spracheingabe")

# Verbindung zur SQLite DB
conn = sqlite3.connect("sales_data.db")

def query_gpt_to_sql(question):
    system_prompt = """
    Du bist ein hilfreicher Assistent, der natürliche Sprache in SQL-Abfragen übersetzt.
    Die Datenbank hat diese Tabellen:

    customers(customer_id, name, region)
    products(product_id, name, category, price)
    sales(sale_id, product_id, customer_id, quantity, sale_date)

    Schreibe eine passende SQL-Abfrage, die die Frage beantwortet. Nutze nur die angegebenen Tabellen.
    """

    prompt = system_prompt + f"\n\nFrage: {question}\nSQL:"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=150,
        stop=["#",";"]
    )
    sql_query = response.choices[0].text.strip()
    return sql_query

with st.form("query_form"):
    question = st.text_input("Stellen Sie Ihre Frage zur Verkaufsanalyse:")
    submit = st.form_submit_button("Abfrage starten")

if submit and question:
    try:
        sql_query = query_gpt_to_sql(question)
        st.markdown(f"**Generierte SQL-Abfrage:**\n```sql\n{sql_query}\n```")

        df = pd.read_sql_query(sql_query, conn)
        st.dataframe(df)

        # Wenn Tabelle Spalten 'quantity' und 'price' enthält, zeige Umsatz an
        if "quantity" in df.columns and "price" in df.columns:
            df["umsatz"] = df["quantity"] * df["price"]
            fig = px.bar(df, x=df.columns[0], y="umsatz", title="Umsatz nach Kategorie")
            st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Fehler bei der Abfrage: {e}")
