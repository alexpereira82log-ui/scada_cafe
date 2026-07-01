import streamlit as st
from datetime import date

from services.perdas import (
    inserir_perda,
    carregar_colaboradores
)


def tela_perdas():

    st.subheader("⚠️ Gestão de Perdas")

    st.caption(
        "Registre, consulte e administre as perdas operacionais."
    )

    st.divider()

    with st.expander("➕ Registrar Perda", expanded=True):

        data = st.date_input(
            "Data",
            value=date.today(),
            format="DD/MM/YYYY"
        )

        item = st.text_input(
            "Item"
        )

        categoria = st.selectbox(
            "Categoria",
            [
                "Produto final",
                "Utensilio",
                "Insumo",
                "Hortifruti",
                "Produto de limpeza",
                "Outro"
            ]
        )

        qtd = st.text_input(
            "Quantidade"
        )

        motivo = st.selectbox(
            "Motivo",
            [
                "Lançamento errado",
                "Erro de processo",
                "Saiu sem pagar",
                "Quebra",
                "Venceu (validade)",
                "Cliente",
                "Outro"
            ]
        )

        responsavel = st.selectbox(
            "Responsável",
            carregar_colaboradores()
        )

        obs = st.text_area(
            "Observação"
        )

        st.divider()

        if st.button("💾 Salvar Registro"):
            
            if not item.strip():

                st.warning("Informe o item da perda.")

            elif not qtd.strip():

                st.warning("Informe a quantidade.")

            else:
                try:

                    inserir_perda(
                        data,
                        item,
                        categoria,
                        qtd,
                        motivo,
                        responsavel,
                        obs
                    )

                    st.success(
                        "Registro inserido com sucesso!"
                    )

                except Exception as e:

                    st.error(str(e))

