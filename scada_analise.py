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


meses = [
    "",  # índice 0 vazio
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

mes_nome = meses[mes]


#------------------------------------------------------------------------------------------------------------
# CONEXÃO COM O BANCO DE DADOS E CRIAÇÃO DO DATAFRAMEç
# Importando a base de dados do SQL através do PANDAS:
import pandas as pd
import sqlite3

conexao = sqlite3.connect("faturamento_scada.db")
base_fat_df = pd.read_sql("SELECT * FROM base_fat", conexao)
conexao.close()

conexao = sqlite3.connect("faturamento_scada.db")
base_comissao_df = pd.read_sql("SELECT * FROM comissao", conexao)
conexao.close()

conexao = sqlite3.connect("faturamento_scada.db")
base_perdas_df = pd.read_sql("SELECT * FROM perdas", conexao)
conexao.close()

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
# FILTRO DE DADOS E CRIAÇÃO DE VARIÁVEIS AUXILIARES:
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

# Soma total do faturamento do mes corrente:
total_fat_mes_corrente = base_filtro_mes['faturamento'].sum()

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
media_fat_dia_semana = (
    base_filtro_ano
    .groupby(['dia_semana'])['faturamento']
    .mean()
    .reindex(ordem_dias_semana)
    .round(0)
    .reset_index()
)

# Meta do mês corrente:
meta_mes = base_filtro_mes['meta'].sum()
# Percentual atingido da meta do mês corrente:
perc_meta_mes = (total_fat_mes_corrente / meta_mes) * 100
# Mẽdia de faturamento por dia do mês corrente:
media_fat_dia = fat_por_dia["faturamento"].mean()
# Ticket Mẽdio mês corrente:
ticket_medio_mes = fat_por_dia['faturamento'].sum() / base_filtro_mes['cupom'].sum()
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
comissao_acum = base_comissao_df['rateio'].sum()
# Mẽdia de Comissão diária:
comissao_media_dia = base_comissao_df['rateio'].mean()
# Projeção de Comissão para o mês:
comissao_proj = comissao_acum + (comissao_media_dia * dias_restantes)

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

# Filtrando a base de perdas:
perdas_motivo_mes = base_perdas_df
perdas_motivo_mes = perdas_motivo_mes[perdas_motivo_mes["data"].dt.month == MES_EXIBICAO]
perdas_motivo_filtrado = perdas_motivo_mes.groupby("motivo")[["item"]].count().reset_index()

# Por ano:
perdas_motivo_ano = base_perdas_df
perdas_motivo_ano = perdas_motivo_ano[perdas_motivo_ano["data"].dt.year == ANO_EXIBICAO]
perdas_motivo_filtrado2 = perdas_motivo_ano.groupby("motivo")[["item"]].count().reset_index()

#perdas_motivo = perdas_motivo[perdas_motivo["Data da perda"].dt.month == MES_EXIBICAO]
# Ordenar por quantidade de perdas:
perdas_motivo_filtrado = perdas_motivo_filtrado.sort_values("item", ascending=False).reset_index(drop=True)
perdas_motivo_filtrado2 = perdas_motivo_filtrado2.sort_values("item", ascending=False).reset_index(drop=True)
# Relação de perdas do mês:
relacao_perdas_mes = base_perdas_df[base_perdas_df["data"].dt.month == MES_EXIBICAO]
# Somatório total do número de ocorrências de perdas:
total_perdas_mes = perdas_motivo_filtrado["item"].sum()
#total_perdas_ano = perdas_motivo_ano.groupby('data')[['item']].count().reset_index()
total_perdas_ano = (
    perdas_motivo_ano
    .groupby(perdas_motivo_ano['data'].dt.to_period('M'))['item']
    .count()
    .reset_index()
)



#------------------------------------------------------------------------------------------------------------
# MENU DE OPÇÕES:
import os
import time

def aguardar_comando():
    input("\nPressione ENTER para voltar ao menu...")


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
    print("14 Enviar Relatório por Email")
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
        print(' EM CONSTRUÇÃO')
        print("\n" + "-" * 50)
        aguardar_comando()

    elif escolha == "5":
        print("\n" + "-" * 50)
        print(f'- DADOS FATURAMENTO - {mes_nome}:')
        print(f' Meta Mês: R$ {meta_mes:,.2f}')
        print(f' Faturamento atual: R$ {total_fat_mes_corrente:,.2f}')
        print(f' % Meta: {total_fat_mes_corrente / meta_mes:.0%}')
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
        axs["D"].set_title(f'Perdas por Categoria', fontsize=14, weight='bold')


        # AJUSTES FIGURA:
        #-----------------
        fig.suptitle(f"Dashboard Scada Café - Loja Cinema - {mes_nome} {ANO_EXIBICAO}", fontsize=16, fontweight='bold', color='darkgrey')

        # Gerar arquivo .PNG do gráfico:
        plt.savefig("dashboard_Mes_Corrente_cinema.png", dpi=300, bbox_inches="tight")

        plt.show()
        aguardar_comando()







































    elif escolha == "x":
        break
    else:
        print(" Opção inválida")
        time.sleep(1)







#------------------------------------------------------------------------------------------------------------



