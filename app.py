
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import re
import pandas as pd
import time

servico = Service()
options = Options()
options.add_argument("window-size=500,1200")

driver = webdriver.Chrome(service=servico,options=options)


def buscar_dados_empresas(query):
    
    try:
        driver.get("https://www.google.com")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.submit()
        time.sleep(3)
        dados = []

        btnNextPage = driver.find_elements(By.XPATH, "//*[contains(text(), 'Mais empresas') or contains(text(), 'Mais lugares')]")

        if btnNextPage:
            btnNextPage[0].click()

            for i in range(10):

                cards = driver.find_elements(By.CSS_SELECTOR, ".E94Gcd")  

                for card in cards:
                    nome_empresa = card.find_element(By.CSS_SELECTOR, ".I9iumb").text
                    celulares = re.findall(r"\(11\)\s?9\d{4}[-\s]?\d{4}", card.text)      

                    if celulares:
                        dados.append([nome_empresa, celulares[0]])

                btnNextPage = driver.find_elements(By.XPATH, "//*[contains(text(), 'Próxim') and @jsname='V67aGc']")
               
                if btnNextPage:
                    btnNextPage[0].click()
                    time.sleep(3)
                else:
                    print("Não existem outras páginas para esta busca")
                    break

    except Exception as e:
        print(f"Erro durante a busca a pesquisa {query}. / Detalhes tecnicos: {e}")


    return dados


if __name__ == "__main__":

    # Limpa o arquivo contatos_celulares.csv ao iniciar
    if os.path.exists("contatos_celulares.csv"):
        os.remove("contatos_celulares.csv")

    # Lê a lista de municípios, regiões e siglas do arquivo CSV
    municipios_df = pd.read_csv("municipios.csv")
    municipios = municipios_df.to_dict(orient="records")  # Converte em lista de dicionários

    # Lê os tipos de empresas do arquivo CSV
    tipos_df = pd.read_csv("tipos_empresas.csv")
    tipos = tipos_df["tipo"].tolist()

    for cidade in municipios:
        municipio = cidade["municipio"]
        regiao =  cidade["regiao"]
        sigla = cidade["sigla"]

        for tipo in tipos:
            print(f"Buscando por {tipo} em: {municipio}")
            query = f'"{tipo}"+"{municipio} - {sigla}"'

            registros = []
            itens = buscar_dados_empresas(query)

            for item in itens:                
                registros.append({
                    "municipio": municipio,
                    "regiao": regiao,
                    "sigla": sigla,
                    "tipo": tipo,
                    "nome_estabelecimento": item[0],
                    "celulare": item[1]
                })

            if registros: 
                df = pd.DataFrame(registros)
                df.to_csv("contatos_celulares.csv", mode='a', header=not os.path.exists("contatos_celulares.csv"), index=False, encoding='utf-8')

    print("Busca concluída. Os dados foram salvos em contatos_celulares.csv.")