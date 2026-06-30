from datetime import date

from services.metas import (
    consultar_meta,
    editar_meta
)

print("ANTES")
print(
    consultar_meta(
        date(2026, 6, 26)
    )
)

editar_meta(
    date(2026, 6, 26),
    2871.523875
)

print()
print("DEPOIS")
print(
    consultar_meta(
        date(2026, 6, 26)
    )
)