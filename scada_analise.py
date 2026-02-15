#------------------------------------------------------------------------------------------------------------
# ANALISE DE DADOS SCADA CAFÉ:
#------------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------------
# CALCULAR QTD DE DIAS PARA O FIM DO MÊS:
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

import datetime

hoje = datetime.date.today()
ano = hoje.year
mes = hoje.month
#mes_nome = hoje.strftime("%B")
# Calcular último dia do mês corrente:
if mes == 12:
    ultimo_dia = datetime.date(ano + 1, 1, 1) - datetime.timedelta(days=1)
else:
    ultimo_dia = datetime.date(ano, mes + 1, 1) - datetime.timedelta(days=1)
# Calcular dias restantes:
dias_restantes = (ultimo_dia - hoje).days

print(f"Faltam {dias_restantes} dias para terminar o mês.")


#------------------------------------------------------------------------------------------------------------
# CONEXÃO COM O BANCO DE DADOS E CRIAÇÃO DO DATAFRAMEç
# Importando a base de dados do SQL através do PANDAS:
import pandas as pd
import sqlite3

conexao = sqlite3.connect("faturamento_scada.db")
base_fat_df = pd.read_sql("SELECT * FROM base_fat", conexao)
conexao.close()
#print(base_fat_df.head())


#------------------------------------------------------------------------------------------------------------
# TRATAMENTO DE DADOS:
# Alterar formato de colunas:
base_fat_df["meta"] = pd.to_numeric(base_fat_df["meta"], errors="coerce")
base_fat_df["faturamento"] = pd.to_numeric(base_fat_df["faturamento"], errors="coerce")
base_fat_df['data'] = pd.to_datetime(base_fat_df['data'])

# Criação de colunas auxiliares:
base_fat_df["ano"] = base_fat_df["data"].dt.year
base_fat_df["mes"] = base_fat_df["data"].dt.month
base_fat_df["mes_nome"] = base_fat_df["data"].dt.strftime("%B")

# Exibir nome dos meses na coluna 'mes' em português:
import locale
locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
base_fat_df["mes_nome"] = base_fat_df["data"].dt.strftime("%B")
base_fat_df["mes_nome"] = base_fat_df["data"].dt.strftime("%B").str.capitalize()


#------------------------------------------------------------------------------------------------------------
# FILTRAR DADOS E CRIAÇÃO DE VARIÁVEIS:
# Input para ANO e MES desejado para analises:
ANO_EXIBICAO = int(input('Digite o Ano: '))
MES_EXIBICAO = int(input('Digite o Mês: '))

# Ordenar dias da semana:
ordem_dias_semana = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo"
]

base_filtro_ano = base_fat_df[base_fat_df["data"].dt.year == ANO_EXIBICAO]
base_filtro_mes = base_filtro_ano[base_filtro_ano['data'].dt.month == MES_EXIBICAO]

# Soma total do faturamento do mes corrente:
total_fat_mes_corrente = base_filtro_ano['faturamento'].sum()

# Exibe a o total de faturamento de todos os meses do ano ordenados:
fat_por_mes = (
    base_filtro_ano
    .groupby(["ano", "mes", "mes_nome"])["faturamento"]
    .sum()
    .reset_index()
    .sort_values(["ano", "mes"])
)

# Exibe o faturamento do mes corrente dia a dia:
fat_por_dia = base_filtro_mes[['data', 'faturamento']]

fat_por_dia = ( 
fat_por_dia
    .dropna(subset=["faturamento"]) # Exclui as linhas com faturamento zerados
)

# Média de faturamento por dia da semana (ano corrente):
media_dia_semana = (
    base_filtro_ano
    .groupby(['dia_semana'])['faturamento']
    .mean()
    .reindex(ordem_dias_semana)
)




#------------------------------------------------------------------------------------------------------------


print(media_dia_semana)
