from pathlib import Path
import glob
import shutil
import subprocess
import os
import re
try:
    import lxml
except ImportError:
    print("A biblioteca 'lxml' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'lxml'])
    import lxml
    
import html
from lxml import etree

try:
    import chardet
except ImportError:
    print("A biblioteca 'chardet' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'chardet'])
    import chardet

try:
    import simplekml
except ImportError:
    print("A biblioteca 'simplekml' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'simplekml'])
    import simplekml
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("A biblioteca 'matplotlib' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'matplotlib'])
    import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from matplotlib.collections import LineCollection

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
try:
    import cartopy.crs as ccrs
except ImportError:
    print("A biblioteca 'cartopy' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'cartopy'])
    import cartopy.crs as ccrs
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes




import numpy as np


    

    # Dicionário para mapear os nomes para os números
mapeamento_nomes = {
        'latitude: Latitude [deg]': None,
        'longitude: Longitude [deg]': None,
        'Temperature' : None,
        'Conductivity [S/m]': None
    }

numeros_variaveis = {
        'latitude': None,
        'longitude': None,
        'Temperature': None,
        'Conductivity': None
    }


    # Variáveis para armazenar os dados da tabela
dados_tabela = {
        'latitude': [],
        'longitude': [],
        'Temperature': [],
        'Conductivity': []
    }

    # Dicionário para armazenar os valores
valores = {
        'latitude': None,
        'longitude': None,
        'Temperature': None,
        'Conductivity': None
    }


def obter_estacoes_disponiveis(pasta_copia):
    estacoes = set()
    
    # Expressão regular para extrair o número da estação
    expressao = r'(\d{3}[a-zA-Z]*)'  # Procura 3 dígitos seguidos por zero ou mais letras

    # Iterar pelos nomes dos arquivos .hex
    arquivos_hex = [arquivo for arquivo in os.listdir(pasta_copia) if arquivo.endswith('.hex')]
    for arquivo in arquivos_hex:
        # Use a expressão regular para encontrar o número da estação e a versão
        matches = re.findall(expressao, arquivo)
        if matches:
            estacao = matches[0]
            estacoes.add(estacao)
    
    return estacoes


def cria_bat(input_range): #cria a lista dos processos que irão ser realizados
    result = []
    allowed_numbers = set(map(str, range(1, 22)))  # Números permitidos de 1 a 21 como strings

    for part in input_range.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(str.strip, part.split('-'))
            for num in range(int(start), int(end) + 1):
                if 1 <= num <= 21:
                    result.append(str(num).zfill(2))
                else:
                    print(f"O número '{num}' fora do intervalo 1-21 não pode ser processado.")
        else:
            if len(part) <= 2 and part in allowed_numbers:
                result.append(part.zfill(2))
            else:
                num = int(part)
                if 1 <= num <= 21:
                    result.append(str(num).zfill(2))
                else:
                    print(f"O número '{num}' fora do intervalo 1-21 não pode ser processado.")

    return result

# Criando o dicionário com os números e nomes correspondentes
numeros_nomes = {
    '01': 'Data Conversion',
    '02': 'Filter',
    '05': 'Loop Edit',
    '06': 'Derive',
    '07': 'Derive TEOS-10',
    '08': 'Bin Average',
}

def proc_bat(numeros_nomes, lista_bat): # relaciona os números do processo aos nomes
    lista_nome = []
    for numero in lista_bat:
        nome = numeros_nomes.get(numero)
        lista_nome.append(nome)
    return lista_nome

def converter_coordenadas(coordenada): # muda as coordenadas que estão na tabela, mas não muda na tabela
    graus, minutos, direcao = coordenada.split()
    graus = float(graus)
    minutos = float(minutos)
    decimal = graus + minutos / 60.0
    
    if direcao in ["S", "W"]:
        decimal = -decimal
        
    return decimal

# Lista para armazenar os dados das estações
def cria_tabela(pasta_processados):
    
    # Padrões de expressões regulares para extrair informações
    padrao_numero_estacao = re.compile(r'_(\d{3})\.cnv')
    #padrao_data_hora = re.compile(r'\* NMEA UTC \(Time\) = ([A-Za-z]{3} \d{2} \d{4} \d{2}:\d{2}:\d{2})')
    
    padrao_latitude = re.compile(r'\* NMEA Latitude = (\d+ \d+\.\d+ [NS])')
    padrao_longitude = re.compile(r'\* NMEA Longitude = (\d+ \d+\.\d+ [EW])')
   # padrao_data_hora = re.compile(r'\* NMEA UTC \(Time\) = (.+)')
    padrao_data_hora = re.compile(r'\* (System UpLoad Time|NMEA UTC \(Time\)) = (.+)')
    padrao_temperatura = re.compile(r'\* Temperature SN = (\d+)')
    padrao_condutividade = re.compile(r'\* Conductivity SN = (\d+)')

    # Lista para armazenar os dados das estações
    dados_estacoes = []


# Agora você pode usar o conteúdo decodificado para extrair as informações


    for arquivo_cnv in os.listdir(pasta_processados):
        if arquivo_cnv.endswith('.cnv'):
            numero_estacao = padrao_numero_estacao.search(arquivo_cnv).group(1)
            
            arq_ler = os.path.join(pasta_processados, arquivo_cnv)
            with open(arq_ler, 'r', encoding='latin-1') as arquivo:
                conteudo = arquivo.read()

                latitude_match = padrao_latitude.search(conteudo)
                longitude_match = padrao_longitude.search(conteudo)
               # data_hora_match = padrao_data_hora.search(conteudo)
                temperatura_match = padrao_temperatura.search(conteudo)
                condutividade_match = padrao_condutividade.search(conteudo)

            if latitude_match and longitude_match:
                latitude = latitude_match.group(1)
                longitude = longitude_match.group(1)
                
                
                if temperatura_match:
                    temperatura = temperatura_match.group(1)
                
                if condutividade_match:
                    condutividade = condutividade_match.group(1)
                
                if temperatura_match and condutividade_match:
                    dados_estacoes.append((latitude, longitude, temperatura, condutividade))
                else:
                    dados_estacoes.append((latitude, longitude))

    return dados_estacoes

#lista de quais estações vão ser processadas
def process_range(input_range):
    result = []

    for part in input_range.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(str.strip, part.split('-'))
            if start.isdigit() and end.isdigit():
                start = int(start)
                end = int(end)
                result.extend(f"{num:03d}" for num in range(start, end + 1))
        elif part.isdigit():
            result.append(f"{int(part):03d}")

    return result

def rename_files(source_dir, destination_dir, new_prefix): #renomear na pasta de cópia
    files = os.listdir(source_dir)
    for file in files:
        old_path = os.path.join(source_dir, file)
        new_file_name = file.replace('/', '_')  # Substituir barras por sublinhados
        new_path = os.path.join(destination_dir, new_prefix + new_file_name)
        os.rename(old_path, new_path)
        
def process(bat, pasta_processados, tabela, relatorio): #processa os dados
    input_string = input('Em quais estações irá processar os dados? (Escreva uma lista com 3 dígitos. Ex.: 001-010, 020)')
    input_list = process_range(input_string)

    for num in input_list:
        cmd = ('sbebatch ' + str(bat) + ' ' + num)                
        os.system(cmd)
    while True:
        input_string = input('Em quais estações irá processar os dados? (Escreva uma lista com 3 dígitos. Ex.: 001-010, 020\nCaso a estação tenha letras após o número, por favor, escreva, exemplo: 001ABC)\nCaso queira processar todas as estações, escreva "tudo".')
        
        if input_string == 'tudo':
            input_list = []
            for estacao in estacoes_versoes.items():                  
                cmd = f'sbebatch {bat} {estacao[0]}'
                input_list.append(estacao[0])
                os.system(cmd)
                
            with open(tabela, 'w') as arquivo_saida:
                arquivo_saida.write('Nº ESTAÇÃO\tData e Hora\tLatitude\tLongitude\n')
                    
            estacoes_registradas = set()
            try:
                with open(tabela, 'r') as arquivo_tabela:
                    for linha in arquivo_tabela:
                        estacao, *_ = linha.split('\t')
                        estacoes_registradas.add(estacao)
            except FileNotFoundError:
                pass  # O arquivo da tabela ainda não existe
            # Escrever os dados em um arquivo de texto em formato de tabela
            dados_estacoes = cria_tabela(pasta_processados)

            # Ordene a lista de dados apenas pelo número da estação
            dados_estacoes.sort(key=lambda x: x[0])

            with open(tabela, 'a') as arquivo_saida:
                for dados in dados_estacoes:
                    estacao = dados[0]
                    if estacao not in estacoes_registradas:
                        estacoes_registradas.add(estacao)
                        arquivo_saida.write('\t'.join(dados) + '\n')

            with open(relatorio, 'a') as arquivo:
                arquivo.write('\n\nForam processadas as seguintes estações:')
                for num in input_list:
                    arquivo.write('\nEstação ' + num)
            break
        
        else:
            input_list = process_range(input_string)
            estacoes_invalidas = []
    
            for estacao in input_list:
                if estacao not in estacoes_disponiveis:
                    estacoes_invalidas.append(estacao)
                    

            if estacoes_invalidas:
                print(f'As seguintes estações não estão disponíveis: {", ".join(estacoes_invalidas)}')
                print('Por favor, revise quais estações gostaria de processar e escreva corretamente.')
                continue  # Refaz a pergunta se houver estações inválidas
            
            if input_valido(input_string, estacoes_disponiveis) == False:
                print('Por favor, revise quais estações gostaria de processar e escreva corretamente.')
                continue  # Refaz a pergunta se houver estações inválidas
            
            # Todas as estações são válidas, prossiga com o processamento
            for num in input_list:
                cmd = ('sbebatch ' + str(bat) + ' ' + num)                
                os.system(cmd)
                
            with open(tabela, 'w') as arquivo_saida:
                arquivo_saida.write('Nº ESTAÇÃO\tData e Hora\tLatitude\tLongitude\n')
                    
            estacoes_registradas = set()
            try:
                with open(tabela, 'r') as arquivo_tabela:
                    for linha in arquivo_tabela:
                        estacao, *_ = linha.split('\t')
                        estacoes_registradas.add(estacao)
            except FileNotFoundError:
                pass  # O arquivo da tabela ainda não existe
            # Escrever os dados em um arquivo de texto em formato de tabela
            dados_estacoes = cria_tabela(pasta_processados)

            # Ordene a lista de dados apenas pelo número da estação
            dados_estacoes.sort(key=lambda x: x[0])

            with open(tabela, 'a') as arquivo_saida:
                for dados in dados_estacoes:
                    estacao = dados[0]
                    if estacao not in estacoes_registradas:
                        estacoes_registradas.add(estacao)
                        arquivo_saida.write('\t'.join(dados) + '\n')

            with open(relatorio, 'a') as arquivo:
                arquivo.write('\n\nForam processadas as seguintes estações:')
                for num in input_list:
                    arquivo.write('\nEstação ' + num)
            break

        
        
        
    # Dicionário para mapear os nomes para os números
    mapeamento_nomes = {
        'latitude: Latitude [deg]': None,
        'longitude: Longitude [deg]': None,
        'Temperature' : None,
        'Conductivity [S/m]': None
    }

    numeros_variaveis = {
        'latitude': None,
        'longitude': None,
        'Temperature': None,
        'Conductivity': None
    }


    # Variáveis para armazenar os dados da tabela
    dados_tabela = {
        'latitude': [],
        'longitude': [],
        'Temperature': [],
        'Conductivity': []
    }

    # Dicionário para armazenar os valores
    valores = {
        'latitude': None,
        'longitude': None,
        'Temperature': None,
        'Conductivity': None
    }

    # Flag para indicar quando a tabela começa
    tabela_comecou = False

    for arquivo_cnv in os.listdir(pasta_processados):
        if arquivo_cnv.endswith('.cnv'):            
            arq_ler = os.path.join(pasta_processados, arquivo_cnv)
            with open(arq_ler, 'r', encoding='latin-1') as arquivo:
                linhas = arquivo.readlines()

            # Percorra as linhas do arquivo
            for linha in linhas:
                # Verifique se a linha começa com "name" e contém um dos nomes no mapeamento
                if linha.startswith('# name'):
                    for nome, numero in mapeamento_nomes.items():
                        if nome in linha:
                            # Extraia o número do "name" e atualize o mapeamento
                            numero = int(linha.split('=')[0].strip().split()[-1])
                            mapeamento_nomes[nome] = numero

    # Percorra o dicionário de mapeamento e encontre os números associados aos nomes desejados
            for nome, numero in mapeamento_nomes.items():
                if nome.startswith('latitude'):
                    valores['latitude'] = numero
                elif nome.startswith('longitude'):
                    valores['longitude'] = numero
                elif nome.startswith('Temperature'):
                    valores['Temperature'] = numero
                elif nome.startswith('Conductivity'):
                    valores['Conductivity'] = numero

            for linha in linhas:
                # Verifique se a linha começa com "name" e contém uma das variáveis
                if linha.startswith('# name'):
                    for variavel in numeros_variaveis.keys():
                        if variavel in linha:
                            # Extraia o número do "name" e armazene no dicionário
                            numero = int(re.search(r'# name (\d+)', linha).group(1))
                            numeros_variaveis[variavel] = numero



            # Flag para indicar quando a tabela começa
            tabela_comecou = False


            # Percorra as linhas do arquivo
            for linha in linhas:
                # Verifique se a tabela começou
                if linha.strip() == '*END*':
                    tabela_comecou = True
                    continue

                # Se a tabela já começou, separe os valores por espaços em branco
                if tabela_comecou:
                    valore = linha.split()
                    
                    if len(valore) >= max(numeros_variaveis.values()) + 1:
                        for variavel, numero in numeros_variaveis.items():
                            # Use o número associado à variável para extrair o valor correto
                            indice_valor = numero
                            valor = valore[indice_valor] if valore[indice_valor] != 'NaN' else None
                            dados_tabela[variavel].append(valor)
                


            # Abra o arquivo para escrita (isso substituirá qualquer conteúdo existente)
    with open(tabela, 'w') as arquivo:
                # Escreva o cabeçalho da tabela
        arquivo.write("latitude\tlongitude\tTemperature\tConductivity\n")

                # Escreva os dados
        for i in range(len(dados_tabela['latitude'])):
            linha = f"{dados_tabela['latitude'][i]}\t{dados_tabela['longitude'][i]}\t{dados_tabela['Temperature'][i]}\t\t{dados_tabela['Conductivity'][i]}\n"
            arquivo.write(linha)


    print(f'Os novos dados foram escritos em {tabela}')
   
    
    with open(relatorio, 'a') as arquivo:
        arquivo.write('\n\nForam processadas as seguintes estações:')
        for num in input_list:
            arquivo.write('\nEstação ' + num)

def end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_relatorio): #conferir se o processamento terminou
    terminar = input('Deseja terminar o processamento? (s/n)').lower()
    if terminar == 's':
        print('Processamento concluído!')
        print('Obrigado por utilizar o programa!')
    else:
        process(bat, pasta_processados, tabela, relatorio)
        cria_kml(pasta_processados, tabela)
        plotar(tabela, pasta_relatorio)
        end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_relatorio)
        


def converter_coordenadas(coordenada):
    graus, minutos, direcao = coordenada.split()
    graus = float(graus)
    minutos = float(minutos)
    decimal = graus + minutos / 60.0
    
    if direcao in ["S", "W"]:
        decimal = -decimal
        
    return decimal

def criar_arquivo_kml(nome_arquivo, lista_coordenadas):
    kml = simplekml.Kml()

    rota = kml.newlinestring(name="Rota das Estações")
    style = simplekml.Style()
    style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'

    for estacao, coordenadas in lista_coordenadas.items():
        latitude, longitude = coordenadas
        ponto = kml.newpoint(name=estacao, coords=[(longitude, latitude)])
        ponto.style = style
        rota.coords.addcoordinates([(longitude, latitude)])
        

    kml.save(nome_arquivo)

def cria_kml(pasta_processados, tabela):
    confere = input('Deseja criar um arquivo KML? (s/n)')
    if confere == 's':
        
        latitude = []
        longitude = []
        with open(tabela, 'r') as arquivo:
            next(arquivo)
            
            for linha in arquivo:
                colunas = linha.strip().split('\t')
                
                # Converter os valores para os tipos apropriados e adicioná-los às listas
                latitude.append(float(colunas[0]))
                longitude.append(float(colunas[1]))
                
        kml = simplekml.Kml()
        # Crie um ícone personalizado (triângulo deitado)
        icon_style = simplekml.IconStyle(
            scale=0.5,  # Tamanho do ícone (ajuste conforme necessário)
            color=simplekml.Color.white,  # Cor do ícone (branco)
            icon=simplekml.Icon(
                href='http://maps.google.com/mapfiles/kml/shapes/triangle.png'  # Ícone de triângulo do Google
            )
        )

        # Crie um Placemark (marcador) para cada ponto no caminho
        for i in range(len(latitude)):
            # Verifique se já passou por pelo menos 10 posições
            if i % 10 == 0:
                placemark = kml.newpoint(
                    coords=[(longitude[i], latitude[i])],  # Coordenadas do ponto (longitude, latitude)
                    description="Indicação de direção",  # Descrição do ponto de direção
                )

        # Crie um caminho no KML usando os dados de latitude e longitude e aplique o estilo
        path = kml.newlinestring(
            name="Caminho",
            description="Descrição do caminho",
        )
            # Salve o arquivo KML
        nome_kml = input('Digite o nome do seu arquivo KML: ')

        nome = os.path.join(pasta_processados, 'Relatório', nome_kml + '.kml')
        kml.save(nome)
                
    else:
        return

def plotar(tabela, relatorio):
    confere = input('Deseja criar gráfico termo? (s/n)')
    if confere == 's':
                
        temperatura = []
        condutividade = []
        latitude = []
        longitude = []

        with open(tabela, 'r') as arquivo:
            next(arquivo)
            
            for linha in arquivo:
                colunas = linha.strip().split('\t')
                
                # Converter os valores para os tipos apropriados e adicioná-los às listas
                temperatura.append(float(colunas[2]))
                condutividade.append(float(colunas[4]))
                latitude.append(float(colunas[0]))
                longitude.append(float(colunas[1]))
                
    
        vmin, vmax = min(latitude), max(latitude)
        tmin, tmax = int(min(temperatura)), int(max(temperatura))

       
        # Crie uma figura maior que acomodará ambos os gráficos
        fig = plt.figure(figsize=(12, 6))

        # Primeiro gráfico (maior amplitude de lat e long)
        ax1 = fig.add_subplot(121)  # 1 linha, 2 colunas, primeiro gráfico
        ax1.set_title('Mapa de Temperaturas')
        ax1.set_xlabel('Longitude', labelpad=20)
        ax1.set_ylabel('Latitude', labelpad=30)

        # Crie um mapa para o primeiro gráfico
        m1 = Basemap(
            projection='merc',
            llcrnrlat=min(latitude) - 10,
            urcrnrlat=max(latitude) + 10,
            llcrnrlon=min(longitude) - 10,
            urcrnrlon=max(longitude) + 10,
            resolution='l',
            ax=ax1
        )

        # Desenhe a costa e os limites do mapa no primeiro gráfico
        m1.drawcoastlines()
        m1.drawcountries()

        # Plote os pontos no primeiro gráfico com base em latitude e longitude
        x1, y1 = m1(longitude, latitude)
        sc1 = m1.scatter(x1, y1, c=temperatura, cmap='coolwarm', marker='o', s=9, edgecolor='k', linewidths=0.5)

        # Segundo gráfico (valores puros com barra de temperatura)
        ax2 = fig.add_subplot(122)  # 1 linha, 2 colunas, segundo gráfico
        ax2.set_title('Mapa de Temperaturas')
        ax2.set_xlabel('Longitude', labelpad=20)
        ax2.set_ylabel('Latitude', labelpad=30)

        # Crie um mapa para o segundo gráfico
        m2 = Basemap(
            projection='merc',
            llcrnrlat=min(latitude) - 1,
            urcrnrlat=max(latitude) + 1,
            llcrnrlon=min(longitude) - 5,
            urcrnrlon=max(longitude) + 5,
            resolution='l',
            ax=ax2
        )

        # Desenhe a costa e os limites do mapa no segundo gráfico (mesmo mapa do primeiro)
        m2.drawcoastlines()
        m2.drawcountries()

        # Plote os pontos no segundo gráfico com base em latitude e longitude
        x2, y2 = m2(longitude, latitude)
        sc2 = m2.scatter(x2, y2, c=temperatura, cmap='coolwarm', marker='o', s=9, edgecolor='k', linewidths=0.5)

        # Adicione uma barra de cores ao segundo gráfico
        divider = make_axes_locatable(ax2)
        cax2 = divider.append_axes("right", size="5%", pad=0.05)
        cbar2 = plt.colorbar(sc2, orientation='vertical', shrink=0.75, cax=cax2,extend='both', pad=0.03, aspect=20, ticks=np.linspace(tmin, tmax, 10))
        cbar2.set_label('Temperatura (°C)')
        cbar2.set_ticks(np.arange(int(tmin), int(tmax) + 1, 1))

        
        # Adicione uma barra de cores ao segundo gráfico
        divider = make_axes_locatable(ax1)
        cax1 = divider.append_axes("right", size="5%", pad=0.05)
        cbar1 = plt.colorbar(sc1, orientation='vertical', shrink=0.75, cax=cax1,extend='both', pad=0.03, aspect=20, ticks=np.linspace(tmin, tmax, 10))
        cbar1.set_label('Temperatura (°C)')
        cbar1.set_ticks(np.arange(int(tmin), int(tmax) + 1, 1))


               # cbar = plt.colorbar(sc, orientation='vertical', shrink=0.75, ax=ax, extend='both', pad=0.03, aspect=20, ticks=np.arange(vmin, vmax ))
       # cbar.set_label('Temperatura (°C)')

        # Desenhe linhas de latitude e longitude em ambos os mapas
        parallels1 = range(int(min(latitude) - 10), int(max(latitude) + 10) + 1, 2)
        meridians1 = range(int(min(longitude) - 10), int(max(longitude) + 10) + 1, 5)
        m1.drawparallels(parallels1, labels=[1,0,0,0], fontsize=10, linewidth=0.5)
        m1.drawmeridians(meridians1, labels=[0,0,0,1], fontsize=10, linewidth=0.5)

        parallels2 = range(int(min(latitude) - 1), int(max(latitude) + 1) + 1, 2)
        meridians2 = range(int(min(longitude) - 5), int(max(longitude) + 5) + 1, 5)
        m2.drawparallels(parallels2, labels=[1,0,0,0], fontsize=10, linewidth=0.5)
        m2.drawmeridians(meridians2, labels=[0,0,0,1], fontsize=10, linewidth=0.5)
        
        # Adicione linhas contínuas no segundo gráfico

        for temp in np.unique(temperatura):
            indices = np.where(temperatura == temp)[0]
            color = sc2.to_rgba(temp)
            for index in indices:
                ax2.plot(x2[index], y2[index], 'o', color=color, markersize=5, linewidth=1)
                
        for temp in np.unique(temperatura):
            indices = np.where(temperatura == temp)[0]
            color = sc1.to_rgba(temp)
            for index in indices:
                ax1.plot(x1[index], y1[index], 'o', color=color, markersize=3, linewidth=1)

            #ax2.plot(x_temp, y_temp, color=color, )

        # Ajuste o espaço entre os gráficos (reduza o espaço horizontal)
        plt.subplots_adjust(wspace=0.2)
        caminho_do_arquivo =os.path.join(relatorio, 'Gráfico_Temperatura.png')
        

# Depois de ter criado o gráfico e configurado tudo, você pode salvar assim:
        plt.savefig(caminho_do_arquivo)

        # Mostrar o mapa
        plt.show()




    else:
        return



lista_print = [] #armazena as strings do relatório
def list_print(message):
    lista_print.append(message)
    print(message)

def main():
    
    # Verificação de processamento novo ou continuação
    continuar_processamento = input('Deseja fazer um processamento novo? (s/n)').lower()
    
    if continuar_processamento == 'n':
        # Continuação de processamento
        pasta_processados = input('Digite o caminho da pasta de dados processados:')
        caminho_bat = os.path.join(pasta_processados, 'Batch_file')
        arquivos_na_pasta = os.listdir(caminho_bat)
        
        if len(arquivos_na_pasta) != 1 or not arquivos_na_pasta[0].endswith('.txt'):
            print('Não foi possível determinar o Btach file na pasta.')
            return
        bat = os.path.join(caminho_bat, arquivos_na_pasta[0])
        caminho_split = 'Processamento_split'
        pasta_split = os.path.join(pasta_processados, caminho_split)
        
        tabela = os.path.join(pasta_processados, 'Relatório',  'Tabela_de_posição.txt')
        relatorio = os.path.join(pasta_processados, 'Relatório',  'Relatório_de_dados_e_processamento.txt')
        pasta_relatorio = os.path.join(pasta_processados, 'Relatório')

        process(bat, pasta_processados, tabela, relatorio)
        cria_kml(pasta_processados, tabela)
        plotar(tabela, pasta_relatorio)
        end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_relatorio)


    else:
        nome_path = input('Em que pasta estão os dados? (digite o caminho da pasta)')
        pasta = Path(nome_path)

        #Novo processamento
        if pasta.exists():
            nome_copia = input('Dê nome à pasta que você quer trabalhar: (use _ no lugar de espaços)')
            pasta_copia = pasta.parent / (nome_copia + '//')
            shutil.copytree(pasta, pasta_copia)

        # RENOMEANDO OS ARQUIVOS 
            lista_arquivos = os.listdir(pasta_copia)
            replace = input('Como gostaria de renomear os arquivos?') + '_'
            # Padrão de expressão regular para encontrar a parte do número da estação no nome do arquivo
            padrao_numero_estacao = re.compile(r'(.+?)(\d{3}[a-zA-Z]*)(\..*$)')


            for file in lista_arquivos:
                # Use a expressão regular para encontrar o número da estação
                match = padrao_numero_estacao.search(file)
                if match:
                    parte_anterior = match.group(1)
                    numero_estacao = match.group(2)
                    extensao_arquivo = match.group(3)
                else:
                    # Se não encontrar um número de estação, deixe tudo em branco
                    parte_anterior = ''
                    numero_estacao = ''
                    extensao_arquivo = ''

                name_dir = str(pasta_copia) + '//'
                old_name = name_dir + file
                new_name = f'{name_dir}{replace}{numero_estacao}{extensao_arquivo}'
                    # Verifique se o novo nome de arquivo já existe
                
                if old_name == new_name or os.path.exists(new_name):
                    print(f'O aquivo {old_name} será mantido como {old_name}\nPor favor, verifique manualmente se há mais um tipo de processamento junto aos dados e faça as alterações necessárias')
                else:
                    os.rename(old_name, new_name)
              #  print(f'{numero_estacao}{extensao_arquivo}')


            # Contagem de arquivos e tipos
            arquivos = glob.glob(os.path.join(pasta_copia, '*'))
            counter = len(arquivos)
            n_hex = len(list(pasta_copia.glob('*.hex')))
            n_bl = len(list(pasta_copia.glob('*.bl')))
            n_hdr = len(list(pasta_copia.glob('*.hdr')))
            n_mrk = len(list(pasta_copia.glob('*.mrk')))
            n_xmlcon = len(list(pasta_copia.glob('*.XMLCON')))
            other = counter - (n_hex + n_bl + n_hdr + n_mrk + n_xmlcon)

            print('Sua pasta de dados processados foi criada!')
            list_print(f'Foram copiados {counter} arquivos.')
            list_print(f'Há {n_hex} arquivos do tipo HEX')
            list_print(f'{n_bl} arquivos do tipo BL')
            list_print(f'{n_hdr} arquivos do tipo HDR')
            #list_print(f'{n_mrk} arquivos do tipo MRK')
            list_print(f'{n_xmlcon} arquivos do tipo XMLCON')
            
            if other > 0:
                
                # Lista para armazenar os nomes dos arquivos que não são .ros ou outros tipos específicos
                list_print(f'Há {other} outros arquivos:')
                #print('Tipos de arquivos em "outros":')
                for arquivo in arquivos:
                    extensao = Path(arquivo).suffix
                    if extensao not in ['.hex', '.bl', '.hdr', '.mrk', '.XMLCON']:
                        list_print(arquivo)

        # Contagem de estações
            n_estacoes = n_hex
            list_print(f'Os dados fornecem um total de {n_estacoes} estações.')

            # Verificação de estações completas
            estações_completas = True
            tipos_arquivos = {'.hex', '.bl', '.hdr', '.XMLCON'}
            tipos_faltando = set()
            for station in range(1, n_estacoes + 1):
                station_files = [f'{station:03d}{ext}' for ext in tipos_arquivos]
                missing_files = [file for file in station_files if not any(file in os.path.basename(arq) for arq in arquivos)]
                if missing_files:
                    estações_completas = False
                    tipos_faltando.update([Path(file).suffix for file in missing_files])
                    list_print(f'A estação {station:03d} não está completa. Faltando: {", ".join(missing_files)}')

            if estações_completas:
                list_print('Todas as estações estão completas.')
            lista_arquivos = os.listdir(pasta_copia)


            # CRIANDO PASTA DE DADOS PROCESSADOS    
            nome_processados = input('Nomeie a sua pasta de dados processados: (use _ no lugar de espaços)')
            pasta_processados = pasta.parent / nome_processados
            os.mkdir(pasta_processados)
            nome_pasta_bat = 'Batch_file'
            caminho_bat = os.path.join(pasta_processados, nome_pasta_bat)
            caminho_relatorio = 'Relatório'
            pasta_relatorio = os.path.join(pasta_processados, caminho_relatorio)
            os.makedirs(pasta_relatorio)
            
            # ESCREVENDO RELATÓRIO
            nome_relatorio = 'Relatório_de_dados_e_processamento.txt'
            relatorio = os.path.join(pasta_relatorio, nome_relatorio)
            nome_tabela = 'Tabela_de_posição.txt'
            tabela = os.path.join(pasta_relatorio, nome_tabela)
            with open(tabela, 'w') as arquivo_saida:
                arquivo_saida.write('Latitude\tLongitude\tTemperatura\tCondutividade\n')


            with open(relatorio, 'w') as arq:
                arq.write('RELATÓRIO DE DADOS E PROCESSAMENTO\n')
                arq.write('O relatório presente fornece todas as informações obtidas a partir dos dados brutos.')
                arq.write('\nPor favor, cheque todas as informações e adicione o que achar relevante para o processamento dos dados.\n')
                for i in lista_print:
                    arq.write('\n' + i)
            
            lista_print.clear()
            
            print('Sua pasta foi criada!')
            
            # CRIANDO BATCH FILE (**CONFERIR SE JÁ EXISTE)
            bat_existe = False
            confere = str(input('Você já possui um arquivo PSA para realizar o processamento? (s/n)'))
            pasta_psa = 'Arquivos_PSA'
            caminho_psa = os.path.join(pasta_processados, pasta_psa)
            os.makedirs(caminho_psa)

            if confere == 's':
                print(f'Por favor, coloque os seus arquivos PSA na pasta Arquivos_PSA que se encontra em {nome_processados}')
                #print('Para esse processamento, serão necessários 11 arquivos PSA: DatCnv.psa, Filter.psa, AlignCTD.psa, CellTM.psa. LoopEdit.psa, Derive.psa, BinAvg.psa,\n BottleSum.psa, WildEdit.psa, Split.psa, SeaPlot.psa')
                print('Confira que os arquivos PSA estão nomeados segundo a nomeclatura padrão do SBEDataProcessing')
                input('Pressione Enter após terminar...')
                
            else:
                print(f'Por favor, crie os arquivos PSA desejados e coloque-os na pasta Arquivos_PSA que se encontra em {nome_processados}')
                #print('Para esse processamento, serão necessários 11 arquivos PSA: DatCnv.psa, Filter.psa, AlignCTD.psa, CellTM.psa. LoopEdit.psa, Derive.psa, BinAvg.psa,\n BottleSum.psa, WildEdit.psa, Split.psa, SeaPlot.psa')
                print('Confira que os arquivos PSA estão nomeados segundo a nomeclatura padrão do SBEDataProcessing')
                input('Pressione Enter após terminar...')
                
            # Lista todos os arquivos na pasta arq_psa
            arquivos = os.listdir(caminho_psa)
            confere_seaplot = False
            
            arq_loop = None
            arq_bin = None
            arq_dat = None
            arq_filter = None
            arq_derive = None
            
            arquivos_psa = glob.glob(os.path.join(caminho_psa, '*.psa'))
            for arquivo in arquivos_psa:
                nome_arquivo = os.path.basename(arquivo)
                termo = nome_arquivo.split('.')[-2] + '.psa' # Extrai o termo antes da extensão .psa
                #print(termo)
                if termo == 'AlignCTD.psa':
                    arq_align = arquivo
                   # print('foi align')
                elif termo == 'BinAvg.psa':
                    arq_bin = arquivo
                  #  print('foi bin')
                elif termo == 'BottleSum.psa':
                    arq_sum = arquivo
                  #  print('foi sum')
                elif termo == 'CellTM.psa':
                    arq_cell = arquivo
                  #  print('foi cell')
                elif termo == 'DatCnv.psa':
                    arq_dat = arquivo
                 #   print('foi dat')
                elif termo == 'Derive.psa':
                    arq_derive = arquivo
                 #   print('foi derive')
                elif termo == 'Filter.psa':
                    arq_filter = arquivo
                #    print('foi filter')
                elif termo == 'LoopEdit.psa':
                    arq_loop = arquivo
                 #   print('foi loop')
                elif termo == 'SeaPlot.psa' or termo == 'SeaPlot_autoscale1.psa':
                    arq_sea = arquivo
                 #   print('foi seaplot')
                elif termo == 'SeaPlot_ts.psa':
                    confere_seaplot = True
                    arq_ts = arquivo
                elif termo == 'Split.psa':
                    arq_split = arquivo
                 #   print('foi split')
                elif termo == 'WildEdit.psa':
                    arq_wild = arquivo
                #    print('foi wild')
                elif termo == 'MarkScan.psa':
                    arq_scan = arquivo
                elif termo == 'Buoyancy.psa':
                    arq_buoy = arquivo
                elif termo == 'W_Filter.psa':
                    arq_wf = arquivo
                elif termo == 'Section.psa':
                    arq_section = arquivo
                elif termo == 'Strip.psa':
                    arq_strip = arquivo
                elif termo == 'Trans.psa':
                    arq_trans = arquivo
            

            
            confere_bat = input('Você já possui um Batch File para realizar esse processamento? (s/n)')
            if confere_bat == 's':
                os.makedirs(caminho_bat, exist_ok=True)  # Criar diretório Batch_file, se não existir
                print('Por favor, coloque seu Batch File na pasta Batch_file.\n Faça todas as modificações necessárias \nPressione enter após terminar.')
                print('É recomendável que você registre no arquivo de relatório desse processamento quais processos do SBE Data Processing está realizando.')
                with open(relatorio, 'w') as arq:
                    arq.write('\nDurante o processamento foi utilizado um Batch File já existente.')
            
            else:
                nome_bat = input('Dê nome ao seu batch file (sugestão: batch_nome_do_programa): ') + '.txt'
                bat = os.path.join(caminho_bat, nome_bat)
                os.makedirs(caminho_bat, exist_ok=True)  # Criar diretório Batch_file, se não existir
                name_dir = str(pasta_copia) + '//'
               # input_string = input('Quais processamentos você deseja realizar?')
               # lista_bat = cria_bat(input_string)
              #  lista_nomes = proc_bat(numeros_nomes, lista_bat)

                with open(relatorio, 'a') as arq:
                    arq.write(f'\n\nDurante o processamento foi criado um novo Batch File, chamado {nome_bat}.\n')
                    arq.write('O Batch File utilizado está configurado para realizar os seguintes processamentos:\n')
                #    for i in lista_nomes:
                #        arq.write('\n' + i)


                with open(bat, 'w') as arquivo:
                   # arquivo.write('datcnv  /i' + str(name_dir) + str(replace) + '%1.hex' + ' ' + '/p' + str(arq_dat) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + '%1.XMLCON' )
                    if arq_dat:
                        arquivo.write('datcnv  /i' + str(name_dir) + str(replace) + '%1.hex' + ' ' + '/p' + str(arq_dat) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + '%1.XMLCON' )
                        with open(relatorio, 'a') as arq:
                            arq.write('\nDatCnv')
                    if arq_filter:
                        arquivo.write('\nfilter  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_filter) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        with open(relatorio, 'a') as arq:
                            arq.write('\nFilter')
                    if arq_loop:
                        arquivo.write('\nloopedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_loop) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        with open(relatorio, 'a') as arq:
                            arq.write('\nLoopEdit')
                    if arq_derive:
                        arquivo.write('\nderive  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_derive) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + '%1.XMLCON' )
                        with open(relatorio, 'a') as arq:
                            arq.write('\nDerive')
                    if arq_bin:
                        arquivo.write('\nbinavg  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_bin) +  ' /f' + replace + '%1.cnv' + ' /o' + str(pasta_processados))
                        with open(relatorio, 'a') as arq:
                            arq.write('\nBinAverage')
                    
            input('Por favor, antes de realizar o processamento, confira todas as informações no arquivo de relatório e adicione o que achar necessário. \nPressione Enter quando estiver pronto para realizar o processamento.')
            pasta_relatorio = os.path.join(pasta_processados, 'Relatório')
            process(bat, pasta_processados, tabela, relatorio)
            
            cria_kml(pasta_processados, tabela)
            plotar(tabela, pasta_relatorio)
            end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_relatorio)


        else:
            print('A pasta indicada não existe.')
    

if __name__ == "__main__":
    main()
