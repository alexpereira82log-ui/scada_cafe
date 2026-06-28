import streamlit as st
from datetime import date

from services.faturamento import (
    consultar_faturamento,
    editar_faturamento
)


def tela_faturamento():

    st.subheader("💰 Gestão de Faturamento")

    st.caption(
        "Consulte e altere os dados de faturamento registrados no sistema."
    )

    st.divider()

    # ==========================================
    # ESTADO DA TELA
    # ==========================================

    if "registro_faturamento" not in st.session_state:
        st.session_state.registro_faturamento = None

    # ==========================================
    # CONSULTA
    # ==========================================

    data_consulta = st.date_input(
        "Data",
        value=date.today(),
        format="DD/MM/YYYY"
    )

    if st.button("🔍 Carregar dados"):

        try:

            st.session_state.registro_faturamento = consultar_faturamento(
                data_consulta
            )

            st.success("Registro localizado com sucesso!")

        except ValueError as e:

            st.error(str(e))

    # ==========================================
    # EXIBIÇÃO DOS DADOS
    # ==========================================

    if st.session_state.registro_faturamento:

        registro = st.session_state.registro_faturamento

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            faturamento = st.number_input(
                "💰 Faturamento",
                value=float(registro["faturamento"]),
                step=1.0
            )

            cupom = st.number_input(
                "🧾 Cupons",
                value=int(registro["cupom"]),
                step=1
            )

        with col2:

            meta = st.number_input(
                "🎯 Meta",
                value=float(registro["meta"]),
                step=0.01,
                format="%.2f"
            )

            ticket_medio = st.number_input(
                "🎟 Ticket Médio",
                value=float(registro["ticket_medio"]),
                step=0.01,
                format="%.2f"
            )

        st.divider()

        if st.button("💾 Salvar alterações"):

            try:

                editar_faturamento(
                    registro["data"],
                    faturamento,
                    meta,
                    cupom,
                    ticket_medio
                )

                st.success(
                    "Faturamento atualizado com sucesso!"
                )

                st.session_state.registro_faturamento = consultar_faturamento(
                    registro["data"]
                )

                st.rerun()

            except ValueError as e:

                st.error(str(e))

            except Exception as e:

                st.error(f"Erro inesperado: {e}")