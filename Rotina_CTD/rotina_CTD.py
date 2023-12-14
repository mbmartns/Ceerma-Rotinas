from pathlib import Path
import glob
import shutil
import subprocess
import os
import re
import lxml
import sys
import html
from lxml import etree
import chardet
import simplekml
from collections import defaultdict



def cria_bat(input_range):
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
    '03': 'Align CTD',
    '04': 'Cell Thermal Mass',
    '05': 'Loop Edit',
    '06': 'Derive',
    '07': 'Derive TEOS-10',
    '08': 'Bin Average',
    '09': 'Bottle Summary',
    '10': 'Mark Scan',
    '11': 'Buoyancy',
    '12': 'Wild Edit',
    '13': 'Window Filter',
    '14': 'ASCII In',
    '15': 'ASCII Out',
    '16': 'Section',
    '17': 'Split',
    '18': 'Strip',
    '19': 'Translate',
    '20': 'Sea Plot',
    '21': 'SeaCalc III'
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
    padrao_numero_estacao = re.compile(r'_(\d{3}[a-zA-Z]*)\.cnv')
    padrao_latitude = re.compile(r'\* NMEA Latitude = (\d{2} \d+\.\d+ [NS])')
    padrao_longitude = re.compile(r'\* NMEA Longitude = (\d{3} \d+\.\d+ [EW])')
    padrao_data_hora = re.compile(r'\* NMEA UTC \(Time\) = ([A-Za-z]{3} \d{2} \d{4} \d{2}:\d{2}:\d{2})')
    
    # Lista para armazenar os dados das estações
    dados_estacoes = []

    for arquivo_cnv in os.listdir(pasta_processados):
        if arquivo_cnv.endswith('.cnv'):
            numero_estacao = padrao_numero_estacao.search(arquivo_cnv).group(1)
            
            arq_ler = os.path.join(pasta_processados, arquivo_cnv)
            with open(arq_ler, 'r', encoding='latin-1') as arquivo:
                conteudo = arquivo.read()

                latitude_match = padrao_latitude.search(conteudo)
                longitude_match = padrao_longitude.search(conteudo)
                data_hora_match = padrao_data_hora.search(conteudo)
            
            if latitude_match and longitude_match and data_hora_match:
                latitude = latitude_match.group(1)
                longitude = longitude_match.group(1)
                data_hora = data_hora_match.group(1)
                
                dados_estacoes.append((numero_estacao, data_hora, latitude, longitude))
                
    return dados_estacoes

#lista de quais estações vão ser processadas
def process_range(input_range):
    result = []

    # Divide a entrada em partes separadas por vírgulas
    parts = input_range.split(',')

    for part in parts:
        part = part.strip()

        # Verifica se a parte contém um intervalo (por exemplo, "001-010")
        if '-' in part:
            start, end = map(str.strip, part.split('-'))
            
            # Verifica se o início e o fim são compostos apenas por dígitos ou dígitos seguidos de letras
            if re.match(r'^\d+[a-zA-Z]*$', start) and re.match(r'^\d+[a-zA-Z]*$', end):
                result.extend(f"{num:03}" for num in range(int(start), int(end) + 1))
        
        # Verifica se a parte é composta apenas por dígitos ou dígitos seguidos de letras
        elif re.match(r'^\d+[a-zA-Z]*$', part):
            result.append(f"{(part):03}")

    return result



def rename_files(source_dir, destination_dir, new_prefix): #renomear na pasta de cópia
    files = os.listdir(source_dir)
    for file in files:
        old_path = os.path.join(source_dir, file)
        new_file_name = file.replace('/', '_')  # Substituir barras por sublinhados
        new_path = os.path.join(destination_dir, new_prefix + new_file_name)
        os.rename(old_path, new_path)

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

def input_valido(input_string, estacoes_disponiveis):
    input_list = input_string.split(',')
    
    for item in input_list:
        item = item.strip()
        
        if '-' in item:
            start, end = map(str.strip, item.split('-'))
            
            if not (re.match(r'^\d+[a-zA-Z]*$', start) and re.match(r'^\d+[a-zA-Z]*$', end)):
                return False
        elif not (re.match(r'^\d+[a-zA-Z]*$', item) and item in estacoes_disponiveis):
            return False
    
    return True


def process(bat, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes): #processa os dados
    # Obtenha a lista de estações disponíveis
    estacoes_disponiveis = obter_estacoes_disponiveis(pasta_copia)
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
    


def end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes): #conferir se o processamento terminou
    while True:
        terminar = input('Deseja terminar o processamento? (s/n)').lower()
        if terminar == 's':
            print('Processamento concluído!')
            print('Obrigado por utilizar nosso sistema!')
            break
        elif terminar == 'n':
            process(bat, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes)
            split(pasta_split)
            cria_kml(pasta_processados, tabela)
        else:
            print('Resposta inválida. Por favor, responda com "s" para sim ou "n" para não.')

            
def split(pasta_split): # separa os arquivos de subida e de descida
    while True:
        conferir = input('Deseja separar os arquivos de subida e descida? (s/n)').lower()
        if conferir == 's':
            pasta_up = os.path.join(pasta_split, 'up')
            pasta_down = os.path.join(pasta_split, 'down')

            if not os.path.exists(pasta_up):
                os.makedirs(pasta_up)

            if not os.path.exists(pasta_down):
                os.makedirs(pasta_down)
            arquivos_cnv = [arquivo for arquivo in os.listdir(pasta_split) if arquivo.endswith('.cnv')]

            for arquivo in arquivos_cnv:
                caminho_origem = os.path.join(pasta_split, arquivo)
                primeira_letra = arquivo[0].lower()
                        
                if primeira_letra == 'd':
                    caminho_destino = os.path.join(pasta_down, arquivo)
                elif primeira_letra == 'u':
                    caminho_destino = os.path.join(pasta_up, arquivo)
                        
                shutil.move(caminho_origem, caminho_destino)
            break
        if conferir == 'n':
            break
        else:
            print('Resposta inválida. Por favor, responda com "s" para sim ou "n" para não.')

def converter_coordenadas(coordenada):
    graus, minutos, direcao = coordenada.split()
    graus = float(graus)
    minutos = float(minutos)
    decimal = graus + minutos / 60.0
    
    if direcao in ["S", "W"]:
        decimal = -decimal
        
    return decimal

def criar_arquivo_kml(nome_arquivo, lista_coordenadas, caminho_fotos):
    kml = simplekml.Kml()

    style = simplekml.Style()
    style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'

    for estacao, coordenadas in lista_coordenadas.items():
        latitude, longitude = coordenadas
        ponto = kml.newpoint(name=estacao, coords=[(longitude, latitude)])
        ponto.style = style
        
        fotos_estacao = [arquivo for arquivo in os.listdir(caminho_fotos) if arquivo.endswith(f"{estacao}.jpg") or arquivo.endswith(f"{estacao}-ts.jpg")]

        if fotos_estacao:
            description_html = etree.Element("div")
            for foto in fotos_estacao:
                caminho_foto = os.path.join(caminho_fotos, foto)
                imagem_url = "file:///" + caminho_foto.replace('\\', '/')
                img_tag = etree.Element("img", style="max-width:500px;", src=imagem_url)
                description_html.append(img_tag)
            
            ponto.description = etree.tostring(description_html, pretty_print=True, encoding="unicode")

    kml.save(nome_arquivo)

def cria_kml(pasta_processados, tabela):
    while True:
        confere = input('Deseja criar um arquivo KML? (s/n)').lower()
        if confere == 's':
            caminho_tabela = tabela
            caminho_fotos = os.path.join(pasta_processados, 'Processamento_seaplot')
            
            coordenadas_dict = {}
            with open(caminho_tabela, "r") as arquivo:
                linhas = arquivo.readlines()[1:]
                for linha in linhas:
                    campos = linha.split("\t")
                    estacao = campos[0]
                    latitude = campos[2]
                    longitude = campos[3]
                    
                    latitude_convertida = converter_coordenadas(latitude)
                    longitude_convertida = converter_coordenadas(longitude)

                    coordenadas_dict[estacao] = (latitude_convertida, longitude_convertida)
                    
            nome_kml = input('Digite o nome do seu arquivo KML: ')
            criar_arquivo_kml(os.path.join(pasta_processados, 'Relatório', nome_kml + '.kml'), coordenadas_dict, caminho_fotos)
            break
        if confere == 'n':
            break
        else:
            print('Resposta inválida. Por favor, responda com "s" para sim ou "n" para não.')

lista_print = [] #armazena as strings do relatório
def list_print(message):
    lista_print.append(message)
    print(message)
    
def list_print_custom(lst, prefix=''):
    # Use join para imprimir os elementos da lista em uma única linha
    print(prefix + '\n'.join(lst))



while True:
    
    # Verificação de processamento novo ou continuação
    continuar_processamento = input('Deseja fazer um processamento novo? (s/n)').lower()
    
    if continuar_processamento == 'n':
        # Continuação de processamento
        pasta_processados = input('Digite o caminho da pasta de dados processados:')
        pasta_copia = input('Digite o caminho da pasta em que os arquivos estão copiados: ')
        caminho_bat = os.path.join(pasta_processados, 'Batch_file')
        arquivos_na_pasta = os.listdir(caminho_bat)
        
        if len(arquivos_na_pasta) != 1 or not arquivos_na_pasta[0].endswith('.txt'):
            print('Não foi possível determinar o Batch file na pasta.')
            sys.exit()
        arquivos_hex = [arquivo for arquivo in os.listdir(pasta_copia) if arquivo.endswith('.hex')]
            
            # Dicionário para rastrear as estações e suas versões
        estacoes_versoes = defaultdict(set)

            # Expressão regular para extrair o número da estação e a versão
        expressao = r'(\d{3}[a-zA-Z]*)'  # Procura 3 dígitos seguidos por zero ou mais letras

            # Iterar pelos nomes dos arquivos .hex
        for arquivo in arquivos_hex:
                # Use a expressão regular para encontrar o número da estação e a versão
            matches = re.findall(expressao, arquivo)
            if matches:
                estacao = matches[0]
                versao = matches[1] if len(matches) > 1 else 'Versão Padrão'
                    # Adicione esta estação e versão ao dicionário
                estacoes_versoes[estacao].add(versao)
            

        bat = os.path.join(caminho_bat, arquivos_na_pasta[0])
        caminho_split = 'Processamento_split'
        pasta_split = os.path.join(pasta_processados, caminho_split)
        
        tabela = os.path.join(pasta_processados, 'Relatório',  'Tabela_de_posição.txt')
        relatorio = os.path.join(pasta_processados, 'Relatório',  'Relatório_de_dados_e_processamento.txt')

        process(bat, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes)
        split(pasta_split)
        cria_kml(pasta_processados, tabela)
        end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes)
        
        break


    elif continuar_processamento == 's':
        nome_path = input('Em que pasta estão os dados brutos? (digite o caminho da pasta)')
        pasta = Path(nome_path)

        #Novo processamento
        if pasta.exists():
            nome_copia = input('Dê nome à cópia da pasta em que você irá trabalhar: (use _ no lugar de espaços)')
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

            # Contagem de arquivos e tipos
            arquivos = glob.glob(os.path.join(pasta_copia, '*'))
            counter = len(arquivos)
            n_hex = len(list(pasta_copia.glob('*.hex')))
            n_bl = len(list(pasta_copia.glob('*.bl')))
            n_hdr = len(list(pasta_copia.glob('*.hdr')))
            n_mrk = len(list(pasta_copia.glob('*.mrk')))
            n_xmlcon = len(list(pasta_copia.glob('*.XMLCON')))
            n_con = len(list(pasta_copia.glob('*.con')))
            other = counter - (n_hex + n_bl + n_hdr + n_mrk + n_xmlcon + n_con)

            print('Sua pasta de dados processados foi criada!')
            list_print(f'Foram copiados {counter} arquivos.')
            list_print(f'Há {n_hex} arquivos do tipo HEX')
            list_print(f'{n_bl} arquivos do tipo BL')
            list_print(f'{n_hdr} arquivos do tipo HDR')
            list_print(f'{n_mrk} arquivos do tipo MRK')
            list_print(f'{n_xmlcon} arquivos do tipo XMLCON')
            list_print(f'{n_con} arquivos do tipo CON')
            
            if other > 0:
                
                # Lista para armazenar os nomes dos arquivos que não são .ros ou outros tipos específicos
                list_print(f'Há {other} outros tipos de arquivos:')
                for arquivo in arquivos:
                    extensao = Path(arquivo).suffix 
                    if extensao not in ['.hex', '.bl', '.hdr', '.mrk', '.XMLCON', '.con', '.CON']:
                        list_print(arquivo)
                        
            arquivos_hex = [arquivo for arquivo in os.listdir(pasta_copia) if arquivo.endswith('.hex')]

            # Conjunto para manter um registro único de estações
            estacoes = set()

            # Expressão regular para extrair o número da estação
            expressao = r'(\d{3})(?![a-zA-Z])'  # Procura exatamente 3 dígitos não seguidos por letras

            # Iterar pelos nomes dos arquivos .hex
            for arquivo in arquivos_hex:
                # Use a expressão regular para encontrar o número da estação
                matches = re.findall(expressao, arquivo)
                if matches:
                    for match in matches:
                        estacoes.add(match)

            # Imprimir o número de estações únicas
            print(f"O número total de estações é: {len(estacoes)}")
            
            # Dicionário para rastrear as estações e suas versões
            estacoes_versoes = defaultdict(set)

            # Expressão regular para extrair o número da estação e a versão
            expressao = r'(\d{3}[a-zA-Z]*)'  # Procura 3 dígitos seguidos por zero ou mais letras

            # Iterar pelos nomes dos arquivos .hex
            for arquivo in arquivos_hex:
                # Use a expressão regular para encontrar o número da estação e a versão
                matches = re.findall(expressao, arquivo)
                if matches:
                    estacao = matches[0]
                    versao = matches[1] if len(matches) > 1 else 'Versão Padrão'
                    # Adicione esta estação e versão ao dicionário
                    estacoes_versoes[estacao].add(versao)

            # Dicionário para rastrear os tipos de arquivo associados a cada estação e versão
            estacoes_tipos_arquivo = defaultdict(dict)
            

            # Imprimir informações sobre os tipos de arquivo para cada estação e versão
            
            estações_completas = True
            tipos_arquivos = {'.hex', '.bl', '.hdr', '.mrk'}
            tipos_faltando = set()
            arq_configu = None

            for estacao, versoes in estacoes_versoes.items():
                station_files = [f'{estacao}{ext}' for ext in tipos_arquivos]
                missing_files = [file for file in station_files if not any(file in os.path.basename(arq) for arq in arquivos)]

                # Inicialize as variáveis
                con_presente = False
                xmlcon_presente = False

                # Verifique se pelo menos um dos arquivos .con ou .XMLCON está presente na estação
                if n_con > 0:
                    con_presente = True
                    arq_configu = True
                    
                    
                elif n_xmlcon > 0:
                    xmlcon_presente = True
                    arq_configu = True
                    
                    
                else:
                    estações_completas = False
                    list_print(f'A estação {estacao} não tem arquivo de configuração')
                                    
                if missing_files:
                    estações_completas = False
                    tipos_faltando.update([Path(file).suffix for file in missing_files])
                    list_print(f'A estação {estacao} não está completa. Faltando: {", ".join(missing_files)}')

                if xmlcon_presente:
                    arq_configu =  '%1.XMLCON'
                elif con_presente:
                    arq_configu =  '%1.CON'

            if estações_completas and arq_configu != None:
                list_print('Todas as estações estão completas.')
            lista_arquivos = os.listdir(pasta_copia)


            # CRIANDO PASTA DE DADOS PROCESSADOS    
            nome_processados = input('Nomeie a sua pasta de dados processados: (use _ no lugar de espaços)')
            pasta_processados = pasta.parent / nome_processados
            os.mkdir(pasta_processados)
            nome_pasta_bat = 'Batch_file'
            caminho_bat = os.path.join(pasta_processados, nome_pasta_bat)
            nome_pasta_garrafa = 'Arquivos_BTL'
            caminho_garrafa = os.path.join(pasta_processados, nome_pasta_garrafa)
            os.makedirs(caminho_garrafa)
            caminho_split = 'Processamento_split'
            pasta_split = os.path.join(pasta_processados, caminho_split)
            os.makedirs(pasta_split)
            caminho_plot = 'Processamento_seaplot'
            pasta_plot = os.path.join(pasta_processados, caminho_plot)
            os.makedirs(pasta_plot)
            caminho_relatorio = 'Relatório'
            pasta_relatorio = os.path.join(pasta_processados, caminho_relatorio)
            os.makedirs(pasta_relatorio)
            
            # ESCREVENDO RELATÓRIO
            nome_relatorio = 'Relatório_de_dados_e_processamento.txt'
            relatorio = os.path.join(pasta_relatorio, nome_relatorio)
            nome_tabela = 'Tabela_de_posição.txt'
            tabela = os.path.join(pasta_relatorio, nome_tabela)
            with open(tabela, 'w') as arquivo_saida:
                arquivo_saida.write('Nº ESTAÇÃO\tData e Hora\tLatitude\tLongitude\n')


            with open(relatorio, 'w') as arq:
                arq.write('RELATÓRIO DE DADOS E PROCESSAMENTO\n')
                arq.write('O relatório presente fornece todas as informações obtidas a partir dos dados brutos.')
                arq.write('\nPor favor, cheque todas as informações e adicione o que achar relevante para o processamento dos dados.\n')
                for i in lista_print:
                    arq.write('\n' + i)
            
            lista_print.clear()
            
            print('Sua pasta foi criada!')
            
            bat_existe = False
            confere = str(input('Você já possui um arquivo PSA para realizar o processamento? (s/n)'))
            pasta_psa = 'Arquivos_PSA'
            caminho_psa = os.path.join(pasta_processados, pasta_psa)
            os.makedirs(caminho_psa)

            if confere == 's':
                print(f'Por favor, coloque os seus arquivos PSA na pasta Arquivos_PSA que se encontra em {nome_processados}')
                print('Confira que os arquivos PSA estão nomeados segundo a nomenclatura padrão do SBEDataProcessing')
                input('Pressione Enter após terminar...')
                
            else:
                print(f'Por favor, crie os arquivos PSA desejados e coloque-os na pasta Arquivos_PSA que se encontra em {nome_processados}')
                print('Confira que os arquivos PSA estão nomeados segundo a nomenclatura padrão do SBEDataProcessing')
                input('Pressione Enter após terminar...')
                
            # Lista todos os arquivos na pasta arq_psa
            arquivos = os.listdir(caminho_psa)
            confere_seaplot = False
            confere_teos = False


            arquivos_psa = glob.glob(os.path.join(caminho_psa, '*.psa'))
            for arquivo in arquivos_psa:
                nome_arquivo = os.path.basename(arquivo)
                termo = nome_arquivo.split('.')[-2].lower() + '.psa'  # Converte o termo para letras minúsculas
                if termo == 'alignctd.psa':
                    arq_align = arquivo
                elif termo == 'binavg.psa':
                    arq_bin = arquivo
                elif termo == 'bottlesum.psa':
                    arq_sum = arquivo
                elif termo == 'celltm.psa':
                    arq_cell = arquivo
                elif termo == 'datcnv.psa':
                    arq_dat = arquivo
                elif termo == 'derive.psa':
                    arq_derive = arquivo
                elif termo == 'deriveteos10' or termo == 'deriveteos_10.psa':
                    confere_teos = True
                    arq_teos = arquivo
                elif termo == 'filter.psa':
                    arq_filter = arquivo
                elif termo == 'loopedit.psa':
                    arq_loop = arquivo
                elif termo == 'seaplot.psa' or termo == 'seaplot_autoscale1.psa':
                    arq_sea = arquivo
                elif termo == 'seaplot_ts.psa':
                    confere_seaplot = True
                    arq_ts = arquivo
                elif termo == 'split.psa':
                    arq_split = arquivo
                elif termo == 'wildedit.psa':
                    arq_wild = arquivo
                elif termo == 'markscan.psa':
                    arq_scan = arquivo
                elif termo == 'buoyancy.psa':
                    arq_buoy = arquivo
                elif termo == 'w_filter.psa':
                    arq_wf = arquivo
                elif termo == 'section.psa':
                    arq_section = arquivo
                elif termo == 'strip.psa':
                    arq_strip = arquivo
                elif termo == 'trans.psa':
                    arq_trans = arquivo

            
            while True:
                confere_bat = input('Você já possui um Batch File para realizar esse processamento? (s/n)').lower()

                if confere_bat == 's':
                    os.makedirs(caminho_bat, exist_ok=True)  # Criar diretório Batch_file, se não existir
                    while True:
                        print('Por favor, coloque seu arquivo Batch na pasta Batch_file.')
                        print('Faça todas as modificações necessárias e pressione Enter após terminar.')
                        input('Pressione Enter para continuar...')
                        arquivos_bat = glob.glob(os.path.join(caminho_bat, '*.txt'))

                        if not arquivos_bat:
                            print('Nenhum arquivo Batch foi encontrado na pasta Batch_file.')
                            print('Certifique-se de ter colocado seu arquivo Batch lá.')
                            continue 
                        else:
                            # Se houver pelo menos um arquivo Batch, assuma que o primeiro é o arquivo personalizado
                            bat = arquivos_bat[0]
                            break
                    with open(relatorio, 'w') as arq:
                        arq.write('\nDurante o processamento foi utilizado um Batch File já existente.')
                    break

                if confere_bat == 'n':
                    nome_bat = input('Dê nome ao seu batch file (sugestão: batch_nome_do_programa): ') + '.txt'
                    bat = os.path.join(caminho_bat, nome_bat)
                    os.makedirs(caminho_bat, exist_ok=True)  # Criar diretório Batch_file, se não existir
                    name_dir = str(pasta_copia) + '//'
                    input_string = input('Quais processamentos você deseja realizar?')
                    lista_bat = cria_bat(input_string)
                    lista_nomes = proc_bat(numeros_nomes, lista_bat)

                    with open(relatorio, 'a') as arq:
                        arq.write(f'\n\nDurante o processamento foi criado um novo Batch File, chamado {nome_bat}.\n')
                        arq.write('O Batch File utilizado está configurado para realizar os seguintes processamentos:\n')
                        for i in lista_nomes:
                            arq.write('\n' + i)


                    with open(bat, 'w') as arquivo:
                        if '01' in lista_bat:
                            arquivo.write('datcnv  /i' + str(name_dir) + str(replace) + '%1.hex' + ' ' + '/p' + str(arq_dat) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + arq_configu )
                        if '02' in lista_bat:
                            arquivo.write('\nfilter  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_filter) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        if '03' in lista_bat:    
                            arquivo.write('\nalignctd  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_align)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        if '04' in lista_bat:
                            arquivo.write('\ncelltm  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_cell)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        if '05' in lista_bat:
                            arquivo.write('\nloopedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_loop) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        if '06' in lista_bat:
                            arquivo.write('\nderive  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_derive) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + arq_configu )
                            if confere_teos == True:
                                arquivo.write('\nDeriveTEOS10  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_teos) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + arq_configu )
                        if '07' in lista_bat:
                            if confere_teos == True:
                                arquivo.write('\nDeriveTEOS10  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_teos) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + arq_configu )
                        if '08' in lista_bat:
                            arquivo.write('\nbinavg  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_bin) +  ' /f' + replace + '%1.cnv' + ' /o' + str(pasta_processados))
                        if '10' in lista_bat:
                            arquivo.write('\nmarkscan /i' + str(name_dir) + str(replace) + '%1.mrk' + ' ' + '/p' + str(arq_scan) + ' /f' + replace + '%1.bsr' + ' /o' +  str(pasta_processados))
                        if '11' in lista_bat:
                            arquivo.write('\nbuoyancy  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_buoy) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        if '13' in lista_bat:
                            arquivo.write('\nwfilter  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_wf) +  ' /f' + replace + '%1.cnv' + ' /o' + str(pasta_processados))
                        if '12' in lista_bat:
                            arquivo.write('\nwildedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_wild)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        if '17' in lista_bat:
                            arquivo.write('\nsplit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_split) +  ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_split))
                        if '18' in lista_bat:
                            arquivo.write('\nstrip  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_strip)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        if '19' in lista_bat:
                            arquivo.write('\ntrans  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_trans)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                        if '20' in lista_bat:
                            arquivo.write('\nseaplot  /i' + str(pasta_split) + '//' + str('d'+replace) + '%1.cnv' + ' ' + '/p' + str(arq_sea) + ' /f' + replace + '%1.jpg' + ' /o' +  str(pasta_plot))
                            if confere_seaplot == True:
                                arquivo.write('\nseaplot  /i' + str(pasta_split) + '//' + str('d'+replace) + '%1.cnv' + ' ' + '/p' + str(arq_ts) + ' /f' + replace + '%1.jpg' + ' /o' +  str(pasta_plot))
                        if '09' in lista_bat:
                            arquivo.write('\nbottlesum  /i' + str(pasta_processados) + '//' + str(replace) + '%1.ros' + ' ' + '/p' + str(arq_sum) + ' /f' + replace + '%1.BTL' + ' /o' + str(caminho_garrafa) + ' /c' + str(name_dir + replace) + arq_configu)
                    break
                else:
                    print('Resposta inválida. Por favor, responda com "s" para sim ou "n" para não.')
                    
                    
            input('Por favor, antes de realizar o processamento, confira todas as informações no arquivo de relatório e adicione o que achar necessário. \nPressione Enter quando estiver pronto para realizar o processamento.')
            process(bat, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes)
            split(pasta_split)
            cria_kml(pasta_processados, tabela)
            end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes)


        else:
            print('A pasta indicada não existe.')
        break
    
        
    else:
        print('Resposta inválida. Por favor, responda com "s" para sim ou "n" para não.')
        verificacao_fim = input('Deseja cancelar o processo? (s/n)')
        if verificacao_fim == 's':
            print('Processamento cancelado')
            break
        
