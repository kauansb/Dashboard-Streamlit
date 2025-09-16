# ===================== Imports =====================
import streamlit as st
import pandas as pd
import numpy as np

# ===================== Configuração da Página =====================
# Configuração inicial da página

# Tenta mostrar logo na sidebar (arquivo `logo.png` na pasta do projeto)
try:
    st.image("logo.png", width=250)
except Exception:
    pass

st.set_page_config(layout="wide", page_title="Dashboard")

# ===================== Funções =====================
# Função para carregar dados
@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath, sep=";", decimal=",")
    df["Data"] = pd.to_datetime(df["Data"])
    df["Mes"] = df["Data"].apply(lambda x: f"{x.month}/{x.year}")
    return df

# ===================== Carregamento de Dados =====================
# Carregar os dados
df = load_data("vendas.csv")

# ===================== Cabeçalho =====================
# Título do Dashboard
st.title(":bar_chart: Dashboard - Vendas")

# ===================== Sidebar / Filtros =====================
# Sidebar - Filtros
st.sidebar.header("Filtros")
mes_selecionado = st.sidebar.selectbox("Selecione o mês", df["Mes"].unique())
ramo_selecionado = st.sidebar.multiselect(
    "Selecione os canais de venda", df["Ramo"].unique(), default=df["Ramo"].unique()
    )

# Filtrar os dados
df_filtrado = df[(df["Mes"] == mes_selecionado) & (df["Ramo"].isin(ramo_selecionado))]

# ===================== Visual e KPIs =====================
# KPIs
total_faturamento = df_filtrado["Total"].sum()
num_vendas = len(df_filtrado)
ticket_medio = total_faturamento / num_vendas if num_vendas else 0

def format_currency(v):
    s = f"{v:,.2f}"
    # converte 1,234.56 -> 1.234,56 para formato BR
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

k1, k2, k3 = st.columns(3)
k1.metric("Faturamento", format_currency(total_faturamento))
k2.metric("Número de Vendas", f"{num_vendas}")
k3.metric("Ticket Médio", format_currency(ticket_medio))

# ===================== Visualizações (Gráficos) =====================
# Layout com duas colunas para gráficos (mais espaço para o gráfico de barras)
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(f"Faturamento por Cidade — {mes_selecionado}")
    # Agrupa por cidade e plota com st.bar_chart (Streamlit)
    df_cidade = df_filtrado.groupby("Cidade")["Total"].sum().sort_values(ascending=False)
    st.bar_chart(df_cidade, color="#ff4b4b")

with col_right:
    st.subheader("Faturamento por Forma de Pagamento")
    # Agrupa por forma de pagamento e plota um gráfico (garantindo dados finitos)
    pagamento_df = df_filtrado.groupby("Forma de pagamento")["Total"].sum().reset_index()

    # Sanitiza os valores: converte para numérico, remove infinitos e NaN
    pagamento_df["Total"] = pd.to_numeric(pagamento_df["Total"], errors="coerce")
    pagamento_df["Total"] = pagamento_df["Total"].replace([np.inf, -np.inf], np.nan).fillna(0)

    total_pag = pagamento_df["Total"].sum()

    if total_pag <= 0:
        st.info("Sem faturamento para as formas de pagamento selecionadas.")
        pagamento_display = pagamento_df.copy()
        pagamento_display["Total"] = pagamento_display["Total"].apply(format_currency)
        pagamento_display["Percent"] = "0%"
        st.table(pagamento_display.sort_values("Total", ascending=False).reset_index(drop=True))
    else:
        # calcula percentuais e ordena
        pagamento_df["Percent"] = (pagamento_df["Total"] / total_pag * 100).round(1)
        pagamento_df = pagamento_df.sort_values("Total", ascending=False).reset_index(drop=True)

        # Exibe top-3 formas como KPIs para facilitar leitura
        top_n = min(3, len(pagamento_df))
        cols = st.columns(top_n)
        for i in range(top_n):
            nome = pagamento_df.loc[i, "Forma de pagamento"]
            valor = pagamento_df.loc[i, "Total"]
            perc = pagamento_df.loc[i, "Percent"]
            cols[i].metric(label=nome, value=format_currency(valor), delta=f"{perc}%")

        # Tabela resumida para formas de pagamento
        pagamento_display = pagamento_df.copy()
        pagamento_display["Total"] = pagamento_display["Total"].apply(format_currency)
        pagamento_display["Percent"] = pagamento_display["Percent"].astype(str) + "%"
        st.table(pagamento_display.reset_index(drop=True))

# ===================== Dados e Download =====================
# Tabela de dados filtrados e botão para download
st.markdown("### Dados (filtrados)")
st.dataframe(df_filtrado.reset_index(drop=True))
csv = df_filtrado.to_csv(index=False, sep=";", decimal=",")
