import streamlit as st

from admin.auth import autenticar_admin
from admin.pages.faturamento import tela_faturamento
from admin.pages.perdas import tela_perdas
from admin.pages.metas import tela_metas
from admin.pages.colaboradores import tela_colaboradores

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
        st.success("🔓 Área administrativa liberada.")

    with col2:

        if st.button("🚪 Sair"):

            st.session_state.admin_logado = False

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

        tela_faturamento()

    elif opcao == "Perdas":

        tela_perdas()

    elif opcao == "Metas":

        tela_metas()

    elif opcao == "Colaboradores":

        tela_colaboradores()