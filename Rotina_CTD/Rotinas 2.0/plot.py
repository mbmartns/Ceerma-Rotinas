import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.lines import Line2D
from pathlib import Path
import os



def convert_latitude(latitude_str):
    degrees, minutes, hemisphere = latitude_str.split()
    degrees = float(degrees)
    minutes = float(minutes.replace('.', ''))
    
    if hemisphere.upper() == 'S':
        degrees = -degrees
    
    return degrees + minutes / 6000.0

def convert_longitude(longitude_str):
    degrees, minutes, hemisphere = longitude_str.split()
    degrees = float(degrees)
    minutes = float(minutes.replace('.', ''))
    
    if hemisphere.upper() == 'W':
        degrees = -degrees
    
    return degrees + minutes / 6000.0

def converter_coordenadas(coordenada): # muda as coordenadas que estão na tabela, mas não muda na tabela
    graus, minutos, direcao = coordenada.split()
    graus = float(graus)
    minutos = float(minutos)
    decimal = graus + minutos / 60.0
    
    if direcao in ["S", "W"]:
        decimal = -decimal
        
    return decimal


# Leia o arquivo de texto
file_path = "./Tabela_de_posição.txt"

estacao = []
latitude = []
longitude = []

        
coordenadas_dict = {}


with open(file_path, 'r') as arquivo:
    next(arquivo)

    for linha in arquivo:
        colunas = linha.strip().split(',\t')

        # Obter o número da estação, latitude e longitude
        estacao = int(colunas[0])
        
        lat = colunas[2].strip()
        long = colunas[3].strip()

        # Converter as coordenadas para graus decimais
        converted_latitude = converter_coordenadas(lat)
        converted_longitude = converter_coordenadas(long)
        # Armazenar as coordenadas no dicionário
        coordenadas_dict[estacao] = (converted_latitude, converted_longitude)

        
        # Processar a coluna de Latitude
        lat_str = colunas[2].strip()
        latitude.append(lat_str)

        # Processar a coluna de Longitude
        lon_str = colunas[3].strip()
        longitude.append(lon_str)



# Converter as latitudes e longitudes para graus decimais
converted_latitudes = [converter_coordenadas(lat) for lat in latitude]
converted_longitudes = [converter_coordenadas(lon) for lon in longitude]

# Definir as latitudes e longitudes mínimas e máximas
lat_min = min(converted_latitudes) - 2
lat_max = max(converted_latitudes) + 2
lon_min = min(converted_longitudes) - 3
lon_max = max(converted_longitudes) + 3

# Criar um mapa usando a biblioteca Basemap com as latitudes e longitudes convertidas
m = Basemap(
    projection='merc',
    llcrnrlat=min(converted_latitudes) - 2,
    urcrnrlat=max(converted_latitudes) + 2,
    llcrnrlon=min(converted_longitudes) - 3,
    urcrnrlon=max(converted_longitudes) + 3,
    resolution='l'
)

# Criar uma figura e um eixo para o mapa
fig, ax2 = plt.subplots(figsize=(15, 10))

# Definir a cor do oceano como azul e a cor da terra como cinza
m.drawmapboundary(fill_color='#99CCFF')
m.fillcontinents(color='lightgrey', lake_color='#99CCFF')

# Desenhar a costa e os limites do mapa
m.drawcoastlines()
m.drawcountries()

# Adicionar estilo de linha para cada meridiano
parallels = range(int(lat_min), int(lat_max) + 1)
meridians = range(int(lon_min), int(lon_max) + 1)
m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10, linewidth=1)
m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10, linewidth=1)
    


# Plotar os pontos no mapa com base nas coordenadas das estações
for estacao, coordenadas in coordenadas_dict.items():
    latitude, longitude = coordenadas
    x, y = m(longitude, latitude)
    m.plot(x, y, 'ro', markersize=5)

    #plt.text((x + x_offset), y + x_offset, str(estacao), color='black', fontsize=12, verticalalignment='bottom', horizontalalignment='right')
    #plt.text(x, y, str(estacao), color='red', fontsize=12, verticalalignment='bottom', horizontalalignment='right', ha='right', va='bottom')
    x_offset = 3500  # Ajuste o valor conforme necessário
    ax2.annotate(str(estacao), xy=(x + x_offset, y), xytext=(x + x_offset, y),
                color='black', fontsize=12,
                ha='left', va='bottom')
                #arrowprops=dict(arrowstyle="->", color='red'))
                

# Adicionar rótulos de paralelos e meridianos
parallels = range(int(lat_min), int(lat_max) + 1)
meridians = range(int(lon_min), int(lon_max) + 1)
m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10, linewidth=0.5)
m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10, linewidth=0.5)

    # Adicionar título e legendas
map_name = input('Digite o nome do seu mapa: ')
ax2.set_title(map_name)


ax2.legend()
# Adicionar legenda
# Plotar um ponto vermelho

# Criar um marcador personalizado para a legenda
marker = Line2D([0], [0], marker='o', color='red', linestyle='None', label='Estações')

# Adicionar o marcador personalizado à legenda
ax2.legend(handles=[marker], loc='upper right')

plt.savefig(os.path.join(r'C:\Users\Bia\Desktop\PROCESS_CTD\Processados\Relatório\\' + map_name + '.png'), dpi=300)

# Exibir o mapa
plt.show()    

