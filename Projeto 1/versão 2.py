from pathlib import Path
from pathlib import *
import glob
import os
import shutil


#pasta = str(input('Copie o endereço da pasta aqui: '))

#print(str(pasta))
#C:\Users\Bia\Desktop\CTD_Dados_Brutos-20230423T021151Z-001
pasta = r'C:\Users\Bia\Desktop\CTD_Dados_Brutos-20230423T021151Z-001'
os.chdir(pasta)
#dados = Path(pasta)

dados = Path(r'C:\Users\Bia\Desktop\CTD_Dados_Brutos-20230421T142953Z-001')
#print(dados)
# C:\Users\Bia\Downloads\CTD_Dados_Brutos-20230421T142953Z-001

arquivos = list(dados.glob("*.*"))

# renomeando e copiand diretório

if(os.path.exists('CTD_Dados_Brutos')):
    os.rename('CTD_Dados_Brutos', 'CTD_LACN_2019_ORIGINAL')
    
scr = '/scr/CTD_LACN_2019_ORIGINAL'
dest = '/dest/CTD_LACN_2019'
shutil.copy2(scr, dest)
    
#shutil.copy2('CTD_LACN_2019_ORIGINAL', 'CTD_Dados_Brutos-20230421T142953Z-001\CTD_LACN_2019')


#renomeando todos os arquivos

#dir = repr(pasta)[1:-1]
dir = r'C:\Users\Bia\Desktop\CTD_Dados_Brutos-20230421T142953Z-001'
for file in os.listdir(dir):
    tipo_arq = file.split('_')[-1]
    old_name = dir + file
    new_name = dir +  'LACN.' + tipo_arq
    #print(tipo_arq)
   # os.rename(old_name, new_name)

#definindo os tipos de arquivo


bl_files = Path(r'C:\Users\Bia\Desktop\CTD_Dados_Brutos').glob('*.bl')
hdr_files = dados.glob('*.hdr')
hex_files = dados.glob('*.hex')
mrk_files = dados.glob('*.mrk')
xmlcon_files = dados.glob('*.XMLCON')

#contando quantidade de cada arquivo

n_bl = 0
n_hdr = 0
n_hex = 0
n_mrk = 0
n_xmlcon = 0

for n in bl_files:
    n_bl += 1
for n in hdr_files:
    n_hdr += 1
for n in hex_files:
    n_hex += 1
for n in mrk_files:
    n_mrk += 1  
for n in xmlcon_files:
    n_xmlcon += 1
    
#verificando erros nos dados
    
erro = False

if n_bl == n_hdr == n_hex == n_mrk == n_xmlcon:
    print('Todas as informações estão completas')
else:
    print('Está faltando alguma informação')
    erro = True