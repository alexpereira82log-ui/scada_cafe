#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Calcular fim do mês:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
import datetime

hoje = datetime.date.today()
ano = hoje.year
mes = hoje.month
# Calcular último dia do mês corrente:
if mes == 12:
    ultimo_dia = datetime.date(ano + 1, 1, 1) - datetime.timedelta(days=1)
else:
    ultimo_dia = datetime.date(ano, mes + 1, 1) - datetime.timedelta(days=1)
# Calcular dias restantes:
dias_restantes = (ultimo_dia - hoje).days

print(f"Faltam {dias_restantes} dias para terminar o mês.")


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
ANO_EXIBICAO = 2025
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#Importação de bases e criação de DataFrames:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
import pandas as pd

faturamento_df = pd.read_excel("base_cinema.xlsx")
produtos_df = pd.read_excel('base_cinema_produtos.xlsx')
perdas_df = pd.read_excel('base_cinema_perdas.xlsx')
comissao_df = pd.read_excel('base_cinema_comissao.xlsx')

# Converter colunas para formato Datetime:
#faturamento_df["Dia"] = pd.to_datetime(faturamento_df["Dia"], errors="coerce")
produtos_df["Dia"] = pd.to_datetime(produtos_df["Mês"], errors="coerce")
perdas_df["Data"] = pd.to_datetime(perdas_df["Data"], errors="coerce")

# Filtrar dados do ano de exibição:
faturamento_df = faturamento_df[faturamento_df["Dia"].dt.year == ANO_EXIBICAO]
produtos_df = produtos_df[produtos_df["Mês"].dt.year == ANO_EXIBICAO]
perdas_df = perdas_df[perdas_df["Data"].dt.year == ANO_EXIBICAO]


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Tratamento de dados:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
import locale
#locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Renomear uma coluna:
faturamento_df = faturamento_df.rename(columns={'Cupom Total': 'Cupons por Dia'})
# Acrescentando uma coluna com percentual da meta:
faturamento_df["% Meta"] = faturamento_df["Faturamento"] / faturamento_df["Meta"] * 100
# Substituir formato da coluna Mês atual por descrição do mês:
#faturamento_df["Mês"] = faturamento_df["Mês"].dt.month_name(locale="pt_BR.utf8")
faturamento_df["Mês"] = faturamento_df["Mês"].dt.month_name(locale="pt_BR.UTF-8")

# Substituir formato da coluna Mês atual por descrição do mês:
#produtos_df["Mês"] = produtos_df["Mês"].dt.month_name(locale="pt_BR.utf8") 
produtos_df["Mês"] = produtos_df["Mês"].dt.month_name(locale="pt_BR.UTF-8")

#Renomear colunas:
perdas_df = perdas_df.rename(columns={'MÊS/ANO': 'Mês'})
perdas_df = perdas_df.rename(columns={'Data': 'Data da perda'})
perdas_df = perdas_df.rename(columns={'Responsavel': 'Responsável'})
# Converter coluna para formato Datetime:
perdas_df["Mês"] = pd.to_datetime(perdas_df["Data da perda"],format="%Y-%m-%d" ,errors="coerce")
# Alterar exibição para apenas o nome do mês:
#perdas_df["Mês"] = perdas_df["Mês"].dt.month_name(locale="pt_BR.utf8")
perdas_df["Mês"] = perdas_df["Mês"].dt.month_name(locale="pt_BR.UTF-8")


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Análise de Dados Por Mês
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# Gerar o somatório de faturamento por mês:
faturamento_por_mes = faturamento_df.groupby("Mês")[["Faturamento", "Meta"]].sum().reset_index()

# Ordenar os meses de forma correta (crescente):
faturamento_por_mes["Mês"] = pd.Categorical(
    faturamento_por_mes["Mês"],
    categories=ordem_meses,
    ordered=True
)
faturamento_por_mes = faturamento_por_mes.sort_values("Mês")

print("\n" + "-" * 50)
print("FATURAMENTO POR MÊS:")
print(faturamento_por_mes)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Análise de Dados Por Dia
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Gerar o somatório de faturamento por mês
faturamento_por_dia = faturamento_df.groupby("Dia")["Faturamento"].sum().reset_index()

# Ordenar os dias de forma correta (crescente):
faturamento_por_dia["Dia"] = pd.Categorical(
    faturamento_por_dia["Dia"],
    ordered=True
)
faturamento_por_dia = faturamento_por_dia.sort_values("Dia")

#print("-" * 50)
#print("FATURAMENTO POR DIA:")
#print(faturamento_por_dia)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Análise de Dados Por DiaDia da Semana
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
faturamento_dia_semana = faturamento_df.groupby("Dia semana")[["Faturamento", "Ticket Médio", "Cupons por Dia"]].mean().round(2).reset_index()
ordem_dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

# Ordenar os dias da semana de forma correta (crescente):
faturamento_dia_semana["Dia semana"] = pd.Categorical(
    faturamento_dia_semana["Dia semana"],
    categories=ordem_dias_semana,
    ordered=True
)
faturamento_dia_semana = faturamento_dia_semana.sort_values("Dia semana")

print("\n" + "-" * 50)
print("MÉDIAS POR DIA DA SEMANA:")
print(faturamento_dia_semana)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Produtos mais vendidos no Ano e no Mês
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Filtrar os dados do mês desejado:
produtos_por_mes = produtos_df.loc[produtos_df['Mês'] == "Dezembro", :]
produtos_por_mes = produtos_por_mes.sort_values("Valor Total", ascending=False)

total_fat_ano = faturamento_df["Faturamento"].sum()

# Somar o valor total por produto no ano:
produtos_ano = produtos_df.groupby("Produto")["Valor Total"].sum().reset_index()
produtos_ano = produtos_ano.sort_values("Valor Total", ascending=False)
#inserir coluna com percentual:
produtos_ano["% do Fat Total"] = produtos_ano["Valor Total"] / total_fat_ano
#inserir coluna com média mensal:
produtos_ano["Média Fat Mensal"] = produtos_ano["Valor Total"] / mes

# Função para formatar valores em reais (R$):
def formatar(valor):
    valor_formatado = f"R$ {valor:,.2f}"
    return valor_formatado

# Função para formatar valores percentuais
def formatar_perc(percentual):
    percentual_formatado = f"{percentual:.2%}"
    return percentual_formatado

produtos_ano["Valor Total"] = produtos_ano["Valor Total"].apply(formatar)
produtos_ano["Média Fat Mensal"] = produtos_ano["Média Fat Mensal"].apply(formatar)
produtos_ano["% do Fat Total"] = produtos_ano["% do Fat Total"].apply(formatar_perc)

print("\n" + "-" * 50)
print(f"Faturamento Total Ano: R$ {total_fat_ano:,.2f}")
print("Produtos mais vendidos do Ano:")
print(produtos_ano.head(10)) # Exibir os 10 produtos mais vendidos do Ano
print("Produtos mais vendidos do Mês:")
print(produtos_por_mes.head(10))

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Criação de variáveis e funções
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# FILTRAR MES CORRENTE em:
df_mes_corrente = faturamento_df[
    (faturamento_df['Dia'].dt.year == 2025) &
    (faturamento_df['Dia'].dt.month == 12)
]

import calendar
import locale
# Configura o locale para Português do Brasil (Pode ser necessário dependendo do ambiente):
#locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
# Se a linha acima falhar, tente: locale.setlocale(locale.LC_TIME, 'portuguese')

# Método 2: Usando a biblioteca 'calendar' para ter controle do idioma
mes_numero = df_mes_corrente['Dia'].dt.month.iloc[0]
nome_do_mes_pt_br = calendar.month_name[mes_numero]
# Apenas para garantir que caso comece com letra maiúscula (o calendar.month_name retorna 'outubro')
nome_do_mes_corrente = nome_do_mes_pt_br.capitalize()

# VARIÁVEIS DE APOIO:
meta_mes_corrente = df_mes_corrente["Meta"].sum()
soma_faturamento = df_mes_corrente['Faturamento'].sum()
faturamento_medio_dia = df_mes_corrente['Faturamento'].mean()
total_cupons_mes = df_mes_corrente['Cupons por Dia'].sum()
ticket_medio_dia = soma_faturamento / total_cupons_mes
media_cupons_dia = df_mes_corrente['Cupons por Dia'].mean()
projecao_faturamento = soma_faturamento + (faturamento_medio_dia * (dias_restantes))
ticket_meta_dia = (meta_mes_corrente - soma_faturamento) / total_cupons_mes * media_cupons_dia / dias_restantes
fat_meta_dia = (meta_mes_corrente - soma_faturamento) / dias_restantes
ticket_meta_dia = (meta_mes_corrente - soma_faturamento) / media_cupons_dia / dias_restantes
fat_total_eq_1 = df_mes_corrente[df_mes_corrente['Equipe'] == 1]['Faturamento'].sum()
fat_total_eq_2 = df_mes_corrente[df_mes_corrente['Equipe'] == 2]['Faturamento'].sum()
ticket_eq_1 = df_mes_corrente[df_mes_corrente['Equipe'] == 1]['Ticket Médio'].mean()
ticket_eq_2 = df_mes_corrente[df_mes_corrente['Equipe'] == 2]['Ticket Médio'].mean()
total_dias_eq_1 = df_mes_corrente[df_mes_corrente['Equipe'] == 1]['Dia'].nunique()
total_dias_eq_2 = df_mes_corrente[df_mes_corrente['Equipe'] == 2]['Dia'].nunique()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Resumo de Resultados:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# EXIBIÇÕES:
print("\n" + "-" * 50)
print(f'- DADOS FATURAMENTO - {nome_do_mes_corrente}:')
print(f'Meta Mês: R$ {meta_mes_corrente:,.2f}')
print(f'Faturamento: R$ {soma_faturamento:,.2f}')
print(f'% Meta: {soma_faturamento / meta_mes_corrente:.0%}')
print(f'Faturamento Médio Dia: R$ {faturamento_medio_dia:,.2f}')
print(f'Ticket Médio Dia: R$ {ticket_medio_dia:,.2f}')
print(f'Média Cupons Dia: {media_cupons_dia:.0f}')
print("\n" + "-" * 50)
print('- PROJEÇÕES E RECUPERAÇÃO META:')
print(f'Ainda faltam R$ {meta_mes_corrente - soma_faturamento:,.2f} para atingirmos a  meta do mês.')
print(f'Estamos projetando R$ {projecao_faturamento:,.2f} de faturamento no mês.')
print(f'Precisamos de R$ {ticket_meta_dia:,.0f} por mesa ou R$ {fat_meta_dia:,.0f} por dia para alcançarmos a meta do mês.')
print(f'Isso representa R$ {ticket_meta_dia - ticket_medio_dia:,.0f} a mais por mesa mediante aos R$ {ticket_medio_dia:,.0f} realizado atualmente.')
print("\n" + "-" * 50)
print('- RESULTADO POR EQUIPE:')
print(f'Faturamento Equipe 01: R$ {fat_total_eq_1:,.0f}')
print(f'Faturamento Equipe 02: R$ {fat_total_eq_2:,.0f}')
print(f'Ticket Médio Equipe 01: R$ {ticket_eq_1:,.0f}')
print(f'Ticket Médio Equipe 02: R$ {ticket_eq_2:,.0f}')
print(f"Dias trabalhados Equipe 1: {total_dias_eq_1}")
print(f"Dias trabalhados Equipe 2: {total_dias_eq_2}")

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Projeção Comissão:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# arredondar coluna rateio:
comissao_df['Vlr Final'] = comissao_df['Vlr Final'].round(2)
# Excluir linhas com valor zero na coluna 'Vlr Final':
comissao_df = comissao_df[comissao_df['Vlr Final'] != 0]

total_comissao_atual = comissao_df['Vlr Final'].sum()
media_diaria_comissao = comissao_df['Vlr Final'].mean()
projecao_comissao = (total_comissao_atual + (media_diaria_comissao * dias_restantes))

print("\n" + "-" * 50)
print("PROJEÇÃO COMISSÃO:")
print(f'Comissão atual: R$ {total_comissao_atual:,.2f}')
print(f'Média diária: R$ {media_diaria_comissao:,.2f}')
print(f"Projeção comissão: R$ {projecao_comissao:,.2f}")

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# PERDAS: Por Mês
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Agrupar perdas por mês
perdas_por_mes = perdas_df.groupby("Mês")[["Quantidade"]].count().reset_index()

# Ordenar meses de forma correta (crescente):
perdas_por_mes["Mês"] = pd.Categorical(perdas_por_mes["Mês"], categories=ordem_meses, ordered=True)
perdas_por_mes = perdas_por_mes.sort_values("Mês").reset_index(drop=True)

print("\n" + "-" * 50)
print("PERDAS POR MÊS:")
print(perdas_por_mes)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# PERDAS: Por Motivo
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Filtrar perdas do mês corrente:
perdas_mes_corrente = perdas_df[perdas_df['Mês'] == nome_do_mes_corrente]
# Contagem por Motivo
perdas_motivo = perdas_mes_corrente.groupby("Motivo")[["Item"]].count().reset_index()
# Ordenar por quantidade de perdas:
perdas_motivo = perdas_motivo.sort_values("Item", ascending=False).reset_index(drop=True)
# Somatório total do número de ocorrências de perdas:
total_perdas_mes = perdas_motivo["Item"].sum()

print("\n" + "-" * 50)
print("PERDAS MÊS CORRENTE:")
print(perdas_mes_corrente)

print("PERDAS POR MOTIVO:")
print(perdas_motivo)
print(f"Total: {total_perdas_mes}")

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# DASHBOARD: GRÁFICOS
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

# Definir ciclo de cores personalizado usando a paleta 'tab10'
cores = plt.get_cmap('tab10').colors
ciclo_cores = cycler('color', cores)
plt.rc('axes', prop_cycle=ciclo_cores)

# === Ordem dos meses ===
ordem_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# Ordem meses em inglês:
ordem_meses_ingles = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# DASHBOARD: Mês Corrente:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Criação de Mosaico:
mosaico = "BC;DE" # Definição do mosaico onde serão alocados os gráficos
fig = plt.figure(figsize=(14, 10)) # Criação da figura dos gráficos
espacamento = {'wspace': 0.12, 'hspace': 0.3} # Variável para definição de espaçamentos
axs = fig.subplot_mosaic(mosaico, gridspec_kw=espacamento) # Criação do sistema de eixos


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO B:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# FATURAMENTO POR DIA:
# Agrupar por dia e somar o Faturamento
# Nota: Como já filtramos por mês, o 'Dia' aqui será o dia do mês (1, 2, 3...)
dados_diarios_mes = df_mes_corrente.groupby(df_mes_corrente['Dia'].dt.day)['Faturamento'].sum().reset_index()

# NOVIDADE CRUCIAL: FILTRAR APENAS DIAS COM FATURAMENTO MAIOR QUE ZERO
dados_diarios_mes = dados_diarios_mes[
    dados_diarios_mes['Faturamento'] > 0
].reset_index(drop=True) # O reset_index é opcional, mas boa prática após um filtro


# --- NOVIDADE: 1.4 Calcular a Média ---
media_diaria = dados_diarios_mes['Faturamento'].mean()

# .plot() é o comando para gráficos de linha
axs["B"].plot(
    dados_diarios_mes['Dia'],
    dados_diarios_mes['Faturamento'],
    marker='o',          # Adiciona um marcador para cada dia
    linestyle='-',       # Linha contínua
    linewidth=2,
    label="Faturamento"
)

# --- NOVIDADE: Linha de Média ---
axs["B"].axhline(
    y=media_diaria,
    color='red',
    linestyle='--', # Linha tracejada
    alpha=0.3,
    linewidth=2,
    label=f"Média Diária ({media_diaria:,.0f} R$)" # Adicionar label da média na legenda com o valor formatado
)

# --- NOVIDADE: Valores sobre os Pontos (Rótulos de Dados) ---
for dia, faturamento in zip(dados_diarios_mes['Dia'], dados_diarios_mes['Faturamento']):
    axs["B"].text(
        dia, 
        faturamento + 100,  # Adiciona um pequeno offset (+100) para ficar acima do ponto
        f"{faturamento:,.0f}", # Formata o valor sem casas decimais e com separador de milhar
        ha='center',        # Alinhamento horizontal: centralizado no ponto
        va='bottom',        # Alinhamento vertical: acima do ponto
        fontsize=9,
        alpha=0.7,
        color='dimgrey',
        weight='bold'
    )

# --- 3. Personalização e Visualização ---
axs["B"].set_title(f'Faturamento Diário', fontsize=14, weight='bold')
axs["B"].set_xlabel('Dia do Mês', fontsize=10)
axs["B"].set_ylabel('Faturamento (R$)', fontsize=10)
axs["B"].tick_params(axis="x", rotation=45, labelsize=8)


# Garantir que todos os dias do mês apareçam no eixo X
dias = range(1, len(dados_diarios_mes) + 1)
axs["B"].set_xticks(dias)

axs["B"].legend()
axs["B"].grid(True, linestyle='--', alpha=0.4)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO C:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# RELAÇÃO TICKET MÉDIO X NÚMERO DE CUPONS:
# VARIÁVEIS TICKET: - - - - - - - - - - - - - - - - - - - - - - - - 
ticket_medio_mes_corrente = df_mes_corrente.groupby(df_mes_corrente['Dia'].dt.day)['Ticket Médio'].mean().reset_index()
# Filtrar faturamento maior que '0':
ticket_medio_mes_corrente = ticket_medio_mes_corrente[
    ticket_medio_mes_corrente['Ticket Médio'] > 0
].reset_index(drop=True) # O reset_index é opcional, mas boa prática após um filtro
# Linha de Média
media_ticket_mes_corrente = ticket_medio_mes_corrente['Ticket Médio'].mean()

# VARIÁVEIS CUPONS: - - - - - - - - - - - - - - - - - - - - - - - - 
dados_cupons_mes_corrente = df_mes_corrente.groupby(df_mes_corrente['Dia'].dt.day)['Cupons por Dia'].sum().reset_index()
#dados_cupons_mes_corrente.columns = ['Dia do Mês', 'Cupons por Dia']
# Filtrar cupos maior que '0':
dados_cupons_mes_corrente = dados_cupons_mes_corrente[dados_cupons_mes_corrente['Cupons por Dia'] > 0].reset_index(drop=True)
# O reset_index é opcional, mas boa prática após um filtro
# Calcular a Média de Cupons
media_cupons_mes_corrente = dados_cupons_mes_corrente['Cupons por Dia'].mean()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# CONSTRUÇÃO DO GRÁFICO COM DOIS EIXOS Y:
axs["C"].grid(True, linestyle='--', alpha=0.4)

# Primeiro eixo Y - Ticket Médio:
axs["C"].plot(ticket_medio_mes_corrente['Dia'], ticket_medio_mes_corrente['Ticket Médio'],
         marker='o', linestyle='-', linewidth=2, label='Ticket Médio Diário')
axs["C"].set_ylabel('Ticket Médio (R$)', color='steelblue')
axs["C"].set_xlabel('Dia do Mês', fontsize=10)
axs["C"].tick_params(axis='y', labelcolor="steelblue")
axs["C"].set_title(f'Relação Ticket Médio x Número de Cupons', fontsize=11, weight='bold')

# Linha de Média Ticket Médio:
media_ticket_mes_corrente = ticket_medio_mes_corrente['Ticket Médio'].mean()
axs["C"].axhline(
    y=media_ticket_mes_corrente,
    color='red',
    linestyle='--', # Linha tracejada
    alpha=0.3,
    linewidth=2,
    label=f"Média Ticket Dia ({media_ticket_mes_corrente:,.0f} R$)" # Adicionar label da média na legenda com o valor formatado
)
# Valores sobre os Pontos Ticket Médio (Rótulos de Dados):
for dia, ticket in zip(ticket_medio_mes_corrente['Dia'], ticket_medio_mes_corrente['Ticket Médio']):
    axs["C"].text(
        dia,
        ticket + 0.1,  # Adiciona um pequeno offset (+5) para ficar acima do ponto
        f"{ticket:,.2f}", # Formata o valor sem casas decimais e com separador de milhar
        ha='center',
        va='bottom',
        fontsize=9,
        color='dimgrey',
        weight='bold'
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - -
ax2 = axs["C"].twinx()  # Criar um segundo eixo Y compartilhando o eixo X
# - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Segundo eixo Y - Cupons por Dia:
ax2.plot(dados_cupons_mes_corrente['Dia'], dados_cupons_mes_corrente['Cupons por Dia'],
         marker='s', linestyle='-', color='darkred', linewidth=2, alpha=0.15, label=f'Cupons por Dia ({media_cupons_dia:.0f})')
ax2.set_ylabel('Cupons por Dia', color='darkred')
ax2.tick_params(axis='y', labelcolor='darkred')

#Ajuste de grid do gráfico de linhas para Cupons - AX2:
#ax2.grid(axis='y', linestyle='--', alpha=0.4)
ax2.grid(False)

# Garantir que todos os dias do mês apareçam no eixo X
dias = range(1, len(dados_diarios_mes) + 1)
axs["C"].set_xticks(dias)
axs["C"].set_xticklabels(dados_cupons_mes_corrente["Dia"], rotation=45, fontsize=8)

# Adicionar legendas ancorando a posição fixa (x, y) / bbox_transform para posicionar em relação a área do gráfico
#axs["C"].legend(bbox_to_anchor=(0.65, 1), bbox_transform=axs["C"].transAxes)
axs["C"].legend(bbox_transform=ax2.transAxes)
ax2.legend()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO D:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PERDAS POR MÊS:
perdas_mes = axs["D"].bar(perdas_por_mes['Mês'], perdas_por_mes['Quantidade'], color='red', alpha=0.3, label='Perdas')
media_perdas_mes = perdas_por_mes['Quantidade'].mean()

# --- NOVIDADE: Linha de Média ---
axs["D"].axhline(
    y=media_perdas_mes,
    #color='salmon',
    linestyle='--', # Linha tracejada
    alpha=0.5,
    linewidth=2,
    label=f"Média Mês ({media_perdas_mes:,.0f})" # Adicionar label da média na legenda com o valor formatado
)

# === Personalização ===
axs["D"].set_title('Perdas Por Mês', fontsize=14, weight='bold')
#axs["D"].set_xlabel("Mês")
axs["D"].set_ylabel("Quantidade")
axs["D"].tick_params(axis="x", rotation=45, labelsize=8)
axs["D"].grid(False)
axs["D"].grid(axis="y", linestyle="--", alpha=0.4)
axs["D"].legend()

# === Valores sobre as barras ===
axs["D"].bar_label(
    perdas_mes, # Variável que recebeu a instrução do gráfico
    label=perdas_por_mes["Quantidade"], # Informação a ser exibida em cima de cada barra
    padding=3, # Posição do texto em relação à barra
    fontsize=9, # Tamanho da fonte
    fontweight='bold', # Fonte em negrito
    color="dimgrey" # Cor do texto
    )

# Muda a cor da barra para valores abaixo da média:
for i, barra in enumerate(perdas_mes):
    if perdas_por_mes["Quantidade"].iloc[i] < media_perdas_mes:
        barra.set_color('green')

# Destacar área no gráfico (exemplo: período de redução de perdas)
#plt.axvspan(4.5, 9.5, color='lightgreen', alpha=0.3) 
#plt.text(5.5, 70, 'Período de Redução de Perdas', fontsize=10, color='darkgreen')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO E:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PERDAS POR MOTIVO:
perdas_cat = axs["E"].pie(
    perdas_motivo['Item'],
    labels=perdas_motivo['Motivo'],
    autopct='%1.1f%%',
    startangle=140,
    textprops={'fontsize': 10, 'weight': 'bold', 'color': 'black'}
)

# === Personalização ===
axs["E"].set_title(f'Perdas por Categoria', fontsize=14, weight='bold')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # AJUSTES FIGURA:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
fig.suptitle(f"Dashboard Scada Café - Loja Cinema - {nome_do_mes_corrente} 2025", fontsize=16, fontweight='bold', color='darkgrey')

# Gerar arquivo .PNG do gráfico:
plt.savefig("dashboard_Mes_Corrente.png", dpi=300, bbox_inches="tight")

plt.show()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# DASHBOARD: Mês a Mês:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Criação de Mosaico:
mosaico_mes = "AA;BC" # Definição do mosaico onde serão alocados os gráficos
fig = plt.figure(figsize=(14, 10)) # Criação da figura dos gráficos
espacamento = {'wspace': 0.15, 'hspace': 0.3} # Variável para definição de espaçamentos
axs = fig.subplot_mosaic(mosaico_mes, gridspec_kw=espacamento) # Criação do sistema de eixos

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO A:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# FATURAMENTO X META MENSAL:
faturamento_por_mes = faturamento_df.groupby("Mês")[["Faturamento", "Meta"]].sum().reset_index()

media_faturamento_mes = faturamento_por_mes.loc[
    faturamento_por_mes["Mês"] != nome_do_mes_corrente, "Faturamento" # .loc[condição, coluna] → exclui esse mês.
].mean() # .mean() → calcula a média somente dos meses restantes.

# === Ordenar meses ===
faturamento_por_mes["Mês"] = pd.Categorical(faturamento_por_mes["Mês"],
                                     categories=ordem_meses,
                                     ordered=True)
faturamento_por_mes = faturamento_por_mes.sort_values("Mês")

# === Criar o gráfico de barras ===
barras_meta = axs["A"].bar(
    faturamento_por_mes["Mês"],
    faturamento_por_mes["Meta"],
    label="Meta",
    color="darkorange",
    alpha=0.4
)

barras_faturamento = axs["A"].bar(
    faturamento_por_mes["Mês"],
    faturamento_por_mes["Faturamento"],
    label="Faturamento",
    color="steelblue"
)

# Definir rótulos das colunas Meta e Faturamento
axs["A"].bar_label(barras_meta, fmt="{:,.0f}", padding=3, fontsize=8)
axs["A"].bar_label(barras_faturamento, fmt="{:,.0f}", padding=3, fontsize=8, fontweight='bold')

# === Linha média ===
axs["A"].axhline(y=media_faturamento_mes, color="darkred", linestyle="--", alpha=0.3, linewidth=2,
            label=f"Média ({media_faturamento_mes:,.0f})")

# === Personalização ===
axs["A"].set_title("Faturamento x Meta Mensal", fontsize=14, weight='bold')
#ax.set_xlabel("Mês")
axs["A"].set_ylabel("Valores (R$)")
axs["A"].tick_params(axis="x", rotation=45, labelsize=8)
axs["A"].legend(loc="lower left")
axs["A"].grid(False)
axs["A"].grid(axis="y", linestyle="--", alpha=0.6)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO B:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# MÉDIA FATURAMENTO DIA (MÊS):
faturamento_por_dia = faturamento_df.groupby(faturamento_df['Dia'].dt.month)['Faturamento'].mean().reset_index().round(1)
faturamento_por_dia = faturamento_por_dia.rename(columns={'Dia': 'Mês'}) # Renomear coluna

# .plot() é o comando para gráficos de linha
axs["B"].plot(
    faturamento_por_dia['Mês'],
    faturamento_por_dia['Faturamento'],
    marker='o',          # Adiciona um marcador para cada dia
    linestyle='-',       # Linha contínua
    linewidth=2,
    label="Fat Médio Dia"
)

# --- NOVIDADE: Valores sobre os Pontos (Rótulos de Dados) ---
for dia, faturamento in zip(faturamento_por_dia['Mês'], faturamento_por_dia['Faturamento']):
    axs["B"].text(
        dia, 
        faturamento + 15,  # Adiciona um pequeno offset (+100) para ficar acima do ponto
        f"{faturamento:,.0f}", # Formata o valor sem casas decimais e com separador de milhar
        ha='center',        # Alinhamento horizontal: centralizado no ponto
        va='bottom',        # Alinhamento vertical: acima do ponto
        fontsize=9,
        alpha=0.7,
        color='dimgrey',
        weight='bold'
    )

# --- 3. Personalização e Visualização ---
axs["B"].set_title('Faturamento Médio - 2025', fontsize=14, weight='bold')
axs["B"].set_xlabel('Meses', fontsize=10)
axs["B"].set_ylabel('Média Faturamento (R$)', fontsize=10)

# Garantir que todos os meses apareçam no eixo X:
dias = range(1, len(faturamento_por_dia) + 1)
axs["B"].set_xticks(dias)

#axs["B"].legend()
axs["B"].grid(False)
axs["B"].grid(True, linestyle='--', alpha=0.4)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO C:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# RELAÇÃO TICKET MÉDIO X NÚMERO DE CUPONS:
# VARIÁVEIS TICKET: - - - - - - - - - - - - - - - - - - - - - - - - 
ticket_medio_mes = faturamento_df.groupby(faturamento_df['Dia'].dt.month)['Ticket Médio'].mean().reset_index()
# Filtrar faturamento maior que '0':
ticket_medio_mes = ticket_medio_mes[
    ticket_medio_mes['Ticket Médio'] > 0
].reset_index(drop=True) # O reset_index é opcional, mas boa prática após um filtro

# VARIÁVEIS CUPONS: - - - - - - - - - - - - - - - - - - - - - - - - 
dados_cupons_mes = faturamento_df.groupby(faturamento_df['Dia'].dt.month)['Cupons por Dia'].mean().reset_index()
# Filtrar cupos maior que '0':
dados_cupons_mes = dados_cupons_mes[dados_cupons_mes['Cupons por Dia'] > 0].reset_index(drop=True)
# O reset_index é opcional, mas boa prática após um filtro

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# CONSTRUÇÃO DO GRÁFICO COM DOIS EIXOS Y:

# Primeiro eixo Y - Ticket Médio:
axs["C"].plot(ticket_medio_mes['Dia'], ticket_medio_mes['Ticket Médio'],
         marker='o', linestyle='-', linewidth=2, label='Ticket Médio Diário')
axs["C"].set_ylabel('Ticket Médio (R$)', color='steelblue', fontsize=10)
axs["C"].tick_params(axis='y', labelcolor="steelblue")
axs["C"].set_title('Relação Ticket Médio x Número de Cupons - 2025', fontsize=11, weight='bold')
axs["C"].set_xlabel('Meses', fontsize=10)

# Valores sobre os Pontos Ticket Médio (Rótulos de Dados):
for dia, ticket in zip(ticket_medio_mes['Dia'], ticket_medio_mes['Ticket Médio']):
    axs["C"].text(
        dia,
        ticket + 0.1,  # Adiciona um pequeno offset (+5) para ficar acima do ponto
        f"{ticket:,.2f}", # Formata o valor sem casas decimais e com separador de milhar
        ha='center',
        va='bottom',
        fontsize=9,
        color='dimgrey',
        weight='bold'
    )

axs["C"].grid(True, linestyle='--', alpha=0.4)

# - - - - - - - - - - - - - - - - - - - - - - - - - - -
ax2 = axs["C"].twinx()  # Criar um segundo eixo Y compartilhando o eixo X
# - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Segundo eixo Y - Cupons por Dia:
ax2.plot(dados_cupons_mes['Dia'], dados_cupons_mes['Cupons por Dia'],
         marker='s', linestyle='-', color='darkred', linewidth=2, alpha=0.15, label='Cupons por Dia')
ax2.set_ylabel('Cupons por Dia', color='darkred', fontsize=10)
ax2.tick_params(axis='y', labelcolor='darkred')

ax2.grid(False)

# Garantir que todos os dias de Outubro (1 a 31) apareçam no eixo X
#dias = range(1, len(dados_diarios_mes) + 1)
axs["C"].set_xticks(dias)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # AJUSTES FIGURA:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
fig.suptitle("Dashboard Mês a Mês - Scada Café - Loja Cinema - 2025", fontsize=16, fontweight='bold', color='darkgrey')

# Gerar arquivo .PNG do gráfico:
plt.savefig("dashboard_Mes_a_Mes.png", dpi=300, bbox_inches="tight")

plt.show()


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# DASHBOARD: Mural de Resultados:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Criação de Mosaico:
mosaico_mes = "AAA;BBC" # Definição do mosaico onde serão alocados os gráficos
fig = plt.figure(figsize=(14, 10)) # Criação da figura dos gráficos
espacamento = {'wspace': 0.15, 'hspace': 0.3} # Variável para definição de espaçamentos
axs = fig.subplot_mosaic(mosaico_mes, gridspec_kw=espacamento) # Criação do sistema de eixos

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO A:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# FATURAMENTO X META MENSAL:
faturamento_por_mes = faturamento_df.groupby("Mês")[["Faturamento", "Meta"]].sum().reset_index()

media_faturamento_mes = faturamento_por_mes.loc[
    faturamento_por_mes["Mês"] != nome_do_mes_corrente, "Faturamento" # .loc[condição, coluna] → exclui esse mês.
].mean() # .mean() → calcula a média somente dos meses restantes.

# === Ordenar meses ===
faturamento_por_mes["Mês"] = pd.Categorical(faturamento_por_mes["Mês"],
                                     categories=ordem_meses,
                                     ordered=True)
faturamento_por_mes = faturamento_por_mes.sort_values("Mês")

# Calcular percentual atingido da meta
faturamento_por_mes["Percentual"] = faturamento_por_mes["Faturamento"] / faturamento_por_mes["Meta"]

# === Criar o gráfico de barras ===
barras_meta = axs["A"].bar(faturamento_por_mes["Mês"], faturamento_por_mes["Meta"], label="Meta", color="darkorange", alpha=0.4)
barras_faturamento = axs["A"].bar(faturamento_por_mes["Mês"], faturamento_por_mes["Faturamento"],label="Faturamento", color="steelblue")
#axs["A"].bar_label(barras_meta, fmt="{:,.0f}", padding=3, fontsize=8, label='Meta')

# Inserir rótulos com percentual sobre as barras de faturamento:
axs["A"].bar_label(
    barras_faturamento,
    labels=faturamento_por_mes["Percentual"].apply(lambda x: f"{x:.0%}"),
    padding=3,
    fontsize=8,
    fontweight='bold'
)

# === Linha média ===
axs["A"].axhline(y=media_faturamento_mes, color="darkred", linestyle="--", alpha=0.3, linewidth=2,
            label="Média")

# === Personalização ===
axs["A"].set_title("Faturamento x Meta Mensal", fontsize=14, weight='bold')
#ax.set_xlabel("Mês")
axs["A"].set_ylabel("Valores (R$)")
axs["A"].set_xticks(range(len(faturamento_por_mes)))
axs["A"].set_xticklabels(faturamento_por_mes["Mês"], rotation=45, fontsize=8) # rotation=45, fontsize=8
#ax.set_yticklabels(fontsize=8)
axs["A"].legend(loc="lower left")
axs["A"].grid(False)
axs["A"].grid(axis="y", linestyle="--", alpha=0.6)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO B:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PERDAS POR MÊS:
perdas_mes = axs["B"].bar(perdas_por_mes['Mês'], perdas_por_mes['Quantidade'], color='red', alpha=0.3, label='Perdas')
media_perdas_mes = perdas_por_mes['Quantidade'].mean()

# --- NOVIDADE: Linha de Média ---
axs["B"].axhline(
    y=media_perdas_mes,
    #color='salmon',
    linestyle='--', # Linha tracejada
    alpha=0.5,
    linewidth=2,
    label=f"Média Mês ({media_perdas_mes:,.0f})" # Adicionar label da média na legenda com o valor formatado
)

# === Personalização ===
axs["B"].set_title('Perdas Por Mês', fontsize=14, weight='bold')
axs["B"].set_ylabel("Quantidade")
#axs["D"].set_xlabel("Mês")
axs["B"].grid(False)
axs["B"].set_xticks(range(len(perdas_por_mes)))
axs["B"].set_xticklabels(perdas_por_mes["Mês"], rotation=45, fontsize=8)
axs["B"].grid(axis="y", linestyle="--", alpha=0.4)
axs["B"].legend()

# === Valores sobre as barras ===
axs["B"].bar_label(
    perdas_mes, # Variável que recebeu a instrução do gráfico
    label=perdas_por_mes["Quantidade"], # Informação a ser exibida em cima de cada barra
    padding=3, # Posição do texto em relação à barra
    fontsize=9, # Tamanho da fonte
    fontweight='bold', # Fonte em negrito
    color="dimgrey" # Cor do texto
    )

# Muda a cor da barra para valores abaixo da média:
for i, barra in enumerate(perdas_mes):
    if perdas_por_mes["Quantidade"].iloc[i] < media_perdas_mes:
        barra.set_color('green')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GRAFICO C:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PERDAS POR MOTIVO:
perdas_cat = axs["C"].pie(
    perdas_motivo['Item'],
    labels=perdas_motivo['Motivo'],
    autopct='%1.1f%%',
    startangle=140,
    textprops={'fontsize': 10, 'weight': 'bold', 'color': 'black'}
)

# === Personalização ===
axs["C"].set_title(f'Perdas por Categoria', fontsize=14, weight='bold')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # AJUSTES FIGURA:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
fig.suptitle(f"Dashboard - Scada Café - Loja Cinema - 2025 (Resultado Parcial)", fontsize=16, fontweight='bold', color='darkgrey')

# Gerar arquivo .PNG do gráfico:
plt.savefig("dashboard_Mes_Mural.png", dpi=300, bbox_inches="tight")

plt.show()


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# ENVIO DE RELATÓRIO POR EMAIL:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Importação de bibliotecas necessárias:
import smtplib # Biblioteca para envio de emails
import email.message # Biblioteca para manipulação de mensagens de email
from senha_email import senha_app # Importa a senha do email de um arquivo externo
from email.mime.multipart import MIMEMultipart # Biblioteca para manipulação de emails com múltiplas partes
from email.mime.text import MIMEText # Biblioteca para manipulação de texto em emails
from email.mime.application import MIMEApplication # Biblioteca para manipulação de anexos em emails
import os # Biblioteca para manipulação de arquivos e diretórios

# Formatação de variáveis para email:
def dataframe_para_html(df):
    return df.to_html(
        index=False,
        border=0,
        justify="center",
        classes="tabela-relatorio"
    )

# Criação de função para enviar email:
def enviar_email():
    msg = MIMEMultipart()
    msg["Subject"] = "Relatório Scada Café - Loja Cinema"
    msg["From"] = "alex.pereira82log@gmail.com"
    msg["To"] = "alex.barista@icloud.com"
    
    # Link da imagem de assinatura hospedada:
    link_imagem = "https://d3p2amk7tvag7f.cloudfront.net/pdvs/245f27d9196ae3b2c5dcc6dd6f6f1be7f861db7c.png"
    
    # Corpo do email em HTML:
    tabela_mes = dataframe_para_html(faturamento_por_mes)
    tabela_dia_semana = dataframe_para_html(faturamento_dia_semana)

    corpo_email = f"""
    <html>
    <head>
    <style>
        .tabela-relatorio {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 10px;
            margin-bottom: 20px;
            font-family: Arial, sans-serif;
            font-size: 14px;
        }}

        .tabela-relatorio th {{
            background-color: #2F4F4F;
            color: #FFFFFF;
            padding: 8px;
            border: 1px solid #DDDDDD;
            text-align: center;
        }}

        .tabela-relatorio td {{
            padding: 8px;
            border: 1px solid #DDDDDD;
            text-align: center;
        }}
    </style>
    </head>

    <body>
    <p>Segue relatório de análises e resultados atualizado referente às vendas de Scada Café (Loja Cinema).</p>

    <p><strong><span style="text-decoration: underline;">RESUMO DADOS FATURAMENTO:</span></strong></p>
    <p style='margin:0;'>- Meta Mês: <strong>R$ {meta_mes_corrente:,.2f}</strong></p>
    <p style='margin:0;'>- Faturamento Total: <strong>R$ {soma_faturamento:,.2f}</strong></p>
    <p style='margin:0;'>- Faturamento Médio Dia: <strong>R$ {faturamento_medio_dia:,.2f}</strong></p>
    <p style='margin:0;'>- Média Cupons Dia: <strong>{media_cupons_dia:.0f}</strong></p>
    <p style='margin:0;'>- Ticket Médio Dia: <strong>R$ {ticket_medio_dia:,.2f}</strong></p>
    
    <p><strong><span style="text-decoration: underline;">PROJEÇÕES E RECUPERAÇÃO META:</span></strong></p>
    <p>- Ainda faltam <strong>R$ {meta_mes_corrente - soma_faturamento:,.2f}</strong> para atingirmos a  meta do mês.</p>
    <p> </p>
    <p>- Estamos projetando <strong>R$ {projecao_faturamento:,.2f}</strong> de faturamento no mês.</p>
    <p> </p>
    <p>- Precisamos de <strong>R$ {ticket_meta_dia:,.0f} por mesa ou R$ {fat_meta_dia:,.0f} por dia</strong> para alcançarmos a meta do mês.</p>
    <p> </p>

    <p><strong><span style="text-decoration: underline;">FATURAMENTO POR MÊS:</span></strong></p>
    {tabela_mes}
    
    <p><strong><span style="text-decoration: underline;">FATURAMENTO POR DIA DA SEMANA:</span></strong></p>
    {tabela_dia_semana}

    <p style='margin:0;'>Att,<br>Alex Pereira</p>
        <img src='{link_imagem}' style='max-width:150px; width:100%; height:auto;'>

    </body>
    </html>
    """
    
    # Anexando o corpo do email em HTML
    msg.attach(MIMEText(corpo_email, "html"))

    # Anexar arquivos de uma pasta específica:
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))

    # Lista os arquivos na pasta informada
    lista_arquivos = os.listdir(diretorio_atual)
    for nome_arquivo in lista_arquivos:
        if nome_arquivo.lower().endswith(".png"):
            caminho_arquivo = os.path.join(diretorio_atual, nome_arquivo)
            with open(caminho_arquivo, "rb") as arquivo:
                msg.attach(MIMEApplication(arquivo.read(), Name=nome_arquivo))

    servidor = smtplib.SMTP("smtp.gmail.com", 587)
    servidor.starttls()
    # Substitua pela sua senha de aplicativo
    servidor.login(msg["From"], senha_app)
    servidor.send_message(msg)
    servidor.quit()

    # Confirmação envio email:
    print("Email enviado com sucesso!")
    
enviar_email()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# FIM DO CÓDIGO:
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
