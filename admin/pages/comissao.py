import streamlit as st
import pandas as pd

from datetime import date

from services.comissao_service import (
    obter_comissao_dia,
    listar_rateio_dia,
    recalcular_rateio,
    salvar_rateio,
    listar_colaboradores_ativos,
    obter_resumo_mensal_comissao,
)

from services.afastamento_service import (
    aplicar_afastamento,
    obter_calendario_mensal,
)

from services.relatorio_comissao_service import (
    obter_relatorio_mensal_comissao,
)




def tela_comissao():
    """
    Tela administrativa para gestão da comissão dos colaboradores.
    """

    st.subheader("💰 Gestão de Comissão")



    if st.session_state.pop("comissao_salva", False):
        st.success(
            "Comissão atualizada com sucesso!"
        )

    if st.session_state.pop("afastamento_salvo", False):
        st.success(
            "Afastamento registrado com sucesso!"
        )


    hoje = date.today()

    ano = hoje.year
    mes = hoje.month

    # ==========================================================
    # Resumo Mensal
    # ==========================================================

    st.markdown("## 📈 Resumo Mensal")

    resumo = obter_resumo_mensal_comissao(
        ano,
        mes,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "💰 Taxa Serviço",
            f"R$ {resumo['taxa_servico']:,.2f}"
        )

    with col2:
        st.metric(
            "💵 Comissão (80%)",
            f"R$ {resumo['comissao_total']:,.2f}"
        )

    with col3:
        st.metric(
            "📅 Média Diária",
            f"R$ {resumo['media_diaria']:,.2f}"
        )

    with col4:
        st.metric(
            "👤 Média Individual",
            f"R$ {resumo['media_individual']:,.2f}"
        )

    with col5:
        st.metric(
            "📈 Projeção Individual",
            f"R$ {resumo['projecao_final']:,.2f}"
        )

    # ==========================================================
    # Comissão Diária
    # ==========================================================

    with st.expander(
        "📅 Comissão Diária",
        expanded=True,
    ):

        data = st.date_input(
            "📅 Data da operação"
        )

        comissao = obter_comissao_dia(data)

        if comissao is None:

            st.warning(
                "Ainda não existe comissão registrada para esta data."
            )

        else:

            valor_taxa = float(
                comissao["valor_taxa_servico"] or 0
            )

            valor_rateio = valor_taxa * 0.80

            participantes = listar_rateio_dia(data)

            dados = []

            for colaborador in participantes:

                dados.append({
                    "ID": colaborador["id"],
                    "Participa": colaborador["presente"],
                    "Colaborador": colaborador["nome"],
                    "Comissão": round(
                        colaborador["valor"],
                        2
                    ),
                })

            df = pd.DataFrame(dados)

            st.markdown("### 👥 Participação do Dia")

            df_editado = st.data_editor(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "ID": None,

                    "Participa": st.column_config.CheckboxColumn(
                        "Elegível"
                    ),

                    "Colaborador": st.column_config.TextColumn(
                        "Colaborador"
                    ),

                    "Comissão": st.column_config.NumberColumn(
                        "Comissão",
                        format="R$ %.2f",
                    ),
                },
                disabled=[
                    "Colaborador",
                    "Comissão",
                ],
            )

            participantes_interface = df_editado.to_dict("records")

            participantes = [
                {
                    "id": participante["ID"],
                    "nome": participante["Colaborador"],
                    "presente": participante["Participa"],
                    "valor": participante["Comissão"],
                }
                for participante in participantes_interface
            ]

            participantes, elegiveis, valor_individual = recalcular_rateio(
                participantes,
                valor_rateio,
            )

            st.markdown("### 📊 Resultado do Rateio")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "💰 Taxa de Serviço",
                    f"R$ {valor_taxa:,.2f}"
                )

            with col2:
                st.metric(
                    "💵 Valor para Rateio (80%)",
                    f"R$ {valor_rateio:,.2f}"
                )

            with col3:
                st.metric(
                    "👥 Elegíveis",
                    elegiveis
                )

            with col4:
                st.metric(
                    "🪙 Comissão Individual",
                    f"R$ {valor_individual:,.2f}"
                )

            st.divider()

            col1, col2 = st.columns([1, 5])

            with col1:

                salvar = st.button(
                    "💾 Salvar",
                    use_container_width=True,
                )

            if salvar:

                salvar_rateio(
                    data,
                    participantes,
                )

                st.session_state["comissao_salva"] = True

                st.rerun()

    # ==========================================================
    # Afastamentos Programados
    # ==========================================================

    with st.expander(
        "🗓️ Afastamentos Programados",
        expanded=False,
    ):

        colaboradores = listar_colaboradores_ativos()

        col1, col2 = st.columns(2)

        with col1:

            colaborador = st.selectbox(
                "👤 Colaborador",
                options=colaboradores,
                format_func=lambda c: c["nome"],
            )

            motivo = st.selectbox(
                "📌 Motivo",
                options=[
                    "Férias",
                    "Atestado",
                    "Folga",
                    "Licença",
                    "Outro",
                ],
            )

        with col2:

            data_inicio = st.date_input(
                "📅 Data inicial"
            )

            data_fim = st.date_input(
                "📅 Data final"
            )

        btn_aplicar_afastamento = st.button(
            "🗓️ Aplicar Afastamento",
            use_container_width=True,
        )

        if btn_aplicar_afastamento:

            afastamento = {
                "colaborador_id": colaborador["id"],
                "colaborador_nome": colaborador["nome"],
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "motivo": motivo,
                "observacao": "",
            }

            aplicar_afastamento(afastamento)

            st.session_state["afastamento_salvo"] = True

            st.rerun()

    
    # ==========================================================
    # Calendário Mensal
    # ==========================================================

    with st.expander(
        "📅 Calendário Mensal",
        expanded=False,
    ):

        calendario = obter_calendario_mensal(
            ano,
            mes,
        )

        df_calendario = pd.DataFrame(
            calendario
        )

        styler = df_calendario.style

        st.dataframe(
            styler,
            use_container_width=True,
            hide_index=True,
        )

    # ==========================================================
    # Relatório Gerencial
    # ==========================================================

    with st.expander(
        "📊 Relatório Gerencial de Comissão",
        expanded=False,
    ):

        relatorio = obter_relatorio_mensal_comissao(
            ano,
            mes,
        )

        df_relatorio = pd.DataFrame(
            relatorio
        )

        # ==========================================================
        # Formatação monetária
        # ==========================================================

        colunas_valores = df_relatorio.columns[1:]

        df_relatorio[colunas_valores] = (
            df_relatorio[colunas_valores]
            .round(2)
        )

        st.dataframe(
            df_relatorio,
            use_container_width=True,
            hide_index=True,
        )
