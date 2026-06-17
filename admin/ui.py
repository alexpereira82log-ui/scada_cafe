import streamlit as st

from admin.auth import autenticar_admin


# ==========================================
# ÁREA ADMINISTRATIVA
# ==========================================

def exibir_area_admin():

    st.subheader("🔒 Administração")

    st.markdown(
        """
        Área restrita para gerenciamento do sistema.

        Apenas usuários autorizados podem acessar
        as funcionalidades administrativas.
        """
    )

    # --------------------------------------
    # AUTENTICAÇÃO
    # --------------------------------------

    if not autenticar_admin():

        st.info("Informe a senha para continuar.")

        return

    # --------------------------------------
    # MENU ADMINISTRATIVO
    # --------------------------------------

    col1, col2 = st.columns([4, 1])

    with col1:
        st.success("Administrador autenticado.")

    with col2:

        if st.button("🚪 Sair"):

            st.session_state.admin_logado = False

            # Limpa o campo de senha
            if "senha_admin" in st.session_state:
                st.session_state.senha_admin = ""

            st.rerun()

    st.divider()


    opcao = st.selectbox(
        "Selecione o módulo",
        [
            "Página Inicial",
            "Faturamento",
            "Perdas",
            "Metas",
            "Colaboradores"
        ]
    )

    if opcao == "Página Inicial":

        st.info(
            "Selecione um módulo acima para iniciar."
        )

    elif opcao == "Faturamento":

        st.warning("Módulo em desenvolvimento.")

    elif opcao == "Perdas":

        st.warning("Módulo em desenvolvimento.")

    elif opcao == "Metas":

        st.warning("Módulo em desenvolvimento.")

    elif opcao == "Colaboradores":

        st.warning("Módulo em desenvolvimento.")