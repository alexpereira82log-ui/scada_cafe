from services.faturamento import (
    consultar_faturamento,
    editar_faturamento
)

editar_faturamento(
    "2026-06-26",
    2805,
    2871.52,
    58,
    48.36
)

print(consultar_faturamento("2026-06-26"))