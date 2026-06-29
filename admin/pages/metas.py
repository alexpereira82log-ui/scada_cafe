import streamlit as st
from datetime import date

from services.metas import (
    obter_status_mes,
    obter_proximo_mes,
    abrir_novo_mes
)


def tela_metas():

    st.subheader("🎯 Gestão de Metas")

    st.caption(
        "Gerencie a abertura do mês, a importação das metas e ajustes pontuais."
    )

    st.divider()

    # ==========================================
    # STATUS DO MÊS
    # ==========================================

    hoje = date.today()

    ano = hoje.year
    mes = hoje.month

    status = obter_status_mes(
        ano,
        mes
    )

    st.subheader("📊 Status do Mês")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📅 Calendário",
            "✅ Criado" if status["calendario"] else "❌ Não criado"
        )

    with col2:

        st.metric(
            "📆 Dias cadastrados",
            status["dias_cadastrados"]
        )

    with col3:

        st.metric(
            "🎯 Dias com meta",
            f'{status["dias_com_meta"]}/{status["dias_cadastrados"]}'
        )

    with col4:

        st.metric(
            "💰 Meta mensal",
            f'R$ {status["meta_mensal"]:,.2f}'
        )

    st.divider()

    # ==========================================
    # ESTADO DA TELA
    # ==========================================

    if "confirmar_abertura_mes" not in st.session_state:
        st.session_state.confirmar_abertura_mes = False


    # ==========================================
    # ABRIR NOVO MÊS
    # ==========================================

    with st.expander("📅 Abrir novo mês"):

        proximo_mes = obter_proximo_mes()

        st.write(
            "O sistema abrirá automaticamente o próximo mês disponível."
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "📅 Próximo mês",
                f'{proximo_mes["nome_mes"]}/{proximo_mes["ano"]}'
            )

        with col2:

            st.metric(
                "📆 Dias",
                proximo_mes["qtd_dias"]
            )

        with col3:

            st.metric(
                "👥 Equipe inicial",
                proximo_mes["equipe_inicial"]
            )

        st.divider()

        if not st.session_state.confirmar_abertura_mes:

            if st.button(
                f'📅 Abrir {proximo_mes["nome_mes"]}/{proximo_mes["ano"]}'
            ):

                st.session_state.confirmar_abertura_mes = True

                st.rerun()

        else:

            st.warning(
                "Você está prestes a criar o calendário do próximo mês."
            )

            st.markdown(
                f"""
    **Mês:** {proximo_mes["nome_mes"]}/{proximo_mes["ano"]}

    **Dias:** {proximo_mes["qtd_dias"]}

    **Equipe inicial:** {proximo_mes["equipe_inicial"]}

    Os campos de faturamento, meta, cupom e ticket médio permanecerão vazios.
    """
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button("Cancelar"):

                    st.session_state.confirmar_abertura_mes = False

                    st.rerun()

            with col2:

                if st.button("✅ Confirmar criação"):

                    try:

                        resultado = abrir_novo_mes()

                        st.session_state.confirmar_abertura_mes = False

                        st.success(
                            f'Calendário de {resultado["nome_mes"]}/{resultado["ano"]} criado com sucesso!'
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

    # ==========================================
    # IMPORTAR METAS
    # ==========================================

    with st.expander("📂 Importar metas"):

        st.info(
            "Funcionalidade em desenvolvimento."
        )

    # ==========================================
    # CONSULTAR / EDITAR
    # ==========================================

    with st.expander("✏️ Consultar / Editar metas"):

        st.info(
            "Funcionalidade em desenvolvimento."
        )