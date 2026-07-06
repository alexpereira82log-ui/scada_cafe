import streamlit as st
import pandas as pd

from services.comissao_service import (
    obter_comissao_dia,
    listar_rateio_dia,
    recalcular_rateio,
    salvar_rateio,
    listar_colaboradores_ativos,
)



def tela_comissao():
    """
    Tela administrativa para gestão da comissão dos colaboradores.
    """

    st.subheader("💰 Gestão de Comissão")

    # ==========================================================
    # Resumo Mensal
    # ==========================================================

    st.markdown("## 📈 Resumo Mensal")

    st.info(
        "Resumo mensal em desenvolvimento."
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

            participantes = df_editado.to_dict("records")

            participantes, elegiveis, valor_individual = recalcular_rateio(
                participantes,
                valor_rateio
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
                    participantes
                )

                st.success(
                    "Comissão atualizada com sucesso!"
                )

                st.rerun()

    # ==========================================================
    # Afastamentos Programados
    # ==========================================================

    with st.expander(
        "🗓️ Afastamentos Programados",
        expanded=False,
    ):

        colaboradores = listar_colaboradores_ativos()

        nomes_colaboradores = [
            colaborador["nome"]
            for colaborador in colaboradores
        ]

        col1, col2 = st.columns(2)

        with col1:

            colaborador = st.selectbox(
                "👤 Colaborador",
                options=nomes_colaboradores,
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

        st.button(
            "✔ Aplicar Afastamento",
            use_container_width=True,
        )