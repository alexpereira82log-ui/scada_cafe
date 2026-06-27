import streamlit as st
from datetime import date
from services.importador import executar_importacao


FOLDER_ID = "1-EZ342AsYKlkBpaT0Hcvo7f1GH0dW8G4"


def tela_importador():

    st.subheader("📥 Importador de Relatórios")

    data_relatorio = st.date_input(
        "Data do relatório",
        value=date.today(),
        format="DD/MM/YYYY"
    )


    if st.button("🚀 Importar Relatório"):

        data_str = data_relatorio.strftime("%Y-%m-%d")

        try:
            with st.spinner("Importando relatório..."):
                
                resultado = executar_importacao(
                    data_str,
                    FOLDER_ID
                )

            
            # Limpa o cache do Streamlit
            st.cache_data.clear()
            # Atualiza o cache para que o Dashboard reflita
            # imediatamente os dados recém-importados.

            st.success("Importação concluída com sucesso!")
            st.caption(f"Relatório importado: {data_str}")

            st.write("### Resultado")

            st.write(f"✔ Base Fat: {resultado['base_fat']} registro(s)")

            st.write(f"✔ Comissão: {resultado['comissao_dia']} registro(s)")

            st.write(f"✔ Produtos: {resultado['produtos']} registro(s)")

        except Exception as e:

            st.error(str(e))