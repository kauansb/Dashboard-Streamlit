# ===================== Imports =====================
import streamlit as st
import pandas as pd
import plotly.express as px

# ===================== Configuração da Página =====================
# Configuração inicial da página
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

# Tenta mostrar logo na sidebar (arquivo `logo.png` na pasta do projeto)
try:
    st.sidebar.image("logo.png", width='stretch')
except Exception:
    pass

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
    fig_cidade = px.bar(
        df_filtrado.groupby("Cidade")[['Total']].sum().reset_index().sort_values("Total", ascending=False),
        x="Cidade",
        y="Total",
        labels={"Total": "Faturamento (R$)", "Cidade": "Filial"},
        color="Total",
        color_continuous_scale="Blues",
    )
    fig_cidade.update_layout(template="plotly_white", yaxis_tickprefix="R$ ", margin=dict(t=40, b=20))
    st.plotly_chart(fig_cidade, width='stretch')

with col_right:
    st.subheader("Faturamento por Forma de Pagamento")
    fig_pagamento = px.pie(
        df_filtrado.groupby("Forma de pagamento")[['Total']].sum().reset_index(),
        values="Total",
        names="Forma de pagamento",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_pagamento.update_traces(textinfo="percent+label")
    fig_pagamento.update_layout(template="plotly_white", margin=dict(t=40, b=20))
    st.plotly_chart(fig_pagamento, width='stretch')

# ===================== Dados e Download =====================
# Tabela de dados filtrados e botão para download
st.markdown("### Dados (filtrados)")
st.dataframe(df_filtrado.reset_index(drop=True))
csv = df_filtrado.to_csv(index=False, sep=";", decimal=",")
