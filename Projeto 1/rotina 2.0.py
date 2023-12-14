from pathlib import Path
import glob
import shutil
import subprocess
import os

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

def rename_files(source_dir, destination_dir, new_prefix):
    files = os.listdir(source_dir)
    for file in files:
        old_path = os.path.join(source_dir, file)
        new_file_name = file.replace('/', '_')  # Substituir barras por sublinhados
        new_path = os.path.join(destination_dir, new_prefix + new_file_name)
        os.rename(old_path, new_path)
        
def process(bat):
    input_string = input('Em quais estações irá processar os dados? (Escreva uma lista com 3 dígitos. Ex.: 001-010, 020)')
    input_list = process_range(input_string)

    for num in input_list:
        cmd = ('sbebatch ' + str(bat) + ' ' + num)                
        os.system(cmd)

def end(bat, pasta_split):
    terminar = input('Deseja terminar o processamento? (s/n)').lower()
    if terminar == 's':
        print('Processamento concluído!')
    else:
        process(bat)
        split(pasta_split)
        end(bat, pasta_split)
        
def split(pasta_split):
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
        process(bat)
        split(pasta_split)
        end(bat, pasta_split)


    else:
        nome_path = input('Em que pasta estão os dados? (digite o caminho da pasta)')
        pasta = Path(nome_path)
        #arquivos = glob.glob(os.path.join(pasta, '*'))
        #Novo processamento
        if pasta.exists():
            nome_copia = input('Dê nome à pasta que você quer trabalhar: (use _ no lugar de espaços)')
            pasta_copia = pasta.parent / (nome_copia + '//')
            shutil.copytree(pasta, pasta_copia)
            
        # RENOMEANDO OS ARQUIVOS 
            lista_arquivos = os.listdir(pasta_copia)
            replace = input('Como gostaria de renomear os arquivos? (termine com _ )')
            for file in lista_arquivos:
                nome = file.split('_')[0]
                tipo_arq = file.split('_')[-1]
                name_dir = str(pasta_copia) + '//'
                old_name = name_dir + file
                new_name = name_dir + replace + tipo_arq
                os.rename(old_name, new_name)


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
            print(f'Foram copiados {counter} arquivos')
            print(f'Há {n_hex} arquivos do tipo HEX')
            print(f'{n_bl} arquivos do tipo BL')
            print(f'{n_hdr} arquivos do tipo HDR')
            print(f'{n_mrk} arquivos do tipo MRK')
            print(f'{n_xmlcon} arquivos do tipo XMLCON')
            
            if other > 0:
                # Lista para armazenar os nomes dos arquivos que não são .ros ou outros tipos específicos
                print(f'Há {other} outros arquivos:')
                #print('Tipos de arquivos em "outros":')
                for arquivo in arquivos:
                    extensao = Path(arquivo).suffix
                    if extensao not in ['.hex', '.bl', '.hdr', '.mrk', '.XMLCON']:
                        if extensao == ".ros":
                            arquivo_ros = arquivo
                           # print(f'o aqeuivo ros é {arquivo_ros}')
                        print(arquivo)

              #  for file_type in set([Path(file).suffix for file in arquivos]):
               #     if file_type not in ['.hex', '.bl', '.hdr', '.mrk', '.XMLCON']:
                #        print(file_type)
                        
           # print(arquivos)
                
        # Contagem de estações
            n_estacoes = n_hex
            print(f'Há um total de {n_estacoes} estações.')

            # Verificação de estações completas
            estações_completas = True
            tipos_arquivos = {'.hex', '.bl', '.hdr', '.mrk', '.XMLCON'}
            tipos_faltando = set()
            for station in range(1, n_estacoes + 1):
                station_files = [f'{station:03d}{ext}' for ext in tipos_arquivos]
                missing_files = [file for file in station_files if not any(file in os.path.basename(arq) for arq in arquivos)]
                if missing_files:
                    estações_completas = False
                    tipos_faltando.update([Path(file).suffix for file in missing_files])
                    print(f'A estação {station:03d} não está completa. Faltando: {", ".join(missing_files)}')

            if estações_completas:
                print('Todas as estações estão completas.')
            #else:
               # print(f'Estações com tipos de arquivo faltando: {", ".join(tipos_faltando)}')
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
            
            print('Sua pasta foi criada!')
            
            # CRIANDO BATCH FILE (**CONFERIR SE JÁ EXISTE)
            bat_existe = False
            confere = str(input('Você já possui um arquivo PSA para realizar o processamento? (s/n)'))
            if confere == 's':
                pasta_psa = 'Arquivos_PSA'
                caminho_psa = os.path.join(pasta_processados, pasta_psa)
                os.makedirs(caminho_psa)
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

            arquivos_psa = glob.glob(os.path.join(caminho_psa, '*.psa'))
            for arquivo in arquivos_psa:
                nome_arquivo = os.path.basename(arquivo)
                termo = nome_arquivo.split('.')[-2] + '.psa' # Extrai o termo antes da extensão .psa
                if termo == 'AlignCTD.psa':
                    arq_align = arquivo
                elif termo == 'BinAvg.psa':
                    arq_bin = arquivo
                elif termo == 'BottleSum.psa':
                    arq_sum = arquivo
                elif termo == 'CellTM.psa':
                    arq_cell = arquivo
                elif termo == 'DatCnv.psa':
                    arq_dat = arquivo
                elif termo == 'Derive.psa':
                    arq_derive = arquivo
                elif termo == 'Filter.psa':
                    arq_filter = arquivo
                elif termo == 'LoopEdit.psa':
                    arq_loop = arquivo
                elif termo == 'SeaPlot.psa':
                    arq_sea = arquivo
                elif termo == 'Split.psa':
                    arq_split = arquivo
                elif termo == 'WildEdit.psa':
                    arq_wild = arquivo
                
            confere_bat = input('Você já possui um Batch File para realizar esse processamento? (s/n)')
            if confere_bat == 's':
                os.makedirs(caminho_bat, exist_ok=True)  # Criar diretório Batch_file, se não existir
                print('Por favor, coloque seu Batch File na pasta Batch_file.\n Faça todas as modificações necessárias \nPressione enter após terminar.')
            else:
                nome_bat = input('Dê nome ao seu batch file (sugestão: batch_nome_do_programa): ') + '.txt'
                bat = os.path.join(caminho_bat, nome_bat)
                os.makedirs(caminho_bat, exist_ok=True)  # Criar diretório Batch_file, se não existir
                name_dir = str(pasta_copia) + '//'
                with open(bat, 'w') as arquivo:
                arquivo.write('datcnv  /i' + str(name_dir) + str(replace) + '%1.hex' + ' ' + '/p' + str(arq_dat) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + '%1.XMLCON' )
                arquivo.write('\nfilter  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_filter) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                arquivo.write('\nalignctd  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_align)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    arquivo.write('\ncelltm  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_cell)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    arquivo.write('\nloopedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_loop) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    arquivo.write('\nderive  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_derive) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + '%1.XMLCON' )
                    arquivo.write('\nbinavg  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_bin) +  ' /f' + replace + '%1.cnv' + ' /o' + str(pasta_processados))
                    #Win32\BottleSum.psa   lacn_024.btl Bottlesum fPIRA_%1.BTL
                    arquivo.write('\nbottlesum  /i' + str(pasta_processados) + '//' + str(replace) + '%1.ros' + ' ' + '/p' + str(arq_sum) + ' /f' + replace + '%1.BTL' + ' /o' + str(caminho_garrafa) + ' /c' + str(name_dir + replace) + '%1.XMLCON')
                    #Win32\WildEdit.psa 12
                    arquivo.write('\nwildedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_wild)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    #Win32\Split.psa 17
                    arquivo.write('\nsplit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_split) +  ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_split))
                    #Win32\SeaPlot.psa 20
                    arquivo.write('\nseaplot  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_sea) + ' /f' + replace + '%1.jpg' + ' /o' +  str(pasta_plot))


                
            else:
                usuario = input('Qual o nome do usuário do PC?')
                #arq_psa = r'C:\Users' + '\\\\' + usuario + '\AppData\Local\Sea-Bird\SBEDataProcessing-Win32\\\\'
                #arq_seaplot = r'C:\Users' + '\\\\' + usuario + '\Application Data\Sea-Bird\SBEDataProcessing-Win32\SeaPlot.psa\\\\'
                pasta_psa = 'Arquivos_PSA'
                caminho_psa = os.path.join(pasta_processados, pasta_psa)
                os.makedirs(caminho_psa)
                print(f'Por favor, crie e coloque os seus arquivos PSA dentro da pasta Arquivos_PSA que se encontra em {nome_processados}')
                print('Para esse processamento, serão necessários 11 arquivos PSA: DatCnv.psa, Filter.psa, AlignCTD.psa, CellTM.psa. LoopEdit.psa, Derive.psa, BinAvg.psa,\n BottleSum.psa, WildEdit.psa, Split.psa, SeaPlot.psa')
                input('Certifique-se que foram criados todos os PSA e pressione Enter após ter colocado os arquivos na pasta...')

                arq_psa = r'C:\Users\\' + usuario + '\AppData\Local\Sea-Bird\SBEDataProcessing-Win32\\'

                # Lista todos os arquivos na pasta arq_psa
                arquivos = os.listdir(arq_psa)

                # Copia cada arquivo para a pasta de destino
                for arquivo in arquivos:
                    caminho_origem = os.path.join(arq_psa, arquivo)
                    caminho_destino = os.path.join(caminho_psa, arquivo)
                    shutil.copy2(caminho_origem, caminho_destino)
                input('Por favor, copie o PSA do SeaPlot para a pasta de Arquivos_PSA e pressione enter')
                

                arquivos_psa = glob.glob(os.path.join(caminho_psa, '*.psa'))
                caminhos = {}
                for arquivo in arquivos_psa:
                    nome_arquivo = os.path.basename(arquivo)
                    termo = nome_arquivo.split('.')[-2] + '.psa' # Extrai o termo antes da extensão .psa
                    if termo == 'AlignCTD.psa':
                        arq_align = arquivo
                    elif termo == 'BinAvg.psa':
                        arq_bin = arquivo
                    elif termo == 'BottleSum.psa':
                        arq_sum = arquivo
                    elif termo == 'CellTM.psa':
                        arq_cell = arquivo
                    elif termo == 'DatCnv.psa':
                        arq_dat = arquivo
                    elif termo == 'Derive.psa':
                        arq_derive = arquivo
                    elif termo == 'Filter.psa':
                        arq_filter = arquivo
                    elif termo == 'LoopEdit.psa':
                        arq_loop = arquivo
                    elif termo == 'SeaPlot.psa':
                        arq_sea = arquivo
                    elif termo == 'Split.psa':
                        arq_split = arquivo
                    elif termo == 'WildEdit.psa':
                        arq_wild = arquivo
                
                        
                nome_bat = input('Dê nome ao seu batch file (sugestão: batch_nome_do_programa): ') + '.txt'
                bat = os.path.join(caminho_bat, nome_bat)
                os.makedirs(caminho_bat, exist_ok=True)  # Criar diretório Batch_file, se não existir
                name_dir = str(pasta_copia) + '//'
                with open(bat, 'w') as arquivo:
                    arquivo.write('datcnv  /i' + str(name_dir) + str(replace) + '%1.hex' + ' ' + '/p' + str(arq_dat) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + '%1.XMLCON' )
                    arquivo.write('\nfilter  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_filter) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    arquivo.write('\nalignctd  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_align)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    arquivo.write('\ncelltm  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_cell)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    arquivo.write('\nloopedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_loop) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    arquivo.write('\nderive  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_derive) + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + '%1.XMLCON' )
                    arquivo.write('\nbinavg  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_bin) +  ' /f' + replace + '%1.cnv' + ' /o' + str(pasta_processados))
                    #Win32\BottleSum.psa   lacn_024.btl Bottlesum fPIRA_%1.BTL
                    arquivo.write('\nbottlesum  /i' + str(pasta_processados) + '//' + str(replace) + '%1.ros'  + ' ' + '/p' + str(arq_sum) + ' /f' + replace + '%1.BTL' + ' /o' + str(caminho_garrafa) + ' /c' + str(name_dir + replace) + '%1.XMLCON')
                    #Win32\WildEdit.psa 12
                    arquivo.write('\nwildedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_wild)  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
                    #Win32\Split.psa 17
                    arquivo.write('\nsplit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_split) +  ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_split))
                    #Win32\SeaPlot.psa 20
                    arquivo.write('\nseaplot  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(arq_sea) + ' /f' + replace + '%1.jpg' + ' /o' +  str(pasta_plot))


                    
            process(bat)
            split(pasta_split)
            end(bat, pasta_split)


        else:
            print('A pasta indicada não existe.')




        

if __name__ == "__main__":
    main()
