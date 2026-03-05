# ============================================================
# ANALISE DE DADOS SCADA CAFÉ:
# ============================================================

# ============================================================
# IMPORTS:
# ============================================================
import matplotlib.pyplot as plt
import numpy as np
import calendar
import pandas as pd
import sqlite3
import locale
import smtplib # Biblioteca para envio de emails
import os
import time
import email.message # Biblioteca para manipulação de mensagens de email
import subprocess


from datetime import date, datetime
from cycler import cycler
from email.message import EmailMessage
from senha_email import senha_app  # Importa a senha do email de um arquivo externo
from email.mime.multipart import MIMEMultipart # Biblioteca para manipulação de emails com múltiplas partes
from email.mime.text import MIMEText # Biblioteca para manipulação de texto em emails
from email.mime.application import MIMEApplication # Biblioteca para manipulação de anexos em emails


# ============================================================
# CALCULAR QTD DE DIAS PARA O FIM DO MÊS:
# ============================================================
# Data atual
hoje = date.today()

# Extrair mês atual
mes = hoje.month

# Último dia do mês atual
ultimo_dia_mes = calendar.monthrange(hoje.year, mes)[1]

# Cálculo dos dias restantes incluindo hoje
dias_restantes = ultimo_dia_mes - hoje.day + 1

# Lista de nomes dos meses
meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

mes_nome = meses[mes]

print(f"Faltam {dias_restantes} dia(s) para terminar {mes_nome}.")


# ============================================================
# CONEXÃO COM O BANCO DE DADOS E CRIAÇÃO DO DATAFRAME:
# ============================================================
# Importando a base de dados do SQL através do PANDAS:

with sqlite3.connect("faturamento_scada.db") as conexao:
    base_fat_df = pd.read_sql("SELECT * FROM base_fat", conexao)
    base_comissao_df = pd.read_sql("SELECT * FROM comissao_colaborador", conexao)
    base_perdas_df = pd.read_sql("SELECT * FROM perdas", conexao)
    base_produtos_df = pd.read_sql("SELECT * FROM venda_produtos", conexao)


# ============================================================
# TRATAMENTO DE DADOS:
# ============================================================

# Garantir que colunas numéricas estejam corretas:
colunas_numericas_produtos = ["qtd", "valor_unit", "valor_total", "perc_total_venda"]

for col in colunas_numericas_produtos:
    base_produtos_df[col] = (
        base_produtos_df[col]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace("%", "", regex=False)
    )
    base_produtos_df[col] = pd.to_numeric(base_produtos_df[col], errors="coerce")

# Alterar formato de colunas:
base_fat_df["meta"] = pd.to_numeric(base_fat_df["meta"], errors="coerce")
base_fat_df["faturamento"] = pd.to_numeric(base_fat_df["faturamento"], errors="coerce")
base_fat_df['data'] = pd.to_datetime(base_fat_df['data'])

base_comissao_df['data'] = pd.to_datetime(base_comissao_df['data'])

base_produtos_df['mes'] = pd.to_datetime(base_produtos_df['mes'])

# Criação de colunas auxiliares:
base_fat_df["ano"] = base_fat_df["data"].dt.year
base_fat_df["mes"] = base_fat_df["data"].dt.month
base_fat_df["mes_nome"] = base_fat_df["data"].dt.strftime("%B")

base_comissao_df["ano"] = base_comissao_df["data"].dt.year
base_comissao_df["mes"] = base_comissao_df["data"].dt.month
base_comissao_df["mes_nome"] = base_comissao_df["data"].dt.strftime("%B")

base_produtos_df["ano"] = base_produtos_df["mes"].dt.year
base_produtos_df["mes_num"] = base_produtos_df["mes"].dt.month
base_produtos_df["mes_nome"] = base_produtos_df["mes"].dt.strftime("%B")

# Exibir nome dos meses na coluna 'mes' em português:
locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

base_fat_df["mes_nome"] = base_fat_df["data"].dt.strftime("%B")
base_fat_df["mes_nome"] = base_fat_df["data"].dt.strftime("%B").str.capitalize()

base_comissao_df["mes_nome"] = base_comissao_df["data"].dt.strftime("%B")
base_comissao_df["mes_nome"] = base_comissao_df["data"].dt.strftime("%B").str.capitalize()

base_produtos_df["mes_nome"] = base_produtos_df["mes"].dt.strftime("%B")
base_produtos_df["mes_nome"] = base_produtos_df["mes"].dt.strftime("%B").str.capitalize()


# ============================================================
# FILTRO DE DADOS E CRIAÇÃO DE VARIÁVEIS AUXILIARES:
# ============================================================
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

# Filtro de dados por Ano e por Mês:
base_filtro_ano = base_fat_df[base_fat_df["data"].dt.year == ANO_EXIBICAO]
base_filtro_mes = base_filtro_ano[base_filtro_ano['data'].dt.month == MES_EXIBICAO]

base_comiss_ano = base_comissao_df[base_comissao_df['data'].dt.year == ANO_EXIBICAO]
base_comiss_mes = base_comissao_df[base_comissao_df['data'].dt.month == MES_EXIBICAO]

# Soma total do faturamento do mes corrente:
total_fat_mes_corrente = base_filtro_mes['faturamento'].sum()

# Exibe a o total de faturamento de todos os meses do ano ordenados:
fat_por_mes = (
    base_filtro_ano
    .groupby(['mes', "mes_nome"])[["faturamento", 'meta']]
    .sum()
    .reset_index()
    .sort_values(["mes"])
)

# Exibe o faturamento do mes corrente dia a dia:
fat_por_dia = base_filtro_mes[['data', 'faturamento']]

fat_por_dia = ( 
fat_por_dia
    .dropna(subset=["faturamento"]) # Exclui as linhas com faturamento zerados
)

# Média de faturamento por dia da semana (ano corrente):
media_fat_dia_semana = (
    base_filtro_ano
    .groupby('dia_semana')[['faturamento', 'ticket_medio', 'cupom']]
    .mean()
    .reindex(ordem_dias_semana)
    .round(0)
    .reset_index()
)

# Meta do mês corrente:
meta_mes = base_filtro_mes['meta'].sum(min_count=1)
meta_mes = 0 if pd.isna(meta_mes) else float(meta_mes)
# Percentual atingido da meta do mês corrente:
perc_meta_mes = (total_fat_mes_corrente / meta_mes) if meta_mes != 0 else 0
#perc_meta_mes = (total_fat_mes_corrente / meta_mes * 100) if meta_mes != 0 else 0
# Mẽdia de faturamento por dia do mês corrente:
media_fat_dia = fat_por_dia["faturamento"].mean()
# Total de cupons no mês corrente:
total_cupom_mes_corrente = base_filtro_mes['cupom'].sum()
# Ticket Mẽdio mês corrente:
ticket_medio_mes = total_fat_mes_corrente / total_cupom_mes_corrente if total_cupom_mes_corrente != 0 else 0
#ticket_medio_mes = total_fat_mes_corrente / total_cupom_mes_corrente
# Média de cupons por dia do mês corrente:
media_cupom = base_filtro_mes['cupom'].mean()
# Montante faltante para atingir a meta do mês corrente:
falta_para_meta = base_filtro_mes['meta'].sum() - total_fat_mes_corrente
# Projeção de faturamento para o mês corrente:
proj_fat_mes = total_fat_mes_corrente + (media_fat_dia * dias_restantes)
# Faturamento diário necessário para alcançar a meta:
meta_fat_dia = falta_para_meta / dias_restantes
# Ticket Médio necessário para alcançar a meta:
meta_ticket_dia = meta_fat_dia / media_cupom
# Diferença entre Meta de ticket Médio e Ticket realizado:
diferenca_ticket = meta_ticket_dia - ticket_medio_mes
# Faturamento por Equipe:
fat_eq_1 = base_filtro_mes[base_filtro_mes['equipe'] == '1']['faturamento'].sum()
fat_eq_2 = base_filtro_mes[base_filtro_mes['equipe'] == '2']['faturamento'].sum()
# Ticket Médio por Equipe:
ticket_eq_1 = base_filtro_mes[base_filtro_mes['equipe'] == '1']['ticket_medio'].mean()
ticket_eq_2 = base_filtro_mes[base_filtro_mes['equipe'] == '2']['ticket_medio'].mean()

# Total de comissão acumulada atual:
conn = sqlite3.connect("faturamento_scada.db")
cursor = conn.cursor()

cursor.execute("""
SELECT COALESCE(SUM(rateio_dia),0)
FROM (
    SELECT data, MAX(valor) AS rateio_dia
    FROM comissao_colaborador
    WHERE presente = 1
    GROUP BY data
)
""")

comissao_acum = cursor.fetchone()[0]

conn.close()

# Mẽdia de Comissão diária:
conn = sqlite3.connect("faturamento_scada.db")
cursor = conn.cursor()

cursor.execute("""
SELECT COALESCE(AVG(rateio_dia),0)
FROM (
    SELECT data, MAX(valor) AS rateio_dia
    FROM comissao_colaborador
    WHERE presente = 1
    GROUP BY data
)
""")

comissao_media_dia = cursor.fetchone()[0]

conn.close()

# Projeção de Comissão para o mês:
comissao_proj = comissao_acum + (comissao_media_dia * dias_restantes)

# Soma comissão individual:
conn = sqlite3.connect("faturamento_scada.db")
cursor = conn.cursor()

cursor.execute("""
SELECT c.nome, COALESCE(SUM(cc.valor),0) AS total_comissao
FROM colaboradores c
LEFT JOIN comissao_colaborador cc
    ON c.id = cc.colaborador_id
GROUP BY c.nome
ORDER BY total_comissao DESC
""")

comissao_ind = cursor.fetchall()

conn.close()

# Variaveis da base de perdas:
base_perdas_df["data"] = pd.to_datetime(
    base_perdas_df["data"],
    #format="%Y/%m/%d"
)

# Formatando a coluna 'qtd' para que seja possível gerar calculos:
base_perdas_df['qtd'] = (
    base_perdas_df['qtd']
    .str.replace(',', '.', regex=False)
    .str.extract(r'(\d+\.?\d*)')[0]
    .astype(float)
)

# Filtrando as bases:
# Por ano:
perdas_motivo_ano = base_perdas_df[base_perdas_df["data"].dt.year == ANO_EXIBICAO]
perdas_motivo_filtrado2 = perdas_motivo_ano.groupby("motivo")[["item"]].count().reset_index()

venda_produtos_ano = base_produtos_df[base_produtos_df["ano"] == ANO_EXIBICAO]
venda_produtos_filtrado = (
    venda_produtos_ano
    .groupby("produto")
    .agg({
        "qtd": "sum",
        "valor_total": "sum",
        "valor_unit": "mean",
        "perc_total_venda": "mean"
    })
    .reset_index()
)

# Por Mês:
perdas_motivo_mes = base_perdas_df[(base_perdas_df["data"].dt.month == MES_EXIBICAO) & (base_perdas_df["data"].dt.year == ANO_EXIBICAO)]
perdas_motivo_filtrado = perdas_motivo_mes.groupby("motivo")[["item"]].count().reset_index()

venda_produtos_mes = base_produtos_df[(base_produtos_df["mes_num"] == MES_EXIBICAO) & (base_produtos_df["ano"] == ANO_EXIBICAO)]
venda_produtos_filtrado2 = (
    venda_produtos_mes
    .groupby("produto")
    .agg({
        "qtd": "sum",
        "valor_total": "sum",
        "valor_unit": "mean",
        "perc_total_venda": "mean"
    })
    .reset_index()
)


# Ordenar por valores:
perdas_motivo_filtrado = perdas_motivo_filtrado.sort_values("item", ascending=False).reset_index(drop=True)
perdas_motivo_filtrado2 = perdas_motivo_filtrado2.sort_values("item", ascending=False).reset_index(drop=True)

venda_produtos_filtrado = venda_produtos_filtrado.sort_values("qtd", ascending=False).reset_index(drop=True)
venda_produtos_filtrado2 = venda_produtos_filtrado2.sort_values("qtd", ascending=False).reset_index(drop=True)
# Relação de perdas do mês:
relacao_perdas_mes = base_perdas_df[(base_perdas_df["data"].dt.month == MES_EXIBICAO) & (base_perdas_df["data"].dt.year == ANO_EXIBICAO)]
# Somatório total do número de ocorrências de perdas:
total_perdas_mes = perdas_motivo_filtrado["item"].sum()
#total_perdas_ano = perdas_motivo_ano.groupby('data')[['item']].count().reset_index()
total_perdas_ano = (
    perdas_motivo_ano
    .groupby(perdas_motivo_ano['data'].dt.to_period('M'))['item']
    .count()
    .reset_index()
)

relatorio_fat = base_filtro_mes
relatorio_perdas = perdas_motivo_mes
relatorio_comissao = base_comiss_mes

# Garantindo que as variáveis abaixo são numéricas:
meta_mes = float(meta_mes)
total_fat_mes_corrente = float(total_fat_mes_corrente)
media_fat_dia = float(media_fat_dia)
media_cupom = float(media_cupom)
ticket_medio_mes = float(ticket_medio_mes)
proj_fat_mes = float(proj_fat_mes)
meta_ticket_dia = float(meta_ticket_dia)
meta_fat_dia = float(meta_fat_dia)


# ============================================================
# ============================================================
# CRIAÇÃO DE FUNÇÕES:
# ============================================================
# ============================================================

# CONFIGURAÇÕES DE EMAIL
EMAIL_REMETENTE = "alex.pereira82log@gmail.com"
EMAIL_DESTINOS = "alex.barista@icloud.com"


# FUNÇÃO PARA EXPORTAR EXCEL
def exportar_excel(df, nome_base):
    """
    Exporta um DataFrame para Excel com nome automático.
    Ajusta colunas numéricas para 2 casas decimais.
    """

    # Criar cópia para evitar SettingWithCopyWarning
    df = df.copy()

    # Arredondar colunas numéricas
    colunas_numericas = df.select_dtypes(include=["float", "int"]).columns
    for col in colunas_numericas:
        df.loc[:, col] = df[col].round(2)

    # Nome do arquivo
    nome_arquivo = f"{nome_base}.xlsx"

    # Exportar
    df.to_excel(nome_arquivo, index=False, engine="openpyxl")

    print(f"Arquivo gerado: {nome_arquivo}")

    return nome_arquivo


# FUNÇÃO PARA ENVIAR EMAIL COM ANEXO
def enviar_email_com_anexo(caminho_arquivo):

    try:
        msg = EmailMessage()

        # Nome do arquivo sem extensão (para usar como título)
        nome_arquivo = os.path.basename(caminho_arquivo)
        titulo_email = os.path.splitext(nome_arquivo)[0]

        msg["Subject"] = titulo_email
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = ", ".join(EMAIL_DESTINOS)
        msg["Cc"] = "alex.pereira82log@gmail.com"

        msg.set_content("Segue em anexo o relatório gerado automaticamente.")

        # Ler arquivo
        with open(caminho_arquivo, "rb") as f:
            file_data = f.read()

        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=nome_arquivo
        )

        # Conexão SMTP (mesmo padrão que já funcionava)
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, senha_app)
        servidor.send_message(msg)
        servidor.quit()

        print("Email enviado com sucesso!")

    except Exception as e:
        print(f"Erro ao enviar email: {e}")


# FUNÇÕES DE GERAÇÃO DOS RELATÓRIOS
def gerar_relatorio_faturamento():
    arquivo = exportar_excel(relatorio_fat, "Relatorio_Faturamento")
    enviar_email_com_anexo(arquivo)


def gerar_relatorio_perdas():
    arquivo = exportar_excel(relatorio_perdas, "Relatorio_Perdas")
    enviar_email_com_anexo(arquivo)


def gerar_relatorio_comissao():
    # CONEXÃO COM BANCO
    conn = sqlite3.connect("faturamento_scada.db")

    query = """
    SELECT 
        cc.data,
        c.nome AS colaborador,
        cc.valor
    FROM comissao_colaborador cc
    JOIN colaboradores c
        ON c.id = cc.colaborador_id
    ORDER BY cc.data
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    # CRIAR TABELA GERENCIAL (PIVOT)
    tabela_comissao = df.pivot_table(
        index="data",
        columns="colaborador",
        values="valor",
        aggfunc="sum",
        fill_value=0
    )

    # TOTAL POR COLABORADOR
    tabela_comissao.loc["TOTAL"] = tabela_comissao.sum()

    # EXPORTAR PARA EXCEL
    nome_arquivo = "Relatorio_Comissao_Gerencial.xlsx"

    tabela_comissao.to_excel(
        nome_arquivo,
        engine="openpyxl"
    )

    print("Relatório de comissão gerado com sucesso!")

    # ABRIR O EXCEL AUTOMATICAMENTE
    try:
        subprocess.Popen(["xdg-open", nome_arquivo])
    except Exception as e:
        print(f"Não foi possível abrir o arquivo automaticamente: {e}")

    # ENVIAR EMAIL COM ANEXO
    enviar_email_com_anexo(nome_arquivo)

def aguardar_comando():
    input("\nPressione ENTER para voltar ao menu...")


# ============================================================
# ============================================================
# MENU DE OPÇÕES:
# ============================================================
# ============================================================

while True:
    os.system("cls" if os.name == "nt" else "clear")
    print("DADOS SCADA CAFE - CINEMA")
    print("-----------------------------------")
    print("1 Faturamento por Mês")
    print("2 Faturamento por Dia")
    print("3 Média Fat por Dia da Semana")
    print("4 Top 10 venda Produtos")
    print("5 Resumo Resultado Faturamento")
    print("6 Projeções e Recuperação Meta")
    print("7 Performance Venda por Equipe")
    print("8 Projeção Comissão")
    print("9 Perdas por Mês")
    print("10 Perdas Mês Corrente")
    print("11 GRÁFICO - Dados Mês Atual")
    print("12 GRÁFICO - Evolução Meses")
    print("13 GRÁFICO - Impressão para Mural")
    print("14 Enviar Dados de Faturamento por Email")
    print("15 Gerar relatório Faturamento")
    print("16 Gerar relatório Comissão")
    print("17 Gerar relatório Perdas")
    print("'x' para Sair")
    escolha = input("Escolha uma opção: ")
    
    if escolha == "1":
        print("\n" + "-" * 50)
        print(" FATURAMENTO POR MÊS:")
        print(fat_por_mes)
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "2":
        print("\n" + "-" * 50)
        print(" FATURAMENTO POR DIA:")
        print(fat_por_dia)
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "3":
        print("\n" + "-" * 50)
        print(" MÉDIAS POR DIA DA SEMANA:")
        print(media_fat_dia_semana)
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "4":
        print("\n" + "-" * 50)
        print("- RANKING PRODUTOS MAIS VENDIDOS:")
        print('NO ANO:')
        print(venda_produtos_filtrado.head(10))
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "5":
        print("\n" + "-" * 50)
        print(f'- DADOS FATURAMENTO - {mes_nome}:')
        print(f' Meta Mês: R$ {meta_mes:,.2f}')
        print(f' Faturamento atual: R$ {total_fat_mes_corrente:,.2f}')
        print(f' % Meta: {perc_meta_mes:.0%}')
        print(f' Faturamento Médio Dia: R$ {media_fat_dia:,.2f}')
        print(f' Ticket Médio Dia: R$ {ticket_medio_mes:,.2f}')
        print(f' Média Cupons Dia: {media_cupom:.0f}')
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "6":
        print("\n" + "-" * 50)
        print('- PROJEÇÕES E RECUPERAÇÃO META:')
        print(f' Ainda faltam R$ {falta_para_meta:,.2f} para atingirmos a  meta do mês.')
        print(f' Estamos projetando R$ {proj_fat_mes:,.2f} de faturamento no mês.')
        print(f' Precisamos de R$ {meta_ticket_dia:,.0f} por mesa ou R$ {meta_fat_dia:,.0f} por dia para alcançarmos a meta do mês.')
        print(f' Isso representa R$ {meta_ticket_dia - ticket_medio_mes:,.0f} a mais por mesa mediante aos R$ {ticket_medio_mes:,.0f} realizado atualmente.')
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "7":
        print("\n" + "-" * 50)
        print('- RESULTADO POR EQUIPE:')
        print(f' Faturamento Equipe 01: R$ {fat_eq_1:,.0f}')
        print(f' Faturamento Equipe 02: R$ {fat_eq_2:,.0f}')
        print(f' Ticket Médio Equipe 01: R$ {ticket_eq_1:,.0f}')
        print(f' Ticket Médio Equipe 02: R$ {ticket_eq_2:,.0f}')
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "8":
        print("\n" + "-" * 50)
        print("- PROJEÇÃO COMISSÃO:")
        print(f' Comissão atual: R$ {comissao_acum:,.2f}')
        print(f' Média diária: R$ {comissao_media_dia:,.2f}')
        print(f" Projeção comissão: R$ {comissao_proj:,.2f}")
        print("\n" + "-" * 50)
        print("\nCOMISSÃO ACUMULADA POR COLABORADOR")
        print("-" * 40)
        for nome, valor in comissao_ind:
            print(f"{nome}: R$ {valor:,.2f}")
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "9":
        print("\n" + "-" * 50)
        print("- PERDAS POR MÊS:")
        print(total_perdas_ano)
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "10":
        print("\n" + "-" * 50)
        print("- PERDAS MÊS CORRENTE:")
        print(relacao_perdas_mes)
        print("\n" + "-" * 50)
        print("- PERDAS POR MOTIVO:")
        print(perdas_motivo_filtrado)
        print(f"Total: {total_perdas_mes}")
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "11":
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
        
        # DASHBOARD: Mês Corrente:
        #--------------------------
        # Criação de Mosaico:
        mosaico = "AB;CD" # Definição do mosaico onde serão alocados os gráficos
        fig = plt.figure(figsize=(14, 10)) # Criação da figura dos gráficos
        espacamento = {'wspace': 0.12, 'hspace': 0.3} # Variável para definição de espaçamentos
        axs = fig.subplot_mosaic(mosaico, gridspec_kw=espacamento) # Criação do sistema de eixos

        # GRAFICO A:
        #----------------
        # FATURAMENTO POR DIA:
        # Agrupar por dia e somar o Faturamento
        # Nota: Como já filtramos por mês, o 'Dia' aqui será o dia do mês (1, 2, 3...)
        dados_diarios_mes = base_filtro_mes.groupby(base_filtro_mes['data'].dt.day)['faturamento'].sum().reset_index()

        # NOVIDADE CRUCIAL: FILTRAR APENAS DIAS COM FATURAMENTO MAIOR QUE ZERO
        dados_diarios_mes = dados_diarios_mes[
            dados_diarios_mes['faturamento'] > 0
        ].reset_index(drop=True) # O reset_index é opcional, mas boa prática após um filtro

        # --- NOVIDADE: 1.4 Calcular a Média ---
        media_diaria = dados_diarios_mes['faturamento'].mean()

        # .plot() é o comando para gráficos de linha
        axs["A"].plot(
            dados_diarios_mes['data'],
            dados_diarios_mes['faturamento'],
            marker='o',          # Adiciona um marcador para cada dia
            linestyle='-',       # Linha contínua
            linewidth=2,
            label="Faturamento"
        )

        # --- NOVIDADE: Linha de Média ---
        axs["A"].axhline(
            y=media_diaria,
            color='red',
            linestyle='--', # Linha tracejada
            alpha=0.3,
            linewidth=2,
            label=f"Média Diária ({media_diaria:,.0f} R$)" # Adicionar label da média na legenda com o valor formatado
        )

        # --- NOVIDADE: Valores sobre os Pontos (Rótulos de Dados) ---
        for dia, faturamento in zip(dados_diarios_mes['data'], dados_diarios_mes['faturamento']):
            axs["A"].text(
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
        axs["A"].set_title(f'Faturamento Diário', fontsize=14, weight='bold')
        axs["A"].set_xlabel('Dia do Mês', fontsize=10)
        axs["A"].set_ylabel('Faturamento (R$)', fontsize=10)
        axs["A"].tick_params(axis="x", rotation=45, labelsize=8)


        # Garantir que todos os dias do mês apareçam no eixo X
        dias = range(1, len(dados_diarios_mes) + 1)
        axs["A"].set_xticks(dias)

        axs["A"].legend()
        axs["A"].grid(True, linestyle='--', alpha=0.4)

        # GRAFICO B:
        #------------
        # RELAÇÃO TICKET MÉDIO X NÚMERO DE CUPONS:
        # VARIÁVEIS TICKET:
        ticket_medio_mes_corrente = base_filtro_mes.groupby(base_filtro_mes['data'].dt.day)['ticket_medio'].mean().reset_index()
        # Filtrar faturamento maior que '0':
        ticket_medio_mes_corrente = ticket_medio_mes_corrente[
            ticket_medio_mes_corrente['ticket_medio'] > 0
        ].reset_index(drop=True) # O reset_index é opcional, mas boa prática após um filtro
        # Linha de Média
        media_ticket_mes_corrente = ticket_medio_mes_corrente['ticket_medio'].mean()

        # VARIÁVEIS CUPONS: - - - - - - - - - - - - - - - - - - - - - - - - 
        dados_cupons_mes_corrente = base_filtro_mes.groupby(base_filtro_mes['data'].dt.day)['cupom'].sum().reset_index()
        # Filtrar cupos maior que '0':
        dados_cupons_mes_corrente = dados_cupons_mes_corrente[dados_cupons_mes_corrente['cupom'] > 0].reset_index(drop=True)
        # O reset_index é opcional, mas boa prática após um filtro
        # Calcular a Média de Cupons
        media_cupons_mes_corrente = dados_cupons_mes_corrente['cupom'].mean()

        # CONSTRUÇÃO DO GRÁFICO COM DOIS EIXOS Y:
        axs["B"].grid(True, linestyle='--', alpha=0.4)

        # Primeiro eixo Y - Ticket Médio:
        axs["B"].plot(ticket_medio_mes_corrente['data'], ticket_medio_mes_corrente['ticket_medio'],
                marker='o', linestyle='-', linewidth=2, label='Ticket Médio Diário')
        axs["B"].set_ylabel('Ticket Médio (R$)', color='steelblue')
        axs["B"].set_xlabel('Dia do Mês', fontsize=10)
        axs["B"].tick_params(axis='y', labelcolor="steelblue")
        axs["B"].set_title(f'Relação Ticket Médio x Número de Cupons', fontsize=11, weight='bold')

        # Linha de Média Ticket Médio:
        media_ticket_mes_corrente = ticket_medio_mes_corrente['ticket_medio'].mean()
        axs["B"].axhline(
            y=media_ticket_mes_corrente,
            color='red',
            linestyle='--', # Linha tracejada
            alpha=0.3,
            linewidth=2,
            label=f"Média Ticket Dia ({media_ticket_mes_corrente:,.0f} R$)" # Adicionar label da média na legenda com o valor formatado
        )
        # Valores sobre os Pontos Ticket Médio (Rótulos de Dados):
        for dia, ticket in zip(ticket_medio_mes_corrente['data'], ticket_medio_mes_corrente['ticket_medio']):
            axs["B"].text(
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
        ax2 = axs["B"].twinx()  # Criar um segundo eixo Y compartilhando o eixo X
        # - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Segundo eixo Y - Cupons por Dia:
        ax2.plot(dados_cupons_mes_corrente['data'], dados_cupons_mes_corrente['cupom'],
                marker='s', linestyle='-', color='darkred', linewidth=2, alpha=0.15, label=f'Cupons por Dia ({media_cupons_mes_corrente:.0f})')
        ax2.set_ylabel('Cupons por Dia', color='darkred')
        ax2.tick_params(axis='y', labelcolor='darkred')

        #Ajuste de grid do gráfico de linhas para Cupons - AX2:
        #ax2.grid(axis='y', linestyle='--', alpha=0.4)
        ax2.grid(False)

        # Garantir que todos os dias do mês apareçam no eixo X
        dias = range(1, len(dados_diarios_mes) + 1)
        axs["B"].set_xticks(dias)
        axs["B"].set_xticklabels(dados_cupons_mes_corrente["data"], rotation=45, fontsize=8)

        # Adicionar legendas ancorando a posição fixa (x, y) / bbox_transform para posicionar em relação a área do gráfico
        axs["B"].legend(bbox_transform=ax2.transAxes)
        ax2.legend()


        # GRAFICO C:
        #-------------
        # PERDAS POR MÊS:
        # Agrupar por mês:
        perdas_por_mes = (
            base_perdas_df
            .groupby(base_perdas_df['data'].dt.month)['qtd']
            .count()
            .reindex(range(1,13), fill_value=0)
            .reset_index()
        )

        # Criar nome do mês a partir do número (mantendo coluna 'data')
        perdas_por_mes['mes'] = perdas_por_mes['data'].map(
            dict(zip(range(1,13), ordem_meses))
        )

        # Ordenar corretamente:
        perdas_por_mes['mes'] = pd.Categorical(
            perdas_por_mes['mes'],
            categories=ordem_meses,
            ordered=True
        )
        perdas_por_mes = perdas_por_mes.sort_values('mes')

        # Filtrar meses com perdas > 0
        perdas_por_mes = perdas_por_mes.loc[perdas_por_mes['qtd'] > 0].copy()

        media_perdas_mes = perdas_por_mes['qtd'].mean()

        perdas_mes = axs["C"].bar(
            perdas_por_mes['mes'],
            perdas_por_mes['qtd'],
            color='red',
            alpha=0.3,
            label='Perdas'
        )

        # --- NOVIDADE: Linha de Média ---
        axs["C"].axhline(
            y=media_perdas_mes,
            #color='salmon',
            linestyle='--', # Linha tracejada
            alpha=0.5,
            linewidth=2,
            label=f"Média Mês ({media_perdas_mes:,.0f})" # Adicionar label da média na legenda com o valor formatado
        )

        # === Personalização ===
        axs["C"].set_title('Perdas Por Mês', fontsize=14, weight='bold')
        #axs["C"].set_xlabel("Mês")
        axs["C"].set_ylabel("Quantidade")
        axs["C"].tick_params(axis="x", rotation=45, labelsize=8)
        axs["C"].grid(False)
        axs["C"].grid(axis="y", linestyle="--", alpha=0.4)
        axs["C"].legend()

        # === Valores sobre as barras ===
        axs["C"].bar_label(
            perdas_mes, # Variável que recebeu a instrução do gráfico
            labels=perdas_por_mes["qtd"], # Informação a ser exibida em cima de cada barra
            padding=3, # Posição do texto em relação à barra
            fontsize=9, # Tamanho da fonte
            fontweight='bold', # Fonte em negrito
            color="dimgrey" # Cor do texto
            )

        # Muda a cor da barra para valores abaixo da média:
        for i, barra in enumerate(perdas_mes):
            if perdas_por_mes["qtd"].iloc[i] < media_perdas_mes:
                barra.set_color('green')


        # GRAFICO D:
        #-----------------
        # PERDAS POR MOTIVO:
        perdas_cat = axs["D"].pie(
            perdas_motivo_filtrado['item'],
            labels=perdas_motivo_filtrado['motivo'],
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 10, 'weight': 'bold', 'color': 'black'}
        )

        # === Personalização ===
        axs["D"].set_title(f'Perdas por Categoria (Mês)', fontsize=14, weight='bold')


        # AJUSTES FIGURA:
        #-----------------
        fig.suptitle(f"Dashboard Scada Café - Loja Cinema - {mes_nome} {ANO_EXIBICAO}", fontsize=16, fontweight='bold', color='darkgrey')

        # Gerar arquivo .PNG do gráfico:
        plt.savefig("dashboard_Mes_Corrente_cinema.png", dpi=300, bbox_inches="tight")

        plt.show()
        aguardar_comando()

    elif escolha == "12":
        # ==============================
        # CONFIGURAÇÕES INICIAIS
        # ==============================

        cores = plt.get_cmap('tab10').colors
        ciclo_cores = cycler('color', cores)
        plt.rc('axes', prop_cycle=ciclo_cores)

        ordem_meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]

        mosaico_mes = "AA;BC"
        fig = plt.figure(figsize=(14, 10))
        espacamento = {'wspace': 0.15, 'hspace': 0.3}
        axs = fig.subplot_mosaic(mosaico_mes, gridspec_kw=espacamento)

        # ==============================
        # GRAFICO A - FATURAMENTO X META
        # ==============================

        faturamento_por_mes = (
            base_filtro_ano
            .groupby(base_filtro_ano["data"].dt.month)
            .agg({
                "faturamento": "sum",
                "meta": "sum"
            })
            .reset_index()
        )

        faturamento_por_mes.rename(columns={"data": "mes"}, inplace=True)

        faturamento_por_mes["mes_nome"] = faturamento_por_mes["mes"].apply(
            lambda x: ordem_meses[x - 1]
        )

        faturamento_por_mes = faturamento_por_mes.sort_values("mes")

        # Média do faturamento
        media_faturamento_mes = faturamento_por_mes["faturamento"].mean()

        barras_meta = axs["A"].bar(
            faturamento_por_mes["mes_nome"],
            faturamento_por_mes["meta"],
            label="Meta",
            color="darkorange",
            alpha=0.4
        )

        barras_faturamento = axs["A"].bar(
            faturamento_por_mes["mes_nome"],
            faturamento_por_mes["faturamento"],
            label="Faturamento",
            color="steelblue"
        )

        axs["A"].bar_label(barras_meta, fmt="{:,.0f}", padding=3, fontsize=8)
        axs["A"].bar_label(barras_faturamento, fmt="{:,.0f}", padding=3, fontsize=8, fontweight='bold')

        axs["A"].axhline(
            y=media_faturamento_mes,
            linestyle="--",
            alpha=0.4,
            linewidth=2,
            label=f"Média ({media_faturamento_mes:,.0f})"
        )

        axs["A"].set_title(f"Faturamento x Meta Mensal {ANO_EXIBICAO}", fontsize=14, weight='bold')
        axs["A"].set_ylabel("Valores (R$)")
        axs["A"].tick_params(axis="x", rotation=45, labelsize=8)
        axs["A"].legend(loc="lower left")
        axs["A"].grid(axis="y", linestyle="--", alpha=0.6)

        # ==============================
        # GRAFICO B - MÉDIA FATURAMENTO
        # ==============================

        faturamento_por_dia = (
            base_filtro_ano
            .groupby(base_filtro_ano['data'].dt.month)['faturamento']
            .mean()
            .reset_index()
        )

        faturamento_por_dia.rename(columns={"data": "mes"}, inplace=True)

        axs["B"].plot(
            faturamento_por_dia["mes"],
            faturamento_por_dia["faturamento"],
            marker='o',
            linewidth=2,
            label="Fat Médio Dia"
        )

        for mes, valor in zip(faturamento_por_dia["mes"], faturamento_por_dia["faturamento"]):
            axs["B"].text(
                mes,
                valor,
                f"{valor:,.0f}",
                ha='center',
                va='bottom',
                fontsize=9,
                alpha=0.7,
                color='dimgrey',
                weight='bold'
            )

        axs["B"].set_title(f'Faturamento Médio - {ANO_EXIBICAO}', fontsize=14, weight='bold')
        axs["B"].set_xlabel('Mês')
        axs["B"].set_ylabel('Média Faturamento (R$)')
        axs["B"].set_xticks(faturamento_por_dia["mes"])
        axs["B"].grid(True, linestyle='--', alpha=0.4)

        # ==============================
        # GRAFICO C - TICKET X CUPONS
        # ==============================

        ticket_medio_mes = (
            base_filtro_ano
            .groupby(base_filtro_ano['data'].dt.month)['ticket_medio']
            .mean()
            .reset_index()
        )

        ticket_medio_mes.rename(columns={"data": "mes"}, inplace=True)

        dados_cupons_mes = (
            base_filtro_ano
            .groupby(base_filtro_ano['data'].dt.month)['cupom']
            .mean()
            .reset_index()
        )

        dados_cupons_mes.rename(columns={"data": "mes"}, inplace=True)

        axs["C"].plot(
            ticket_medio_mes["mes"],
            ticket_medio_mes["ticket_medio"],
            marker='o',
            linewidth=2,
            label='Ticket Médio'
        )

        axs["C"].set_ylabel('Ticket Médio (R$)', color='steelblue', fontsize=10)
        axs["C"].set_xlabel('Mês')
        axs["C"].grid(True, linestyle='--', alpha=0.4)

        for mes, ticket in zip(ticket_medio_mes["mes"], ticket_medio_mes["ticket_medio"]):
            axs["C"].text(
                mes,
                ticket,
                f"{ticket:,.2f}",
                ha='center',
                va='bottom',
                fontsize=9,
                color='dimgrey',
                weight='bold'
            )

        ax2 = axs["C"].twinx()

        ax2.plot(
            dados_cupons_mes["mes"],
            dados_cupons_mes["cupom"],
            marker='s',
            linestyle='-',
            linewidth=2,
            color='darkred',
            alpha=0.15,
            label='Cupons'
        )

        ax2.set_ylabel('Cupons por Dia', color='darkred', fontsize=10)
        ax2.tick_params(axis='y', labelcolor='darkred')

        axs["C"].set_title(f'Relação Ticket Médio x Cupons - {ANO_EXIBICAO}', fontsize=12, weight='bold')

        # ==============================
        # AJUSTES FINAIS
        # ==============================

        fig.suptitle(
            f"Dashboard Mês a Mês - Scada Café - Loja Cinema - {ANO_EXIBICAO}",
            fontsize=16,
            fontweight='bold',
            color='darkgrey'
        )

        plt.savefig("dashboard_Mes_a_Mes_cinema.png", dpi=300, bbox_inches="tight")
        plt.show()

        aguardar_comando()

    elif escolha == '13':

        # ==============================
        # CONFIGURAÇÕES INICIAIS
        # ==============================

        cores = plt.get_cmap('tab10').colors
        ciclo_cores = cycler('color', cores)
        plt.rc('axes', prop_cycle=ciclo_cores)

        ordem_meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]

        mosaico_mes = "AAA;BBC"
        fig = plt.figure(figsize=(14, 10))
        espacamento = {'wspace': 0.15, 'hspace': 0.3}
        axs = fig.subplot_mosaic(mosaico_mes, gridspec_kw=espacamento)

        # ==============================
        # GRAFICO A - FATURAMENTO X META
        # ==============================

        faturamento_por_mes = (
            base_filtro_ano
            .groupby(base_filtro_ano["data"].dt.month)
            .agg({
                "faturamento": "sum",
                "meta": "sum"
            })
            .reset_index()
        )

        faturamento_por_mes.rename(columns={"data": "mes"}, inplace=True)

        faturamento_por_mes["mes_nome"] = faturamento_por_mes["mes"].apply(
            lambda x: ordem_meses[x - 1]
        )

        faturamento_por_mes = faturamento_por_mes.sort_values("mes")

        # Calcular percentual atingido da meta
        faturamento_por_mes["Percentual"] = faturamento_por_mes["faturamento"] / faturamento_por_mes["meta"]

        # Média do faturamento
        media_faturamento_mes = faturamento_por_mes["faturamento"].mean()

        barras_meta = axs["A"].bar(
            faturamento_por_mes["mes_nome"],
            faturamento_por_mes["meta"],
            label="Meta",
            color="darkorange",
            alpha=0.4
        )

        barras_faturamento = axs["A"].bar(
            faturamento_por_mes["mes_nome"],
            faturamento_por_mes["faturamento"],
            label="Faturamento",
            color="steelblue"
        )

        # Inserir rótulos com percentual sobre as barras de faturamento:
        axs["A"].bar_label(
            barras_faturamento,
            labels=faturamento_por_mes["Percentual"].apply(lambda x: f"{x:.0%}"),
            padding=3,
            fontsize=8,
            fontweight='bold'
        )

        axs["A"].axhline(
            y=media_faturamento_mes,
            linestyle="--",
            alpha=0.4,
            linewidth=2,
            label=f"Média ({media_faturamento_mes:,.0f})"
        )

        axs["A"].set_title(f"Faturamento x Meta Mensal {ANO_EXIBICAO}", fontsize=14, weight='bold')
        axs["A"].set_ylabel("Valores (R$)")
        axs["A"].tick_params(axis="x", rotation=45, labelsize=8)
        axs["A"].legend(loc="lower left")
        axs["A"].grid(axis="y", linestyle="--", alpha=0.6)

        # =========================================================
        # GRÁFICO B — PERDAS POR MÊS
        # =========================================================
        
        # PERDAS POR MÊS:
        # Agrupar por mês:
        perdas_por_mes = (
            base_perdas_df
            .groupby(base_perdas_df['data'].dt.month)['qtd']
            .count()
            .reindex(range(1,13), fill_value=0)
            .reset_index()
        )

        # Criar nome do mês a partir do número (mantendo coluna 'data')
        perdas_por_mes['mes'] = perdas_por_mes['data'].map(
            dict(zip(range(1,13), ordem_meses))
        )

        # Ordenar corretamente:
        perdas_por_mes['mes'] = pd.Categorical(
            perdas_por_mes['mes'],
            categories=ordem_meses,
            ordered=True
        )
        perdas_por_mes = perdas_por_mes.sort_values('mes')

        # Filtrar meses com perdas > 0
        perdas_por_mes = perdas_por_mes.loc[perdas_por_mes['qtd'] > 0].copy()

        media_perdas_mes = perdas_por_mes['qtd'].mean()

        perdas_mes = axs["B"].bar(
            perdas_por_mes['mes'],
            perdas_por_mes['qtd'],
            color='red',
            alpha=0.3,
            label='Perdas'
        )

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
        #axs["C"].set_xlabel("Mês")
        axs["B"].set_ylabel("Quantidade")
        axs["B"].tick_params(axis="x", rotation=45, labelsize=8)
        axs["B"].grid(False)
        axs["B"].grid(axis="y", linestyle="--", alpha=0.4)
        axs["B"].legend()

        # === Valores sobre as barras ===
        axs["B"].bar_label(
            perdas_mes, # Variável que recebeu a instrução do gráfico
            labels=perdas_por_mes["qtd"], # Informação a ser exibida em cima de cada barra
            padding=3, # Posição do texto em relação à barra
            fontsize=9, # Tamanho da fonte
            fontweight='bold', # Fonte em negrito
            color="dimgrey" # Cor do texto
            )

        # Muda a cor da barra para valores abaixo da média:
        for i, barra in enumerate(perdas_mes):
            if perdas_por_mes["qtd"].iloc[i] < media_perdas_mes:
                barra.set_color('green')


        # =========================================================
        # GRÁFICO C — PERDAS POR MOTIVO
        # =========================================================
        # PERDAS POR MOTIVO:
        perdas_cat = axs["C"].pie(
            perdas_motivo_filtrado2['item'],
            labels=perdas_motivo_filtrado2['motivo'],
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 10, 'weight': 'bold', 'color': 'black'}
        )

        # === Personalização ===
        axs["C"].set_title(f'Perdas por Categoria (Ano)', fontsize=14, weight='bold')


        # =========================================================
        # AJUSTES FINAIS
        # =========================================================
        fig.suptitle(f"Dashboard - Scada Café - Loja Cinema - {ANO_EXIBICAO}", fontsize=16, fontweight='bold', color='darkgrey')

        # Gerar arquivo .PNG do gráfico:
        plt.savefig("dashboard_Mes_Mural_cinema.png", dpi=300, bbox_inches="tight")

        plt.show()
        aguardar_comando()

    elif escolha == '14':

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # ENVIO DE RELATÓRIO POR EMAIL:
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
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
            msg["Subject"] = f"Relatório Scada Café - Loja Cinema - {ANO_EXIBICAO}"
            msg["From"] = "alex.pereira82log@gmail.com"
            msg["To"] = "alex.barista@icloud.com"
            
            # Link da imagem de assinatura hospedada:
            link_imagem = "https://d3p2amk7tvag7f.cloudfront.net/pdvs/245f27d9196ae3b2c5dcc6dd6f6f1be7f861db7c.png"
            
            # Corpo do email em HTML:
            tabela_mes = dataframe_para_html(fat_por_mes)
            tabela_dia_semana = dataframe_para_html(media_fat_dia_semana)

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
            <p style='margin:0;'><strong>{mes_nome} {ANO_EXIBICAO}</strong></p>

            <p><strong><span style="text-decoration: underline;">RESUMO DADOS FATURAMENTO:</span></strong></p>
            <p style='margin:0;'>- Meta Mês: <strong>R$ {meta_mes:,.2f}</strong></p>
            <p style='margin:0;'>- Faturamento Total: <strong>R$ {total_fat_mes_corrente:,.2f}</strong></p>
            <p style='margin:0;'>- Faturamento Médio Dia: <strong>R$ {media_fat_dia:,.2f}</strong></p>
            <p style='margin:0;'>- Média Cupons Dia: <strong>{media_cupom:.0f}</strong></p>
            <p style='margin:0;'>- Ticket Médio Dia: <strong>R$ {ticket_medio_mes:,.2f}</strong></p>
            
            <p><strong><span style="text-decoration: underline;">PROJEÇÕES E RECUPERAÇÃO META:</span></strong></p>
            <p>- Ainda faltam <strong>R$ {meta_mes - total_fat_mes_corrente:,.2f}</strong> para atingirmos a  meta do mês.</p>
            <p> </p>
            <p>- Estamos projetando <strong>R$ {proj_fat_mes:,.2f}</strong> de faturamento no mês.</p>
            <p> </p>
            <p>- Precisamos de <strong>R$ {meta_ticket_dia:,.0f} por mesa ou R$ {meta_fat_dia:,.0f} por dia</strong> para alcançarmos a meta do mês.</p>
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
                if nome_arquivo.lower().endswith("cinema.png"):
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

    elif escolha == '15':
        gerar_relatorio_faturamento()
        aguardar_comando()

    elif escolha == '16':
        gerar_relatorio_comissao()
        aguardar_comando()

    elif escolha == '17':
        gerar_relatorio_perdas()
        aguardar_comando()


    elif escolha == "x":
            break
    else:
        print("Opção inválida")
        time.sleep(1)

#------------------------------------------------------------------------------------------------------------



