# Nome do arquivo de texto
import os
import re
import simplekml
import matplotlib.pyplot as plt
import numpy as np



pasta_processados = input('nome do arquivo cnv')

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
            


        # Agora, o dicionário "dados_tabela" contém os valores correspondentes às variáveis


        # Nome do arquivo de saída (o novo arquivo que você quer criar)
nome_arquivo_saida = os.path.join(pasta_processados, 'Relatório', 'Tabela_de_posição.txt')
        # Abra o arquivo para escrita (isso substituirá qualquer conteúdo existente)
with open(nome_arquivo_saida, 'w') as arquivo:
            # Escreva o cabeçalho da tabela
    arquivo.write("latitude\tlongitude\tTemperature\tConductivity\n")

            # Escreva os dados
    for i in range(len(dados_tabela['latitude'])):
        linha = f"{dados_tabela['latitude'][i]}\t{dados_tabela['longitude'][i]}\t{dados_tabela['Temperature'][i]}\t\t{dados_tabela['Conductivity'][i]}\n"
        arquivo.write(linha)


print(numeros_variaveis)
print(dados_tabela)


print(f'Os novos dados foram escritos em {nome_arquivo_saida}')

latitude = dados_tabela['latitude']
longitude = dados_tabela['longitude']

kml = simplekml.Kml()

# Crie um caminho no KML usando os dados de latitude e longitude
path = kml.newlinestring(
    name="Caminho",
    description="Descrição do caminho",
    coords=list(zip(longitude, latitude))  # Lembre-se de coordenadas: (longitude, latitude)
)

# Salve o arquivo KML
nome_arquivo_saida = os.path.join(pasta_processados, 'Relatório', 'caminho.kml')
kml.save(nome_arquivo_saida)


temperatura = dados_tabela['Temperature']
condutividade = dados_tabela['Conductivity']

# Converter as strings em números de ponto flutuante
dados_tabela['Temperature'] = [float(valor) for valor in dados_tabela['Temperature']]
dados_tabela['Conductivity'] = [float(valor) for valor in dados_tabela['Conductivity']]

# Crie uma lista de tempo, supondo que cada linha seja uma medida consecutiva no tempo
tempo = list(range(len(dados_tabela['Temperature'])))

# Crie uma figura com dois subplots (um para temperatura e outro para condutividade)
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 6))

# Plote a variação da temperatura
ax1.plot(tempo, dados_tabela['Temperature'], marker='o', linestyle='-', color='b')
ax1.set_ylabel('Temperatura (°C)')
ax1.set_title('Variação de Temperatura e Condutividade')

# Plote a variação da condutividade
ax2.plot(tempo, dados_tabela['Conductivity'], marker='o', linestyle='-', color='r')
ax2.set_xlabel('Tempo')
ax2.set_ylabel('Condutividade')
ax2.set_xlim(0, len(tempo) - 1)

# Ajuste o espaço entre os subplots para evitar sobreposição de rótulos
plt.tight_layout()

# Mostre o gráfico
plt.show()



