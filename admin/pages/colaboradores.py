import streamlit as st

from services.colaboradores import (
    listar_colaboradores,
    adicionar_colaborador
)


def tela_colaboradores():

    st.subheader("👥 Gestão de Colaboradores")

    st.caption(
        "Cadastre, edite e gerencie os colaboradores do sistema."
    )

    st.divider()

    with st.expander("➕ Novo colaborador"):

        novo_nome = st.text_input(
            "Nome do colaborador"
        )

        if st.button("Salvar colaborador"):

            if novo_nome.strip():

                adicionar_colaborador(novo_nome)

                st.success(
                    "Colaborador cadastrado com sucesso!"
                )

                st.rerun()

            else:

                st.warning(
                    "Informe um nome."
                )

    colaboradores = listar_colaboradores()

    st.write("### Colaboradores cadastrados")

    st.dataframe(
        colaboradores,
        use_container_width=True,
        hide_index=True
    )