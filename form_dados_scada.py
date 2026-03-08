import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# ==========================================================
# CONEXÃO COM BANCO
# ==========================================================

conn = sqlite3.connect("faturamento_scada.db")
cursor = conn.cursor()

# ==========================================================
# BUSCAR COLABORADORES
# ==========================================================

cursor.execute("SELECT id, nome FROM colaboradores ORDER BY nome")
colaboradores = cursor.fetchall()

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
# CARREGAR DADOS PARA EDIÇÃO
# ==========================================================

def carregar_dia():

    data = entry_data.get()

    cursor.execute("""
    SELECT comiss_dia FROM comissao_dia
    WHERE data = ?
    """,(data,))

    resultado = cursor.fetchone()

    if not resultado:
        messagebox.showinfo("Aviso","Nenhum registro encontrado para essa data")
        return

    entry_comissao.delete(0,tk.END)
    entry_comissao.insert(0,resultado[0])

    cursor.execute("""
    SELECT colaborador_id, presente
    FROM comissao_colaborador
    WHERE data = ?
    """,(data,))

    presencas = cursor.fetchall()

    for colab_id, presente in presencas:

        if colab_id in check_vars:
            check_vars[colab_id].set(presente)

    cursor.execute("""
    SELECT faturamento, cupom
    FROM base_fat
    WHERE data = ?
    """,(data,))

    fat = cursor.fetchone()

    if fat:

        entry_faturamento.delete(0,tk.END)
        entry_faturamento.insert(0,fat[0])

        entry_cupom.delete(0,tk.END)
        entry_cupom.insert(0,fat[1])

    calcular_rateio()

    messagebox.showinfo("Carregado","Dados carregados para edição")


# ==========================================================
# SALVAR INFORMAÇÕES
# ==========================================================

def salvar():

    data = entry_data.get()
    comissao = entry_comissao.get()
    faturamento = entry_faturamento.get()
    cupom = entry_cupom.get()

    if data == "" or comissao == "" or faturamento == "" or cupom == "":
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

        cursor.execute("SELECT data FROM comissao_dia WHERE data = ?",(data,))
        existe = cursor.fetchone()

        if existe:

            atualizar = messagebox.askyesno(
                "Registro existente",
                "Já existe registro para essa data.\nDeseja atualizar?"
            )

            if not atualizar:
                return

            cursor.execute("""
            UPDATE comissao_dia
            SET comiss_dia = ?
            WHERE data = ?
            """,(comissao,data))

            cursor.execute("""
            DELETE FROM comissao_colaborador
            WHERE data = ?
            """,(data,))

        else:

            cursor.execute("""
            INSERT INTO comissao_dia (data,comiss_dia)
            VALUES (?,?)
            """,(data,comissao))

        for colab_id,var in check_vars.items():

            presente = var.get()

            cursor.execute("""
            INSERT INTO comissao_colaborador
            (data,colaborador_id,presente)
            VALUES (?,?,?)
            """,(data,colab_id,presente))

        cursor.execute("""
        UPDATE base_fat
        SET faturamento = ?, cupom = ?
        WHERE data = ?
        """,(faturamento,cupom,data))

        conn.commit()

        messagebox.showinfo("Sucesso","Informações registradas")

    except Exception as e:

        conn.rollback()
        messagebox.showerror("Erro",str(e))


# ==========================================================
# INTERFACE
# ==========================================================

janela = tk.Tk()
janela.title("Lançamento Diário")
janela.geometry("420x650")

# ==========================================================
# DATA (HOJE AUTOMÁTICO)
# ==========================================================

label_data = tk.Label(janela,text="Data")
label_data.pack()

entry_data = tk.Entry(janela)
entry_data.pack()

entry_data.insert(0,datetime.today().strftime("%Y-%m-%d"))

# ==========================================================
# FATURAMENTO
# ==========================================================

label_faturamento = tk.Label(janela,text="Faturamento do Dia")
label_faturamento.pack()

entry_faturamento = tk.Entry(janela)
entry_faturamento.pack()

# ==========================================================
# CUPOM
# ==========================================================

label_cupom = tk.Label(janela,text="Quantidade de Cupons")
label_cupom.pack()

entry_cupom = tk.Entry(janela)
entry_cupom.pack()

# ==========================================================
# COMISSÃO
# ==========================================================

label_comissao = tk.Label(janela,text="Comissão do Dia")
label_comissao.pack()

entry_comissao = tk.Entry(janela)
entry_comissao.pack()

entry_comissao.bind("<KeyRelease>",lambda e: calcular_rateio())

# ==========================================================
# COLABORADORES
# ==========================================================

label_colab = tk.Label(janela,text="Colaboradores Presentes")
label_colab.pack(pady=10)

frame_colab = tk.Frame(janela)
frame_colab.pack()

check_vars = {}

for colab_id,nome in colaboradores:

    var = tk.IntVar(value=1)

    chk = tk.Checkbutton(
        frame_colab,
        text=nome,
        variable=var,
        command=calcular_rateio
    )

    chk.pack(anchor="w")

    check_vars[colab_id] = var

# ==========================================================
# RATEIO
# ==========================================================

label_rateio = tk.Label(
    janela,
    text="Rateio: -",
    font=("Arial",12,"bold")
)

label_rateio.pack(pady=10)

# ==========================================================
# BOTÕES
# ==========================================================

botao_salvar = tk.Button(
    janela,
    text="Salvar",
    command=salvar,
    bg="green",
    fg="white",
    width=20
)

botao_salvar.pack(pady=10)

botao_carregar = tk.Button(
    janela,
    text="Carregar dia para edição",
    command=carregar_dia,
    width=20
)

botao_carregar.pack()

janela.mainloop()
                