import streamlit as st
from datetime import date

from services.metas import (
    obter_status_mes,
    obter_proximo_mes,
    abrir_novo_mes,
    ler_planilha_metas,
    preparar_planilha_metas,
    montar_dataframe_importacao,
    validar_importacao_metas
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

        st.write(
            "Selecione a planilha de metas enviada pela diretoria."
        )

        arquivo = st.file_uploader(
            "Planilha de metas",
            type=["xlsx"]
        )

        if arquivo:

            try:

                resultado = ler_planilha_metas(arquivo)

                df = preparar_planilha_metas(
                    resultado["dados"]
                )

                df = montar_dataframe_importacao(
                    df,
                    ano,
                    resultado["mes"]
                )

                status = validar_importacao_metas(df)

                st.divider()

                st.subheader("📋 Resumo da Importação")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "📅 Mês",
                        f'{resultado["nome_mes"]}/{hoje.year}'
                    )

                    st.metric(
                        "📆 Dias encontrados",
                        status["dias_planilha"]
                    )

                with col2:

                    st.metric(
                        "📅 Dias no banco",
                        status["dias_banco"]
                    )

                    st.metric(
                        "💰 Meta mensal",
                        f'R$ {status["meta_mensal"]:,.2f}'
                    )

                st.divider()

                if status["valido"]:

                    st.success(
                        "Planilha validada com sucesso. Pronta para importação."
                    )

                else:

                    st.error(
                        status["erro"]
                    )

            except Exception as e:

                st.error(str(e))

    # ==========================================
    # CONSULTAR / EDITAR
    # ==========================================

    with st.expander("✏️ Consultar / Editar metas"):

        st.info(
            "Funcionalidade em desenvolvimento."
        )