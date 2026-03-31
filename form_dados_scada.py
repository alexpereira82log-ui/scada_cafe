from database.connection import get_connection
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# ==========================================================
# BUSCAR COLABORADORES
# ==========================================================

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, nome FROM colaboradores ORDER BY nome")
colaboradores = cursor.fetchall()

conn.close()

# ==========================================================
# FUNÇÃO CALCULAR RATEIO
# ==========================================================

def calcular_rateio():
    try:
        comissao = float(entry_comissao.get())
        presentes = sum(var.get() for var in check_vars.values())

        if presentes == 0:
            label_rateio["text"] = "Rateio: 0"
            return

        rateio = (comissao * 0.8) / presentes
        label_rateio["text"] = f"Rateio por colaborador: {rateio:.2f}"

    except:
        label_rateio["text"] = "Rateio: -"

# ==========================================================
# CARREGAR DADOS
# ==========================================================

def carregar_dia():

    conn = get_connection()
    cursor = conn.cursor()

    data = entry_data.get()

    cursor.execute("""
    SELECT comiss_dia FROM comissao_dia
    WHERE data = %s
    """,(data,))

    resultado = cursor.fetchone()

    if not resultado:
        messagebox.showinfo("Aviso","Nenhum registro encontrado")
        conn.close()
        return

    entry_comissao.delete(0,tk.END)
    entry_comissao.insert(0,resultado[0])

    cursor.execute("""
    SELECT colaborador_id, presente
    FROM comissao_colaborador
    WHERE data = %s
    """,(data,))

    presencas = cursor.fetchall()

    for colab_id, presente in presencas:
        if colab_id in check_vars:
            check_vars[colab_id].set(presente)

    cursor.execute("""
    SELECT faturamento, cupom
    FROM base_fat
    WHERE data = %s
    """,(data,))

    fat = cursor.fetchone()

    if fat:
        entry_faturamento.delete(0,tk.END)
        entry_faturamento.insert(0,fat[0])

        entry_cupom.delete(0,tk.END)
        entry_cupom.insert(0,fat[1])

    conn.close()

    calcular_rateio()
    messagebox.showinfo("Carregado","Dados carregados")

# ==========================================================
# SALVAR
# ==========================================================

def salvar():

    conn = get_connection()
    cursor = conn.cursor()

    data = entry_data.get()
    comissao = entry_comissao.get()
    faturamento = entry_faturamento.get()
    cupom = entry_cupom.get()

    if not all([data, comissao, faturamento, cupom]):
        messagebox.showwarning("Atenção","Preencha todos os campos")
        return

    try:
        datetime.strptime(data,"%Y-%m-%d")
    except:
        messagebox.showerror("Erro","Data inválida")
        return

    comissao = float(comissao)
    faturamento = float(faturamento)
    cupom = int(cupom)

    try:

        cursor.execute(
            "SELECT data FROM comissao_dia WHERE data = %s",
            (data,)
        )

        existe = cursor.fetchone()

        if existe:

            atualizar = messagebox.askyesno(
                "Registro existente",
                "Deseja atualizar?"
            )

            if not atualizar:
                conn.close()
                return

            cursor.execute("""
            UPDATE comissao_dia
            SET comiss_dia = %s
            WHERE data = %s
            """,(comissao,data))

            cursor.execute("""
            DELETE FROM comissao_colaborador
            WHERE data = %s
            """,(data,))

        else:

            cursor.execute("""
            INSERT INTO comissao_dia (data,comiss_dia)
            VALUES (%s,%s)
            """,(data,comissao))

        for colab_id,var in check_vars.items():

            cursor.execute("""
            INSERT INTO comissao_colaborador
            (data,colaborador_id,presente)
            VALUES (%s,%s,%s)
            """,(data,colab_id,bool(var.get())))

        cursor.execute("""
        UPDATE base_fat
        SET faturamento = %s, cupom = %s
        WHERE data = %s
        """,(faturamento,cupom,data))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso","Dados salvos")

    except Exception as e:
        conn.rollback()
        conn.close()
        messagebox.showerror("Erro",str(e))

# ==========================================================
# INTERFACE
# ==========================================================

janela = tk.Tk()
janela.title("Lançamento Diário")
janela.geometry("420x650")

tk.Label(janela,text="Data").pack()
entry_data = tk.Entry(janela)
entry_data.pack()
entry_data.insert(0,datetime.today().strftime("%Y-%m-%d"))

tk.Label(janela,text="Faturamento").pack()
entry_faturamento = tk.Entry(janela)
entry_faturamento.pack()

tk.Label(janela,text="Cupons").pack()
entry_cupom = tk.Entry(janela)
entry_cupom.pack()

tk.Label(janela,text="Comissão").pack()
entry_comissao = tk.Entry(janela)
entry_comissao.pack()
entry_comissao.bind("<KeyRelease>",lambda e: calcular_rateio())

frame_colab = tk.Frame(janela)
frame_colab.pack()

check_vars = {}

for colab_id,nome in colaboradores:
    var = tk.IntVar(value=1)
    chk = tk.Checkbutton(frame_colab,text=nome,variable=var,command=calcular_rateio)
    chk.pack(anchor="w")
    check_vars[colab_id] = var

label_rateio = tk.Label(janela,text="Rateio: -")
label_rateio.pack()

tk.Button(janela,text="Salvar",command=salvar).pack(pady=10)
tk.Button(janela,text="Carregar",command=carregar_dia).pack()

janela.mainloop()