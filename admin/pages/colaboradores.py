import streamlit as st

from services.colaboradores import (
    listar_colaboradores,
    listar_colaboradores_select,
    adicionar_colaborador,
    editar_colaborador,
    alterar_status_colaborador
)


def tela_colaboradores():

    st.subheader("👥 Gestão de Colaboradores")

    st.caption(
        "Cadastre, edite e gerencie os colaboradores do sistema."
    )

    st.divider()

    # ==========================================
    # NOVO COLABORADOR
    # ==========================================

    with st.expander("➕ Novo colaborador"):

        novo_nome_colaborador = st.text_input(
            "Nome do colaborador"
        )

        if st.button("Salvar colaborador"):

            if novo_nome_colaborador.strip():

                try:

                    adicionar_colaborador(novo_nome_colaborador)

                    st.success(
                        "Colaborador cadastrado com sucesso!"
                    )

                    st.rerun()

                except ValueError as e:

                    st.error(str(e))

            else:

                st.warning("Informe um nome.")

    # ==========================================
    # EDITAR COLABORADOR
    # ==========================================

    with st.expander("✏️ Editar colaborador"):

        colaboradores_select = listar_colaboradores_select()

        colaborador = st.selectbox(
            "Colaborador",
            colaboradores_select,
            format_func=lambda x: x[1]
        )

        novo_nome_colaborador = st.text_input(
            "Novo nome"
        )

        if st.button("Salvar alteração"):

            if novo_nome_colaborador.strip():

                try:

                    editar_colaborador(
                        colaborador[0],
                        novo_nome_colaborador
                    )

                    st.success(
                        "Colaborador atualizado com sucesso!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

            else:

                st.warning(
                    "Informe o novo nome."
                )


    # ==========================================
    # DESATIVAR COLABORADOR
    # ==========================================

    with st.expander("🔴 Desativar colaborador"):

        colaboradores_select = listar_colaboradores_select()

        if colaboradores_select:

            colaborador = st.selectbox(
                "Colaborador para desativar",
                colaboradores_select,
                format_func=lambda x: x[1],
                key="desativar_colaborador"
            )

            if st.button("Desativar colaborador"):

                try:

                    alterar_status_colaborador(
                        colaborador[0],
                        False
                    )

                    st.success(
                        "Colaborador desativado com sucesso!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

        else:

            st.info("Não existem colaboradores ativos.")


    # ==========================================
    # REATIVAR COLABORADOR
    # ==========================================

    with st.expander("🟢 Reativar colaborador"):

        colaboradores_select = listar_colaboradores_select(False)

        if colaboradores_select:

            colaborador = st.selectbox(
                "Colaborador para reativar",
                colaboradores_select,
                format_func=lambda x: x[1],
                key="reativar_colaborador"
            )

            if st.button("Reativar colaborador"):

                try:

                    alterar_status_colaborador(
                        colaborador[0],
                        True
                    )

                    st.success(
                        "Colaborador reativado com sucesso!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

        else:

            st.info(
                "Não existem colaboradores inativos."
            )


    # ==========================================
    # LISTAGEM
    # ==========================================

    colaboradores = listar_colaboradores()

    st.subheader("📋 Colaboradores cadastrados")

    st.dataframe(
        colaboradores,
        use_container_width=True,
        hide_index=True
    )