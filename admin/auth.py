import streamlit as st

from admin.config import ADMIN_PASSWORD


# ==========================================
# INICIALIZAR SESSÃO
# ==========================================

def inicializar_admin():

    if "admin_logado" not in st.session_state:
        st.session_state.admin_logado = False

    if "login_key" not in st.session_state:
        st.session_state.login_key = 0


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
        key=f"senha_admin_{st.session_state.login_key}"
    )

    if st.button("Entrar", key="btn_login_admin"):

        if senha == ADMIN_PASSWORD:

            st.session_state.admin_logado = True

            # Limpa o campo de senha
            st.session_state.admin_logado = True

            # Força a recriação do campo de senha
            st.session_state.login_key += 1

            st.success("Status: ✅ Acesso liberado")

            st.rerun()

        else:

            st.error("Senha incorreta.")

    return st.session_state.admin_logado