import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cartopy
import cartopy.crs as ccrs

# Positions
station = ("./almirantado_filtragens.csv")
st = pd.read_csv(station, names=["station","latitude", "longitude"], header=0)
lat_ida = st['latitude'].values[0:6]
long_ida = st['longitude'].values[0:6]
lat_volta = st['latitude'].values[6:12]
long_volta = st['longitude'].values[6:12]
lat_nict = st['latitude'].values[12]
long_nict = st['longitude'].values[12]
print(st[0:6])
print(st[6:12])

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.coastlines(resolution='10m', color='gray')
ax.add_feature(cartopy.feature.LAND, facecolor='lightgray')
ax.add_feature(cartopy.feature.OCEAN, facecolor='#99CCFF')

ax.set_extent([-62.40, -62.0, -58.75, -58.0], crs=ccrs.PlateCarree())

ax.plot(long_ida, lat_ida, 'ro', markersize=3, transform=ccrs.PlateCarree(), label="1ª rodada")
ax.plot(long_volta, lat_volta, 'bo', markersize=3, transform=ccrs.PlateCarree(), label="2ª rodada")
ax.plot(long_nict, lat_nict, 'yo', markersize=3, transform=ccrs.PlateCarree(), label="Nictemeral")

ax.text(-58.4, -62.35, "Estreito de Bransfield", transform=ccrs.PlateCarree(), fontsize=20, fontweight='bold')
ax.text(-58.58, -62.14, "B. Almirantado", transform=ccrs.PlateCarree(), fontsize=18, fontweight='bold')

ax.plot(-58.39, -62.09, 'ko', markersize=2, transform=ccrs.PlateCarree())
ax.text(-58.36, -62.09, "EACF", transform=ccrs.PlateCarree(), fontsize=10, fontweight='bold')

ax.legend(loc='upper right')

plt.savefig('./almirantado_filtragens.png', dpi=300)
plt.show()

