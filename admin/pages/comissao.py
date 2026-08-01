import streamlit as st
import pandas as pd
import calendar

from datetime import date

from services.comissao_service import (
    obter_comissao_dia,
    listar_rateio_dia,
    recalcular_rateio,
    salvar_rateio,
    listar_colaboradores_ativos,
    obter_resumo_mensal_comissao,

)

from services.afastamento_service import (
    aplicar_afastamento,
    excluir_afastamento,
    atualizar_afastamento,
    obter_calendario_mensal,
    listar_afastamentos,

)

from services.relatorio_comissao_service import (
    obter_relatorio_mensal_comissao,
)

from services.exportacao_excel import (
    exportar_dataframe_excel,
)



def tela_comissao():
    """
    Tela administrativa para gestão da comissão dos colaboradores.
    """

    st.subheader("💰 Gestão de Comissão")



    if st.session_state.pop("comissao_salva", False):
        st.success(
            "Comissão atualizada com sucesso!"
        )

    if st.session_state.pop("afastamento_salvo", False):
        st.success(
            "Afastamento registrado com sucesso!"
        )


    # ==========================================================
    # Seletor de mês
    # ==========================================================

    hoje = date.today()

    st.markdown("### 📅 Competência")

    col1, col2 = st.columns(2)

    with col1:

        ano = st.selectbox(
            "Ano",
            options=[2025, 2026, 2027],
            index=1,
        )

    with col2:

        meses = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }

        mes_nome = st.selectbox(
            "Mês",
            options=list(meses.values()),
            index=hoje.month - 1,
        )

    mes = next(
        numero
        for numero, nome in meses.items()
        if nome == mes_nome
    )

    # ==========================================================
    # Resumo Mensal
    # ==========================================================

    st.markdown("## 📈 Resumo Mensal")

    resumo = obter_resumo_mensal_comissao(
        ano,
        mes,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "💰 Taxa Serviço",
            f"R$ {resumo['taxa_servico']:,.2f}"
        )

    with col2:
        st.metric(
            "💵 Comissão (80%)",
            f"R$ {resumo['comissao_total']:,.2f}"
        )

    with col3:
        st.metric(
            "📅 Média Diária",
            f"R$ {resumo['media_diaria']:,.2f}"
        )

    with col4:
        st.metric(
            "👤 Média Individual",
            f"R$ {resumo['media_individual']:,.2f}"
        )

    with col5:
        st.metric(
            "📈 Projeção Individual",
            f"R$ {resumo['projecao_final']:,.2f}"
        )

    # ==========================================================
    # Comissão Diária
    # ==========================================================

    with st.expander(
        "📅 Comissão Diária",
        expanded=True,
    ):

        data_padrao = date(
            ano,
            mes,
            1,
        )

        data = st.date_input(
            "📅 Data da operação",
            value=data_padrao,
        )

        comissao = obter_comissao_dia(data)

        if comissao is None:

            st.warning(
                "Ainda não existe comissão registrada para esta data."
            )

        else:

            valor_taxa = float(
                comissao["valor_taxa_servico"] or 0
            )

            valor_rateio = valor_taxa * 0.80

            participantes = listar_rateio_dia(data)

            dados = []

            for colaborador in participantes:

                dados.append({
                    "ID": colaborador["id"],
                    "Participa": colaborador["presente"],
                    "Colaborador": colaborador["nome"],
                    "Comissão": round(
                        colaborador["valor"],
                        2
                    ),
                })

            df = pd.DataFrame(dados)

            st.markdown("### 👥 Participação do Dia")

            df_editado = st.data_editor(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "ID": None,

                    "Participa": st.column_config.CheckboxColumn(
                        "Elegível"
                    ),

                    "Colaborador": st.column_config.TextColumn(
                        "Colaborador"
                    ),

                    "Comissão": st.column_config.NumberColumn(
                        "Comissão",
                        format="R$ %.2f",
                    ),
                },
                disabled=[
                    "Colaborador",
                    "Comissão",
                ],
            )

            participantes_interface = df_editado.to_dict("records")

            participantes = [
                {
                    "id": participante["ID"],
                    "nome": participante["Colaborador"],
                    "presente": participante["Participa"],
                    "valor": participante["Comissão"],
                }
                for participante in participantes_interface
            ]

            participantes, elegiveis, valor_individual = recalcular_rateio(
                participantes,
                valor_rateio,
            )

            st.markdown("### 📊 Resultado do Rateio")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "💰 Taxa de Serviço",
                    f"R$ {valor_taxa:,.2f}"
                )

            with col2:
                st.metric(
                    "💵 Valor para Rateio (80%)",
                    f"R$ {valor_rateio:,.2f}"
                )

            with col3:
                st.metric(
                    "👥 Elegíveis",
                    elegiveis
                )

            with col4:
                st.metric(
                    "🪙 Comissão Individual",
                    f"R$ {valor_individual:,.2f}"
                )

            st.divider()

            col1, col2 = st.columns([1, 5])

            with col1:

                salvar = st.button(
                    "💾 Salvar",
                    use_container_width=True,
                )

            if salvar:

                salvar_rateio(
                    data,
                    participantes,
                )

                st.session_state["comissao_salva"] = True

                st.rerun()

    # ==========================================================
    # Novo Afastamento
    # ==========================================================

    with st.expander(
        "➕ Novo Afastamento",
        expanded=False,
    ):

        colaboradores = listar_colaboradores_ativos()

        col1, col2 = st.columns(2)

        with col1:

            colaborador = st.selectbox(
                "👤 Colaborador",
                options=colaboradores,
                format_func=lambda c: c["nome"],
            )

            motivo = st.selectbox(
                "📌 Motivo",
                options=[
                    "Férias",
                    "Atestado",
                    "Folga",
                    "Licença",
                    "Outro",
                ],
            )

        with col2:

            data_inicio = st.date_input(
                "📅 Data inicial"
            )

            data_fim = st.date_input(
                "📅 Data final"
            )

        btn_aplicar_afastamento = st.button(
            "🗓️ Aplicar Afastamento",
            use_container_width=True,
        )

        if btn_aplicar_afastamento:

            afastamento = {
                "colaborador_id": colaborador["id"],
                "colaborador_nome": colaborador["nome"],
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "motivo": motivo,
                "observacao": "",
            }

            aplicar_afastamento(afastamento)

            st.session_state["afastamento_salvo"] = True

            st.rerun()


    # ==========================================================
    # Afastamentos cadastrados
    # ==========================================================

    with st.expander(
        "📋 Afastamentos Cadastrados",
        expanded=True,
    ):

        afastamentos = listar_afastamentos()

        if not afastamentos:

            st.info(
                "Nenhum afastamento cadastrado."
            )

        else:

            df_afastamentos = pd.DataFrame(
                afastamentos
            )


            # ==========================================================
            # Ajustes de apresentação
            # ==========================================================

            df_afastamentos = df_afastamentos.drop(
                columns=[
                    "id",
                    "colaborador_id",
                ]
            )

            df_afastamentos.rename(
                columns={
                    "colaborador": "Colaborador",
                    "data_inicio": "Data Inicial",
                    "data_fim": "Data Final",
                    "motivo": "Motivo",
                    "observacao": "Observação",
                },
                inplace=True,
            )

            df_afastamentos["Data Inicial"] = (
                pd.to_datetime(
                    df_afastamentos["Data Inicial"]
                )
                .dt.strftime("%d/%m/%Y")
            )

            df_afastamentos["Data Final"] = (
                pd.to_datetime(
                    df_afastamentos["Data Final"]
                )
                .dt.strftime("%d/%m/%Y")
            )


            st.dataframe(
                df_afastamentos,
                use_container_width=True,
                hide_index=True,
            )
        
            # ==========================================================
            # Seleção do afastamento
            # ==========================================================

            afastamento_selecionado = st.selectbox(
                "Selecione um afastamento",
                options=afastamentos,
                format_func=lambda a:
                    f'{a["colaborador"]} | '
                    f'{a["data_inicio"].strftime("%d/%m/%Y")} → '
                    f'{a["data_fim"].strftime("%d/%m/%Y")} | '
                    f'{a["motivo"]}',
            )


            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                colaborador_edicao = st.selectbox(
                    "👤 Colaborador",
                    options=colaboradores,
                    index=next(
                        i
                        for i, c in enumerate(colaboradores)
                        if c["id"] == afastamento_selecionado["colaborador_id"]
                    ),
                    format_func=lambda c: c["nome"],
                    key="editar_colaborador",
                )

                motivo_edicao = st.selectbox(
                    "📌 Motivo",
                    options=[
                        "Férias",
                        "Atestado",
                        "Folga",
                        "Licença",
                        "Outro",
                    ],
                    index=[
                        "Férias",
                        "Atestado",
                        "Folga",
                        "Licença",
                        "Outro",
                    ].index(afastamento_selecionado["motivo"]),
                    key="editar_motivo",
                )

            with col2:

                data_inicio_edicao = st.date_input(
                    "📅 Data Inicial",
                    value=afastamento_selecionado["data_inicio"],
                    key="editar_data_inicio",
                )

                data_fim_edicao = st.date_input(
                    "📅 Data Final",
                    value=afastamento_selecionado["data_fim"],
                    key="editar_data_fim",
                )

            observacao_edicao = st.text_area(
                "📝 Observação",
                value=afastamento_selecionado["observacao"] or "",
                key="editar_observacao",
            )


            salvar_alteracoes = st.button(
                "💾 Salvar Alterações",
                use_container_width=True,
            )

            if salvar_alteracoes:

                afastamento = {
                    "id": afastamento_selecionado["id"],
                    "colaborador_id": colaborador_edicao["id"],
                    "data_inicio": data_inicio_edicao,
                    "data_fim": data_fim_edicao,
                    "motivo": motivo_edicao,
                    "observacao": observacao_edicao,
                }

                atualizar_afastamento(
                    afastamento
                )

                st.success(
                    "Afastamento atualizado com sucesso."
                )

                st.rerun()


            if st.button(
                "🗑️ Excluir Afastamento",
                use_container_width=True,
            ):

                st.session_state["confirmar_exclusao_afastamento"] = True

            if st.session_state.get(
                "confirmar_exclusao_afastamento",
                False,
            ):

                st.warning(
                    "⚠️ Esta operação removerá definitivamente este afastamento."
                )

                col1, col2 = st.columns(2)

                with col1:

                    btn_confirmar_exclusao = st.button(
                        "✅ Confirmar Exclusão",
                        use_container_width=True,
                    )

                with col2:

                    btn_cancelar_exclusao = st.button(
                        "❌ Cancelar",
                        use_container_width=True,
                    )

                
                if btn_cancelar_exclusao:

                    st.session_state[
                        "confirmar_exclusao_afastamento"
                    ] = False

                    st.rerun()

                if btn_confirmar_exclusao:

                    excluir_afastamento(
                        afastamento_selecionado["id"]
                    )

                    st.session_state[
                        "confirmar_exclusao_afastamento"
                    ] = False

                    st.success(
                        "Afastamento excluído com sucesso."
                    )

                    st.rerun()


    # ==========================================================
    # Calendário Mensal
    # ==========================================================

    with st.expander(
        "📅 Calendário Mensal",
        expanded=False,
    ):

        calendario = obter_calendario_mensal(
            ano,
            mes,
        )

        df_calendario = pd.DataFrame(
            calendario
        )

        styler = df_calendario.style

        st.dataframe(
            styler,
            use_container_width=True,
            hide_index=True,
        )

    # ==========================================================
    # Relatório Gerencial
    # ==========================================================

    with st.expander(
        "📊 Relatório Gerencial de Comissão",
        expanded=False,
    ):

        relatorio = obter_relatorio_mensal_comissao(
            ano,
            mes,
        )

        if not relatorio:

            st.info(
                "Ainda não existem comissões registradas para a competência selecionada."
            )

        else:

            df_relatorio = pd.DataFrame(
                relatorio
            )

            # ==========================================================
            # Formatação monetária
            # ==========================================================

            colunas_valores = df_relatorio.columns[1:]

            df_relatorio[colunas_valores] = (
                df_relatorio[colunas_valores]
                .round(2)
            )

            st.dataframe(
                df_relatorio,
                use_container_width=True,
                hide_index=True,
            )

            if st.button(
                "📄 Exportar para Excel",
                use_container_width=True,
            ):

                caminho = "exports/relatorio_comissao.xlsx"

                exportar_dataframe_excel(
                    df_relatorio,
                    caminho,
                )

                st.success(
                    f"Relatório exportado com sucesso!\n\nArquivo: {caminho}"
                )

