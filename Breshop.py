#Sistema de gerenciamento para Brechó e Bazares
#aluno: Eric Henrique Bergamo   
#RU 5283584

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk


DADOSUSR = "database.json"
PRODUTOS = ["Camisa", "Calça", "Tênis", "Chapéu", "Outros"]


class LojaApp:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("OperaT PDV - Loja")
        self.janela.geometry("720x980")
        self.dados = self.carregar_dados()
        self.carrinho = []
        self.telas = {}
        self.montar_interface()
        self.mostrar_tela("inicio")

    @staticmethod
    def carregar_dados():
        if os.path.exists(DADOSUSR):
            with open(DADOSUSR, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        else:
            dados = {"estoque": {}, "vendas": []}

        estoque = dados.setdefault("estoque", {})
        dados.setdefault("vendas", [])
        for produto in PRODUTOS:
            estoque.setdefault(produto, 0)
        return dados

    def salvar_dados(self):
        with open(DADOSUSR, "w", encoding="utf-8") as arquivo:
            json.dump(self.dados, arquivo, indent=2, ensure_ascii=False)

    @staticmethod
    def ler_valor(texto):
        return float(texto.replace(",", "."))

    @staticmethod
    def moeda(valor):
        return f"R$ {valor:.2f}".replace(".", ",")

    def montar_interface(self):
        container = tk.Frame(self.janela)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        for nome in ("inicio", "venda", "estoque", "relatorios"):
            tela = tk.Frame(container)
            tela.grid(row=0, column=0, sticky="nsew")
            self.telas[nome] = tela

        self.montar_inicio()
        self.montar_vendas()
        self.montar_estoque()
        self.montar_relatorios()

    def mostrar_tela(self, nome):
        if nome == "venda":
            self.atualizar_tabela_venda()
        elif nome == "estoque":
            self.atualizar_tabela_estoque()
        elif nome == "relatorios":
            self.atualizar_tabela_relatorios()
        self.telas[nome].tkraise()

    def montar_inicio(self):
        tela = self.telas["inicio"]
        tk.Label(tela, text="OperaT", font=("Impact", 28)).pack(pady=(60, 10))
        tk.Label(tela, text="Seu sistema de vendas e estoque", font=("Segoe UI", 10, "italic")).pack(pady=(0, 30))
        tk.Label(tela, text="O que você quer fazer?", font=("Segoe UI", 12)).pack(pady=(0, 30))

        estilo = {"font": ("Segoe UI", 14), "width": 20, "height": 2}
        botoes = (
            ("Venda", "#2e7d32", "venda"),
            ("Estoque", "#1565c0", "estoque"),
            ("Relatórios", "#6a1b9a", "relatorios"),
        )
        linha_botoes = tk.Frame(tela)
        linha_botoes.pack()
        for texto, cor, destino in botoes[:2]:
            tk.Button(
                linha_botoes, text=texto, bg=cor, fg="white",
                command=lambda destino=destino: self.mostrar_tela(destino),
                **estilo,
            ).pack(side="left", padx=6, pady=6)

        texto, cor, destino = botoes[2]
        tk.Button(
            tela, text=texto, bg=cor, fg="white",
            command=lambda destino=destino: self.mostrar_tela(destino),
            **estilo,
        ).pack(pady=6)

    def montar_vendas(self):
        tela = self.telas["venda"]
        tk.Label(tela, text="Venda", font=("Segoe UI", 18, "bold")).pack(pady=10)
        formulario = tk.Frame(tela)
        formulario.pack(pady=5)

        tk.Label(formulario, text="Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.produto_venda = ttk.Combobox(formulario, values=PRODUTOS, state="readonly", width=18)
        self.produto_venda.current(0)
        self.produto_venda.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(formulario, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.quantidade_venda = tk.Entry(formulario, width=21)
        self.quantidade_venda.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(formulario, text="Valor unitário (R$):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.valor_venda = tk.Entry(formulario, width=21)
        self.valor_venda.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(formulario, text="Adicionar ao carrinho", command=self.adicionar_ao_carrinho).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        self.tabela_venda = ttk.Treeview(
            tela, columns=("produto", "quantidade", "valor", "subtotal"), show="headings", height=7
        )
        for coluna, titulo in zip(
            ("produto", "quantidade", "valor", "subtotal"),
            ("Produto", "Qtd", "Valor unit.", "Subtotal"),
        ):
            self.tabela_venda.heading(coluna, text=titulo)
            self.tabela_venda.column(coluna, width=120, anchor="center")
        self.tabela_venda.pack(padx=20, pady=5, fill="x")

        self.total_venda = tk.Label(tela, text="Total: R$ 0,00", font=("Arial", 14, "bold"))
        self.total_venda.pack(pady=5)
        botoes = tk.Frame(tela)
        botoes.pack(pady=5)
        tk.Button(botoes, text="Finalizar venda", bg="#2e7d32", fg="white", command=self.finalizar_venda).pack(side="left", padx=5)
        tk.Button(botoes, text="Voltar", command=lambda: self.mostrar_tela("inicio")).pack(side="left", padx=5)

    def adicionar_ao_carrinho(self):
        produto = self.produto_venda.get()
        try:
            quantidade = int(self.quantidade_venda.get())
            valor = self.ler_valor(self.valor_venda.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite números válidos em quantidade e valor.")
            return

        if quantidade <= 0 or valor < 0:
            messagebox.showerror("Erro", "Quantidade e valor não podem ser negativos.")
            return

        reservado = sum(item["qtd"] for item in self.carrinho if item["item"] == produto)
        disponivel = self.dados["estoque"].get(produto, 0)
        if quantidade + reservado > disponivel:
            messagebox.showwarning(
                "Estoque insuficiente",
                f"Só existem {disponivel} unidade(s) de {produto} no estoque.",
            )
            return

        self.carrinho.append({"item": produto, "qtd": quantidade, "valor": valor})
        self.quantidade_venda.delete(0, tk.END)
        self.valor_venda.delete(0, tk.END)
        self.atualizar_tabela_venda()

    def atualizar_tabela_venda(self):
        self.tabela_venda.delete(*self.tabela_venda.get_children())
        total = 0
        for item in self.carrinho:
            subtotal = item["qtd"] * item["valor"]
            total += subtotal
            self.tabela_venda.insert(
                "", "end",
                values=(item["item"], item["qtd"], self.moeda(item["valor"]), self.moeda(subtotal)),
            )
        self.total_venda.config(text=f"Total: {self.moeda(total)}")

    def finalizar_venda(self):
        if not self.carrinho:
            messagebox.showinfo("Carrinho vazio", "Adicione pelo menos um item.")
            return

        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        for item in self.carrinho:
            self.dados["estoque"][item["item"]] -= item["qtd"]
            self.dados["vendas"].append({"data": data, **item})
        self.salvar_dados()

        total = sum(item["qtd"] * item["valor"] for item in self.carrinho)
        messagebox.showinfo("Venda finalizada", f"Venda registrada!\nTotal: {self.moeda(total)}")
        self.carrinho.clear()
        self.atualizar_tabela_venda()

    def montar_estoque(self):
        tela = self.telas["estoque"]
        tk.Label(tela, text="Estoque", font=("Segoe UI", 18, "bold")).pack(pady=10)
        formulario = tk.Frame(tela)
        formulario.pack(pady=5)
        tk.Label(formulario, text="Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.produto_estoque = ttk.Combobox(formulario, values=PRODUTOS, state="readonly", width=18)
        self.produto_estoque.current(0)
        self.produto_estoque.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(formulario, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.quantidade_estoque = tk.Entry(formulario, width=21)
        self.quantidade_estoque.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(formulario, text="Adicionar ao estoque", bg="#54c015", fg="white", command=self.adicionar_ao_estoque).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        self.tabela_estoque = ttk.Treeview(tela, columns=("produto", "quantidade"), show="headings", height=8)
        self.tabela_estoque.heading("produto", text="Produto")
        self.tabela_estoque.heading("quantidade", text="Quantidade em estoque")
        self.tabela_estoque.column("produto", width=200, anchor="center")
        self.tabela_estoque.column("quantidade", width=200, anchor="center")
        self.tabela_estoque.pack(padx=20, pady=10, fill="x")
        tk.Button(tela, text="Voltar", command=lambda: self.mostrar_tela("inicio")).pack(pady=5)

    def adicionar_ao_estoque(self):
        try:
            quantidade = int(self.quantidade_estoque.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um número inteiro na quantidade.")
            return
        if quantidade <= 0:
            messagebox.showerror("Erro", "A quantidade precisa ser maior que zero.")
            return

        produto = self.produto_estoque.get()
        self.dados["estoque"][produto] += quantidade
        self.salvar_dados()
        self.quantidade_estoque.delete(0, tk.END)
        self.atualizar_tabela_estoque()
        messagebox.showinfo("Pronto", f"{quantidade} unidade(s) de {produto} adicionada(s).")

    def atualizar_tabela_estoque(self):
        self.tabela_estoque.delete(*self.tabela_estoque.get_children())
        for produto, quantidade in self.dados["estoque"].items():
            self.tabela_estoque.insert("", "end", values=(produto, quantidade))

    def montar_relatorios(self):
        tela = self.telas["relatorios"]
        tk.Label(tela, text="Relatórios", font=("Segoe UI", 18, "bold")).pack(pady=10)
        self.tabela_relatorios = ttk.Treeview(
            tela, columns=("data", "produto", "quantidade", "subtotal"), show="headings", height=12
        )
        for coluna, titulo, largura in (
            ("data", "Data", 150), ("produto", "Produto", 130),
            ("quantidade", "Qtd", 70), ("subtotal", "Subtotal", 120),
        ):
            self.tabela_relatorios.heading(coluna, text=titulo)
            self.tabela_relatorios.column(coluna, width=largura, anchor="center")
        self.tabela_relatorios.pack(padx=20, pady=10, fill="x")
        self.total_relatorios = tk.Label(tela, text="", font=("Segoe UI", 13, "bold"))
        self.total_relatorios.pack(pady=5)
        tk.Button(tela, text="Voltar", command=lambda: self.mostrar_tela("inicio")).pack(pady=5)

    def atualizar_tabela_relatorios(self):
        self.tabela_relatorios.delete(*self.tabela_relatorios.get_children())
        faturamento = 0
        quantidade_total = 0
        for venda in self.dados["vendas"]:
            subtotal = venda["qtd"] * venda["valor"]
            faturamento += subtotal
            quantidade_total += venda["qtd"]
            self.tabela_relatorios.insert(
                "", "end",
                values=(venda["data"], venda["item"], venda["qtd"], self.moeda(subtotal)),
            )
        self.total_relatorios.config(
            text=f"Peças vendidas: {quantidade_total}   |   Faturamento: {self.moeda(faturamento)}"
        )


if __name__ == "__main__":
    janela = tk.Tk()
    LojaApp(janela)
    janela.mainloop()
