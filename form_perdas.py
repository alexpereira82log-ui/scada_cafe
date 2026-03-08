import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

CAMINHO_BANCO = "faturamento_scada.db"

def salvar_registro():
    try:
        conn = sqlite3.connect(CAMINHO_BANCO)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO perdas (
                data,
                item,
                categoria,
                qtd,
                motivo,
                responsavel,
                obs
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_data.get(),
            entry_item.get(),
            combo_categoria.get(),
            entry_qtd.get(),
            combo_motivo.get(),
            combo_responsavel.get(),
            entry_obs.get()
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Registro inserido com sucesso!")
        limpar_campos()

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

def limpar_campos():
    entry_data.delete(0, tk.END)
    entry_data.insert(0, datetime.today().strftime("%Y-%m-%d"))
    entry_item.delete(0, tk.END)
    combo_categoria.set('')
    entry_qtd.delete(0, tk.END)
    combo_motivo.set('')
    combo_responsavel.set('')
    entry_obs.delete(0, tk.END)

root = tk.Tk()
root.title("Registro de Perdas")
root.geometry("420x450")

# Data
tk.Label(root, text="Data (YYYY-MM-DD)").pack()
entry_data = tk.Entry(root)
entry_data.pack()
entry_data.insert(0, datetime.today().strftime("%Y-%m-%d"))

# Item
tk.Label(root, text="Item").pack()
entry_item = tk.Entry(root)
entry_item.pack()

# Categoria (Combobox)
tk.Label(root, text="Categoria").pack()
combo_categoria = ttk.Combobox(
    root,
    values=[
        "Produto final",
        "Utensilio",
        "Insumo",
        "Hortifruti",
        "Produto de limpeza",
        "Outro"
    ],
    state="readonly"
)
combo_categoria.pack()

# Quantidade
tk.Label(root, text="Quantidade").pack()
entry_qtd = tk.Entry(root)
entry_qtd.pack()

# Motivo (Combobox)
tk.Label(root, text="Motivo").pack()
combo_motivo = ttk.Combobox(
    root,
    values=[
        "Lançamento errado",
        "Erro de processo",
        "Saiu sem pagar",
        "Quebra",
        "Venceu (validade)",
        "Cliente",
        "Outro"
    ],
    state="readonly"
)
combo_motivo.pack()

# Responsável (Combobox)
tk.Label(root, text="Responsável").pack()
combo_responsavel = ttk.Combobox(
    root,
    values=[
        "Brunna",
        "Alex",
        "Jaqueline",
        "Fatima",
        "Fabio",
        "Jeisiana",
        "David",
        "Alexandro",
        "Jessyca",
        "Naiane"
    ],
    state="readonly"
)
combo_responsavel.pack()

# Observação
tk.Label(root, text="Observação").pack()
entry_obs = tk.Entry(root)
entry_obs.pack()

tk.Button(root, text="Salvar", command=salvar_registro).pack(pady=10)
tk.Button(root, text="Limpar", command=limpar_campos).pack()

root.mainloop()
