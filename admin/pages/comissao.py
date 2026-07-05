import streamlit as st
import pandas as pd

from services.comissao_service import (
    obter_comissao_dia,
    listar_rateio_dia,
    recalcular_rateio,
    salvar_rateio,
)



def tela_comissao():
    """
    Tela administrativa para gestão da comissão dos colaboradores.
    """

    st.subheader("💰 Gestão de Comissão")

    st.divider()

    # ==========================================================
    # Seleção da data
    # ==========================================================

    data = st.date_input(
        "📅 Data da comissão"
    )

    # ==========================================================
    # Consulta da comissão do dia
    # ==========================================================

    comissao = obter_comissao_dia(data)

    if comissao is None:
        st.warning(
            "Ainda não existe comissão registrada para esta data."
        )
        st.stop()


    valor_taxa = float(comissao["valor_taxa_servico"] or 0)
    valor_rateio = valor_taxa * 0.80


    st.divider()


    participantes = listar_rateio_dia(data)

    dados = []

    for colaborador in participantes:

        dados.append({
            "ID": colaborador["id"],
            "Participa": colaborador["presente"],
            "Colaborador": colaborador["nome"],
            "Comissão": round(colaborador["valor"], 2),
        })

    df = pd.DataFrame(dados)

    st.divider()

    st.markdown("### 👥 Participantes")

    df_editado = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "ID": None,

            "Participa": st.column_config.CheckboxColumn(
                "Participa"
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

    df_resultado = pd.DataFrame(participantes)

    # ==========================================================
    # Resumo financeiro
    # ==========================================================

    st.markdown("### 📊 Resumo do Dia")

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

        