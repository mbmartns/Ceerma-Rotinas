from pathlib import Path
from pathlib import *
import glob
import os 



dados = Path(r'C:\Users\Bia\Desktop\CTD_Dados_Brutos-20230421T142953Z-001\CTD_Dados_Brutos\\')
print(dados)
arquivos = list(dados.glob("*.*"))

#renomeando todos os arquivos

dir = r'C:\Users\Bia\Desktop\CTD_Dados_Brutos-20230421T142953Z-001\CTD_Dados_Brutos\\'
for file in os.listdir(dir):
    tipo_arq = file.split('_')[-1]
    old_name = dir + file
    new_name = dir +  'lacn_2019_' + tipo_arq
    #print(tipo_arq)
    os.rename(old_name, new_name)

#definindo os tipos de arquivo

bl_files = dados.glob('*.bl')
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
 
#if erro == True: #vamos descobrir onde está o erro
    # quero que printe qual é o "pacote" om informação a menos, no caso, o 60 e diga qual tipo de arquivo que falta


#arquivos = os.listdir(dados)

#teste
#for file in arquivos:
    #print(file) # printar tudo o que tem na pasta
    #if (file[-1] == 'bl'):
       # print('yes')
       # n_bl += 1
    #if file == hdr_files:
     #   n_hdr += 1
   # if file == hex_files:
    #    n_hex += 1
  #  if file == mrk_files:
    #    n_mrk += 1
   # if file == xmlcon_files:
     #   n_xmlcon += 1
     
# compactando os mesmos pacotes

for file in os.listdir(dir):
    tipo_arq = file.split('_')[-1]
    num_arq = tipo_arq.split('.')[0]
    prima = '001'
    pacote = dados.glob('*_' + prima + '.*')
    #if file in os.listdir(pacote):
       # print(file)
    #print(pacote)
    if num_arq == '001':
        pasta = '0'
    #if num_arq in file:
    #print(file)
 
#for file in arquivos:
   # print(file)
#pacote = dados.glob('*_' + '001' + '.*')
#lista_pacote = list(pacote)
#print(lista_pacote)