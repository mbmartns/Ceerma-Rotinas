def dfs_melhor_caminho(grafo, atual, destino, visitados=None, caminho=None, menor_caminho=None):
    if visitados is None:
        visitados = set()
    if caminho is None:
        caminho = []
    if menor_caminho is None:
        menor_caminho = []

    visitados.add(atual)
    caminho.append(atual)

    if atual == destino:
        if not menor_caminho or (len(caminho) < len(menor_caminho)):
            menor_caminho[:] = caminho
    else:
        for vizinho in grafo[atual]:
            if vizinho not in visitados:
                dfs_melhor_caminho(grafo, vizinho, destino, visitados.copy(), caminho, menor_caminho)
    visitados.remove(atual)
    caminho.pop()

    return menor_caminho

nomes_locais = input().split()
grafo = {}

for i in range(len(nomes_locais)):
    conexoes = input().split()[:]
    grafo[nomes_locais[i]] = [nomes_locais[int(conexao)] for conexao in conexoes]
    
origem = nomes_locais[0]
destino = nomes_locais[-1]
caminho = dfs_melhor_caminho(grafo, origem, destino)

if caminho:
    nomes_caminho = ' -> '.join(caminho)
    print(f'Grafite precisou passar por {len(caminho)} pontos através do caminho {nomes_caminho}.')
else:
    print('Infelizmente Grafite não pode chegar no Arruda.')
