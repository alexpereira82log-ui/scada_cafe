import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

CAMINHO_BANCO = "faturamento_scada.db"

def salvar_registro():
    try:
        data = entry_data.get()
        faturamento = float(entry_faturamento.get())
        cupom = int(entry_cupom.get())
        comiss_dia = float(entry_comissao.get())
        colaboradores = int(entry_colaboradores.get())

        conn = sqlite3.connect(CAMINHO_BANCO)
        cursor = conn.cursor()

        # --- Atualiza tabela base_fat ---
        cursor.execute("""
            UPDATE base_fat
            SET faturamento = ?,
                cupom = ?
            WHERE data = ?
        """, (faturamento, cupom, data))

        if cursor.rowcount == 0:
            raise Exception("Data não encontrada na tabela base_fat.")

        # --- Atualiza tabela comissao ---
        cursor.execute("""
            UPDATE comissao
            SET comiss_dia = ?,
                colaboradores = ?
            WHERE data = ?
        """, (comiss_dia, colaboradores, data))

        if cursor.rowcount == 0:
            raise Exception("Data não encontrada na tabela comissao.")

        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Registros atualizados com sucesso!")
        limpar_campos()

    except ValueError:
        messagebox.showerror("Erro", "Verifique os campos numéricos.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

def limpar_campos():
    entry_data.delete(0, tk.END)
    entry_data.insert(0, datetime.today().strftime("%Y-%m-%d"))
    entry_faturamento.delete(0, tk.END)
    entry_cupom.delete(0, tk.END)
    entry_comissao.delete(0, tk.END)
    entry_colaboradores.delete(0, tk.END)

root = tk.Tk()
root.title("Atualização Faturamento e Comissão")
root.geometry("400x400")

# Data
tk.Label(root, text="Data (YYYY-MM-DD)").pack()
entry_data = tk.Entry(root)
entry_data.pack()
entry_data.insert(0, datetime.today().strftime("%Y-%m-%d"))

# Faturamento
tk.Label(root, text="Faturamento (R$)").pack()
entry_faturamento = tk.Entry(root)
entry_faturamento.pack()

# Cupom
tk.Label(root, text="Quantidade de Cupons").pack()
entry_cupom = tk.Entry(root)
entry_cupom.pack()

# Comissão do Dia
tk.Label(root, text="Comissão do Dia (R$)").pack()
entry_comissao = tk.Entry(root)
entry_comissao.pack()

# Colaboradores
tk.Label(root, text="Quantidade de Colaboradores").pack()
entry_colaboradores = tk.Entry(root)
entry_colaboradores.pack()

tk.Button(root, text="Salvar", command=salvar_registro).pack(pady=10)
tk.Button(root, text="Limpar", command=limpar_campos).pack()

root.mainloop()