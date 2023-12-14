from pathlib import Path
from pathlib import *
import glob

caminho = Path()
# print(caminho.absolute())

caminho = Path(__file__)
# print(caminho)

ideia = caminho.parent / 'ideia.txt'
ideia.touch()
#print(ideia)
ideia.write_text('O mundo é belo!')
# print(ideia.read_text())


# for i in range(n_de_arquivos):
    # file = files / f'file_{i}.txt' ou '.blablabla' 
    # mas isso tá CRIANDO, no caso, eu quero renomear!
#arquivos = os.listdir(r"C:\Users\Bia\Downloads\CTD_Dados_Brutos-20230421T142953Z-001\CTD_Dados_Brutos")
#r'C:\Users\Bia\Downloads\CTD_Dados_Brutos-20230421T142953Z-001'
  
n_bl = 0
n_hdr = 0
n_hex = 0
n_mrk = 0
n_xmlcon = 0

import os 
#"C:\Users\Bia\Downloads\CTD_Dados_Brutos-20230421T142953Z-001\CTD_Dados_Brutos"
#endereco_arquivo = input('Escreva o endereço do arquivo: ')
dados = Path(r'C:\Users\Bia\Downloads\CTD_Dados_Brutos-20230421T142953Z-001\CTD_Dados_Brutos\\')
print(dados)

arquivos = list(dados.glob("*.*"))
#print(arquivos)


bl_files = dados.glob('*.bl')
hdr_files = dados.glob('*.hdr')
hex_files = dados.glob('*.hex')
mrk_files = dados.glob('*.mrk')
xmlcon_files = dados.glob('*.XMLCON')

bl_files

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
    
erro = False

if n_bl == n_hdr == n_hex == n_mrk == n_xmlcon:
    print('Todas as informações estão completas')
else:
    print('Está faltando alguma informação')
    erro = True
 
#if erro == True: #vamos descobrir onde está o erro
    # quero que printe qual é o "pacote" om informação a menos, no caso, o 60 e diga qual tipo de arquivo que falta



print(n_bl)
print(n_hdr)
print(n_hex)
print(n_mrk)
print(n_xmlcon)

#arquivos = os.listdir(dados)

for file in arquivos:
    #print(file) # printar tudo o que tem na pasta
    #if (file[-1] == 'bl'):
       # print('yes')
       # n_bl += 1
    if file == hdr_files:
        n_hdr += 1
    if file == hex_files:
        n_hex += 1
    if file == mrk_files:
        n_mrk += 1
    if file == xmlcon_files:
        n_xmlcon += 1

#renomear

dir = r'C:\Users\Bia\Downloads\CTD_Dados_Brutos-20230421T142953Z-001\CTD_Dados_Brutos\\'

for file in os.listdir(dir):
    tipo_arq = file.split('_')[-1]
    old_name = dir + file
    new_name = dir +  'LACN_2019_' + tipo_arq
    #print(tipo_arq)
    os.rename(old_name, new_name)

#print(os.listdir(dir))
        
# agora quero comparar para ver se os dados de cada dia contem as mesmas quantidades de informações

# dados = Path(r"C:\Users\Bia\Downloads\CTD_Dados_Brutos-20230421T142953Z-001\CTD_Dados_Brutos")
# for file in dados:
    # print(file)


