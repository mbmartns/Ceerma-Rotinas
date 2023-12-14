import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

# Load data
station = "./Tabela_de_posição.txt"
st = pd.read_csv(
    station,
    delimiter=",",
    names=["Nº ESTAÇÃO", "Data e Hora", "Latitude", "Longitude"],
    skiprows=1,
    header=None,
    skipinitialspace=True,
    encoding='utf-8'

)

# Calculate map boundaries based on latitude and longitude
lon_min = st["Longitude"].apply(lambda x: float(x.split()[0])).min()
lon_max = st["Longitude"].apply(lambda x: float(x.split()[0])).max()
lat_min = st["Latitude"].apply(lambda x: float(x.split()[0])).min()
lat_max = st["Latitude"].apply(lambda x: float(x.split()[0])).max()

# Setup stereographic basemap with calculated boundaries
m = Basemap(
    width=15000000, height=10000000,
    resolution='l', projection='stere',
    lat_ts=80, lat_0=-55, lon_0=-60.,
    llcrnrlon=lon_min - 1, urcrnrlon=lon_max + 1,
    llcrnrlat=lat_min - 1, urcrnrlat=lat_max + 1
)

m.drawmeridians(np.arange(0, 360, 10), labels=[0, 0, 0, 1], fontweight="bold")
m.drawparallels(np.arange(-90, -40, 5), labels=[1, 0, 0, 0], fontweight="bold")
m.drawcoastlines()
m.drawcountries()

# ETOPO
m.etopo(scale=0.5, alpha=0.5)
m.shadedrelief()

# Map (long, lat) to (x, y) for plotting
x, y = m(st["Longitude"].apply(lambda x: float(x.split()[0])),
          st["Latitude"].apply(lambda x: float(x.split()[0])))

x1, y1 = m(st["Longitude"].apply(lambda x: float(x.split()[0])).iloc[0],
            st["Latitude"].apply(lambda x: float(x.split()[0])).iloc[0])

plt.plot(x, y, 'ok', markersize=10)
plt.text(x1, y1, ' Punta Arenas', fontsize=12, fontweight="bold")
plt.plot(x, y, 'bo') # plot x and y using blue circle markers

for i in range(1, len(st)):
    lon1, lat1 = m(st["Longitude"].apply(lambda x: float(x.split()[0])).iloc[i-1],
                   st["Latitude"].apply(lambda x: float(x.split()[0])).iloc[i-1])
    lon2, lat2 = m(st["Longitude"].apply(lambda x: float(x.split()[0])).iloc[i],
                   st["Latitude"].apply(lambda x: float(x.split()[0])).iloc[i])
    plt.plot([lon1, lon2], [lat1, lat2], "-", linewidth=4, color='red')

plt.title("MEPHYSTO OP42 Drake - Microplásticos", fontsize=10, fontweight="bold")
plt.savefig('./drake_plastico.png', dpi=300)