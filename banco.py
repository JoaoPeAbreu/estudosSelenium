from livro import Livro
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class Livros:

    def __init__(self, url: str) -> None:
        self.url = url
        self.driver = self._configurar_driver()
        self.title_list = []
        self.listastk = []
        self.listapreco = []
        self.con = None

    def _configurar_driver(self):
        service = Service()
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def conectar(self):
        if self.con is None:
            self.con = sqlite3.connect("Site1.db")
            self.cur = self.con.cursor()
    
    def desconectar(self):
        if self.con is not None:
            self.con.close()
            self.con = None

    def criar_tabela(self):
        self.conectar()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS livros (
                            titulo TEXT PRIMARY KEY,
                            estoque INTEGER NOT NULL,
                            preco REAL NOT NULL
        )""")
        self.desconectar()

    def inserir_livro(self, l: Livro):
        self.conectar()
        nlivro = (l.tit, l.est, l.pre)
        self.cur.execute("""INSERT INTO livros (titulo, estoque, preco)
                            VALUES (?, ?, ?)""", nlivro)
        self.con.commit()
        self.desconectar()
    
    def scrape_titulos(self):
        self.driver.get(self.url)
        title_elements = self.driver.find_elements(By.TAG_NAME, 'a')[54:94:2]
        self.title_list = [title.get_attribute('title') for title in title_elements]
        return title_elements

    def scrape_detales(self, title_elements):
        for i, title in enumerate(title_elements):
            title.click()

            qtdstk = int(self.driver.find_element(By.CLASS_NAME, 'instock').text.replace('In stock (', '').replace(' available)', ''))
            preco = float(self.driver.find_element(By.CLASS_NAME, 'price_color').text.replace('£', ''))

            self.listastk.append(qtdstk)
            self.listapreco.append(preco)

            livro = Livro(tit=self.title_list[i], est=qtdstk, pre=preco)
            self.inserir_livro(livro)

            self.driver.back()

    def mostrar_livros(self):
        self.conectar()
        self.cur.execute("SELECT * FROM livros")
        livros = self.cur.fetchall()
        self.desconectar()
        
        for livro in livros:
            print(f"Título: {livro[0]}, Estoque: {livro[1]}, Preço: £{livro[2]:.2f}")

    def mostrar_barato(self):
        self.conectar()
        self.cur.execute("SELECT * FROM livros ORDER BY preco ASC LIMIT 1")
        livro_barato = self.cur.fetchone()
        self.desconectar()
        
        if livro_barato:
            print(f"Livro mais barato: Título: {livro_barato[0]}, Estoque: {livro_barato[1]}, Preço: £{livro_barato[2]:.2f}")
        else:
            print("Nenhum livro encontrado.")

    def mostrar_caro(self):
        self.conectar()
        self.cur.execute("SELECT * FROM livros ORDER BY preco DESC LIMIT 1")
        livro_caro = self.cur.fetchone()
        self.desconectar()
        
        if livro_caro:
            print(f"Livro mais caro: Título: {livro_caro[0]}, Estoque: {livro_caro[1]}, Preço: £{livro_caro[2]:.2f}")
        else:
            print("Nenhum livro encontrado.")
    
    def inserir_menu(self):
        """Este método imprime uma lista de opições
        """
        print("--------------------Menu----------------------")
        print("|     1- Mostrar livros                      |")
        print("|     2- Mostrar livros mais baratos         |")
        print("|     3- Mostrar livros mais caros           |")
        print("|     4- Sair                                |")
        print("----------------------------------------------")

    def criar_menu(self):
        sair = False
        while not sair:
            self.inserir_menu()
            try:
                opicao = int(input("O que você quer fazer: "))
                if opicao == 1:
                    self.mostrar_livros()
                elif opicao == 2:
                    self.mostrar_barato()
                elif opicao == 3:
                    self.mostrar_caro()
                elif opicao == 4:
                    sair = True
                else:
                    print("Opção invalida!")
            except ValueError:
                print("Opção invaliada, por favor digite um número")

if __name__ == '__main__':
    e = Livros(url="https://books.toscrape.com/")
    e.criar_tabela()
    title_elements = e.scrape_titulos()
    e.scrape_detales(title_elements)
    e.criar_menu()
    e.inserir_menu()