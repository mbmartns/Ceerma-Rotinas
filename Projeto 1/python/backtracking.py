def subsets_backtracking(planetas):
    def backtrack(start, subset):
        # Adicione o subset atual à lista de subsets
        subsets.append(subset[:])
        
        # Explore todas as escolhas possíveis a partir do índice 'start'
        for i in range(start, len(planetas)):
            subset.append(planetas[i])
            # Recursivamente gere subsets adicionando planetas a partir da posição 'i + 1'
            backtrack(i + 1, subset)
            # Remova o último planeta para retroceder
            subset.pop()

    subsets = []
    backtrack(0, [])
    return subsets

planetas = ['Planeta de Miller', 'Planeta de Edmunds', 'Planeta de Dr. Mann']

subsets = subsets_backtracking(planetas)
subsets.sort()  # Ordene os subsets em ordem alfabética

# Imprima o número de subsets e a lista de subsets
print(f"O número de subsets de visitação é {len(subsets)}")
print("São eles:")
for subset in subsets:
    print(subset)


O número de subsets de visitação é 8
São eles: [[], ['Planeta de Dr. Mann'], ['Planeta de Dr. Mann', 'Planeta de Edmunds'], ['Planeta de Dr. Mann', 'Planeta de Edmunds', 'Planeta de Miller'], ['Planeta de Dr. Mann', 'Planeta de Miller'], ['Planeta de Edmunds'], ['Planeta de Edmunds', 'Planeta de Miller'], ['Planeta de Miller']]

O número de subsets de visitação é 8
São eles: [[], ['Planeta de Dr. Mann'], ['Planeta de Dr. Mann', 'Planeta de Edmunds'], ['Planeta de Dr. Mann', 'Planeta de Edmunds', 'Planeta de Miller'], ['Planeta de Dr. Mann', 'Planeta de Miller'], ['Planeta de Edmunds'], ['Planeta de Edmunds', 'Planeta de Miller'], ['Planeta de Miller']]