def obter_numero_scan(arq_mrk):
    # Encontrar a posição da linha contendo "mark number 1"
    
        # Lê o arquivo em um DataFrame usando pandas
    df = pd.read_csv(arq_mrk, skiprows=2, delimiter=r'\s*,\s*', engine='python')

    # Extrai o valor do "Scan" do primeiro conjunto de dados (Mark number 1)
    scan_mark_number_1 = df.loc[df['mark'] == 1, 'Scan'].values[0]

    # Imprime o valor encontrado
    print(f'O valor do "Scan" no Mark number 1 é: {scan_mark_number_1}')

    indice_mark = conteudo.find('mark number 1')

    # Se "mark number 1" não for encontrado, retornar None
    if indice_mark == -1:
        return None

    # Procurar a posição da próxima linha após "mark number 1"
    indice_linha_seguinte = conteudo.find('\n', indice_mark)

    # Se não encontrar a próxima linha, retornar None
    if indice_linha_seguinte == -1:
        return None

    # Obter a próxima linha após "mark number 1"
    linha_seguinte = conteudo[indice_mark:indice_linha_seguinte].lower()

    # Procurar o valor associado à coluna "Scan" na próxima linha
    match = re.search(r'scan\D*(\d+)', linha_seguinte)

    # Se não encontrar um número, retornar None
    if not match:
        return None

    # Retornar o número encontrado
    return match.group(1)






















def obter_numero_scan(arq_mrk):
    # Lê o arquivo em um DataFrame usando pandas
    df = pd.read_csv(arq_mrk, skiprows=2, delimiter=r'\s*,\s*', engine='python')

    # Procura diretamente pela string "mark number 1" no início de cada linha
    linha_mark_number_1 = df[df.apply(lambda row: 'mark number 1' in str(row).lower(), axis=1)]
    print(linha_mark_number_1)
    # Verifica se a linha foi encontrada
    if linha_mark_number_1.empty:
        print('A linha correspondente a "Mark number 1" não foi encontrada no DataFrame.')
        return None

    # Obtém o índice da linha Mark number 1
    indice_mark_number_1 = linha_mark_number_1.index[0]
    print(indice_mark_number_1)

    # Converte o índice para um valor inteiro
    #indice_mark_number_1 = indice_mark_number_1.item()

    # Verifica se há uma próxima linha
    if indice_mark_number_1 + 1 < len(df):
        # Extrai o valor da coluna 'Scan' da linha seguinte (onde os números estão)
        scan_mark_number_1 = df.loc[indice_mark_number_1 + 1, 'Scan']

        # Verifica se o valor de Scan foi encontrado
        if not pd.isna(scan_mark_number_1):
            # Imprime o valor encontrado
            print(f'O valor do "Scan" no Mark number 1 é: {scan_mark_number_1}')
            return scan_mark_number_1
        else:
            print('O valor do "Scan" não foi encontrado na linha seguinte.')
            return None
    else:
        print('Não há uma linha seguinte após "Mark number 1".')
        return None


