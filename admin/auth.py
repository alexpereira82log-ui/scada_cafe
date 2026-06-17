import streamlit as st

from admin.config import ADMIN_PASSWORD


# ==========================================
# INICIALIZAR SESSÃO
# ==========================================

def inicializar_admin():
    """
    Cria a variável de sessão que controla
    se o administrador está autenticado.
    """

    if "admin_logado" not in st.session_state:
        st.session_state.admin_logado = False


# ==========================================
# TELA DE LOGIN
# ==========================================

def autenticar_admin():
    """
    Exibe o campo de senha e realiza
    a autenticação do administrador.
    """

    inicializar_admin()

    senha = st.text_input(
        "Digite a senha de administrador",
        type="password",
        key="senha_admin"
    )

    if st.button("Entrar", key="btn_login_admin"):

        if senha == ADMIN_PASSWORD:

            st.session_state.admin_logado = True
            st.success("Status: ✅ Acesso liberado")

            # Recarrega a página para atualizar a interface
            st.rerun()

        else:

            st.error("Senha incorreta.")

    return st.session_state.admin_logado