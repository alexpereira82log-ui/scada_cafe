import streamlit as st
import pandas as pd

from datetime import date

from services.perdas import (
    inserir_perda,
    carregar_colaboradores,
    consultar_perdas,
    editar_perda
)


def tela_perdas():

    st.subheader("⚠️ Gestão de Perdas")

    st.caption(
        "Registre, consulte e administre as perdas operacionais."
    )

    st.divider()


    # ==========================================
    # ESTADO DA TELA
    # ==========================================

    if "registro_perda" not in st.session_state:
        st.session_state.registro_perda = None

    if "confirmar_exclusao_perda" not in st.session_state:
        st.session_state.confirmar_exclusao_perda = None

    if "mensagem_perda" not in st.session_state:
        st.session_state.mensagem_perda = None

    if "registros_perdas" not in st.session_state:
        st.session_state.registros_perdas = [] 

    colaboradores = carregar_colaboradores()

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
            colaboradores
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

    st.divider()

    # ==========================================
    # CONSULTAR / EDITAR PERDAS
    # ==========================================

    with st.expander("✏️ Consultar / Editar Perdas"):

        data_consulta = st.date_input(
            "Data da perda",
            value=date.today(),
            format="DD/MM/YYYY",
            key="consulta_perdas"
        )

        if st.button("🔍 Pesquisar"):

            try:

                st.session_state.registros_perdas = consultar_perdas(
                    data_consulta
                )

            except Exception as e:

                st.error(str(e))

        # ==========================================
        # RESULTADO DA PESQUISA
        # ==========================================

        if st.session_state.registros_perdas:

            st.success(
                f"{len(st.session_state.registros_perdas)} registro(s) encontrado(s)."
            )

            for registro in st.session_state.registros_perdas:

                st.markdown(f"### 📦 {registro['item']}")

                col1, col2 = st.columns(2)

                with col1:

                    st.write(f"**Categoria:** {registro['categoria']}")
                    st.write(f"**Quantidade:** {registro['qtd']}")

                with col2:

                    st.write(f"**Motivo:** {registro['motivo']}")
                    st.write(f"**Responsável:** {registro['responsavel']}")

                if registro["obs"]:

                    st.markdown("**📝 Observação**")

                    st.write(
                        registro["obs"]
                    )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✏️ Editar",
                        key=f"editar_{registro['id']}"
                    ):

                        st.session_state.registro_perda = registro

                        st.rerun()

                with col2:

                    if st.button(
                        "🗑️ Excluir",
                        key=f"excluir_{registro['id']}"
                    ):

                        st.session_state.confirmar_exclusao_perda = registro

                        st.rerun()

                st.divider()

        elif st.session_state.registros_perdas == []:

            st.info(
                "Nenhuma perda encontrada para esta data."
            )

        # ==========================================
        # FORMULÁRIO DE EDIÇÃO
        # ==========================================

        if st.session_state.registro_perda:

            registro = st.session_state.registro_perda

            st.divider()

            st.subheader("✏️ Editar Perda")

            data = st.date_input(
                "Data",
                value=registro["data"],
                format="DD/MM/YYYY",
                key="editar_data"
            )

            item = st.text_input(
                "Item",
                value=registro["item"],
                key="editar_item"
            )

            categorias = [
                "Produto final",
                "Utensilio",
                "Insumo",
                "Hortifruti",
                "Produto de limpeza",
                "Outro"
            ]

            categoria = st.selectbox(
                "Categoria",
                categorias,
                index=categorias.index(registro["categoria"]),
                key="editar_categoria"
            )

            qtd = st.text_input(
                "Quantidade",
                value=registro["qtd"],
                key="editar_qtd"
            )

            motivos = [
                "Lançamento errado",
                "Erro de processo",
                "Saiu sem pagar",
                "Quebra",
                "Venceu (validade)",
                "Cliente",
                "Outro"
            ]

            motivo = st.selectbox(
                "Motivo",
                motivos,
                index=motivos.index(registro["motivo"]),
                key="editar_motivo"
            )

            if registro["responsavel"] in colaboradores:

                indice = colaboradores.index(
                    registro["responsavel"]
                )

            else:

                indice = 0

            responsavel = st.selectbox(
                "Responsável",
                colaboradores,
                index=indice,
                key="editar_responsavel"
            )

            obs = st.text_area(
                "Observação",
                value=registro["obs"],
                key="editar_obs"
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "💾 Salvar Alterações"
                ):

                    try:

                        editar_perda(
                            id=registro["id"],
                            data=data,
                            item=item,
                            categoria=categoria,
                            qtd=qtd,
                            motivo=motivo,
                            responsavel=responsavel,
                            obs=obs
                        )

                        st.session_state.registro_perda = None

                        st.session_state.registros_perdas = consultar_perdas(
                            data_consulta
                        )

                        st.session_state.mensagem_perda = (
                            "Registro atualizado com sucesso!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))

            with col2:

                if st.button("Cancelar"):

                    st.session_state.registro_perda = None

                    st.rerun()