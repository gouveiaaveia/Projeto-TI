import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import huffmancodec as huffc

def calcular_ocorrencias(data, alfabeto):
    # Obter o número de ocorrências para cada variável
    ocorrencias = contar_ocorrencias(data, alfabeto)

    for i, (variavel, ocor) in enumerate(ocorrencias.items()):

        ocor = np.array(ocor)
        
        # Criar gráfico de barras somente com ocorrências diferentes de 0
        valores_presentes = alfabeto[ocor > 0]  # Filtra valores presentes no alfabeto
        contagens_presentes = ocor[ocor > 0]    # Filtra as contagens diferentes de 0

        plt.bar(valores_presentes.astype(str), contagens_presentes, color="red", align="center")
        plt.xlabel(variavel)
        plt.ylabel("Contagem")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

    # Adicione o retorno das ocorrências aqui
    return ocorrencias

#Corrigir
def contar_ocorrencias(data, alfabetoGeral):
    ocorrencias_por_variavel = {}
    
    for coluna in data.columns:
        # Inicializar a contagem com 0 para cada valor do alfabeto
        contagem = {valor: 0 for valor in alfabetoGeral}
        
        # Contar a frequência de cada valor na coluna
        for valor in data[coluna]:
            if valor in contagem:
                contagem[valor] += 1
        
        # Converte as contagens em uma lista para manter a compatibilidade com o alfabeto
        ocorrencias_por_variavel[coluna] = [contagem[valor] for valor in alfabetoGeral]
    
    return ocorrencias_por_variavel

def binning(data, coluna, alfabeto, num_simbolos, ocorrencias):
    # Dividir o alfabeto em intervalos de acordo com o número de símbolos
    intervalos = np.array_split(alfabeto, len(alfabeto) // num_simbolos) 
    
    # Criar cópia da coluna para modificar com os novos valores
    nova_coluna = data[coluna].copy()
    
    for idx, valor_original in enumerate(data[coluna]):
        for intervalo in intervalos:
            if valor_original in intervalo:  # Verificar se o valor está no intervalo
                # Encontrar os índices dos valores presentes no intervalo
                indices_frequentes = np.where(np.isin(alfabeto, intervalo))[0]
                valores_frequentes = alfabeto[indices_frequentes]
                frequencias = np.array([ocorrencias[i] for i in indices_frequentes])  # Acessar frequências usando índices

                # Verificar se há frequências maiores que 0
                if np.any(frequencias > 0):
                    # Atribui o valor com maior frequência
                    valor_mais_frequente = valores_frequentes[np.argmax(frequencias)]
                    # Coloca na nova coluna o valor mais frequente
                    nova_coluna.iloc[idx] = valor_mais_frequente
                else:
                    print(f"Aviso: Nenhuma frequência positiva encontrada para o intervalo {intervalo}")
                
                break  # Sai do loop interno assim que encontrar o intervalo
        
    return nova_coluna


def calculo_medio_bits(data):

    # Calcula a entropia para cada coluna individualmente
    for coluna in data.columns:
        # conta a frequência de cada valor na coluna e normaliza (divide pelo total de ocorrencias).values retona os vaslores como um array
        valores_norm = data[coluna].value_counts(normalize=True).sort_index().values
        
        # Cálculo da entropia para a coluna
        entropia_coluna = -np.sum(valores_norm * np.log2(valores_norm))
        
        print(f"Média (entropia) para {coluna}: {round(entropia_coluna, 10)}")


    # Calcula a média total considerando todas as colunas juntas
    data_flat = data.values.flatten()

    #Contar a frequência dos valores em todas as colunas
    valores_unicos, contagem = np.unique(data_flat, return_counts=True)

    #Obter as porbabilidades
    probabilidade_total = contagem/ np.sum(contagem)

    media_total = -np.sum(probabilidade_total * np.log2(probabilidade_total))

    print(f"Média total (entropia considerando todas as colunas juntas): {round(media_total, 10)}")

    # 8 b) o valores têm que estar entre a entropia e a entropia + 1
    # 8 c) colocar os simbolos combinados na lista usando a ordem mais elevada possível

def huffmaan(data): 
    for coluna in data.columns:
        # Construir o codec de Huffman a partir dos dados da coluna
        codec = huffc.HuffmanCodec.from_data(data[coluna])
        print("Novo")
        # Obter os símbolos e comprimentos dos códigos
        symbols, lengths = codec.get_code_len() #symbols é cada numero do abcedario em cada coluna
                                                #se um simbolo tem 00 em binario a length é 2 bits
        
        # Calcular as frequências dos símbolos na coluna 
        frequencias = data[coluna].value_counts().reindex(symbols, fill_value=0).values
        # Normalizar as frequências para obter as probabilidades
        probabilidades = frequencias / np.sum(frequencias)

        # Calcular o valor médio de bits por símbolo
        L_media = np.average(lengths, weights=probabilidades)
        # Calcular a variância ponderada
        variancia_ponderada = np.average((lengths - L_media)**2, weights=probabilidades)  #tem uma formula(ver)
        print(f"Média ponderada para {coluna}: {L_media:.10f} bits")
        print(f"Variância ponderada dos comprimentos: {variancia_ponderada:.10f}\n")

    #Calcular a média total
    data_flat = data.values.flatten()
    codec = huffc.HuffmanCodec.from_data(data_flat)

    symbols, lengths = codec.get_code_len()

    valores_unicos, contagem = np.unique(data_flat, return_counts=True)
    probabilidades = contagem / np.sum(contagem)

    L_media = np.average(lengths, weights=probabilidades)
    variancia_ponderada = np.average((lengths - L_media)**2, weights=probabilidades)

    print(f"Média ponderada (total): {L_media:.10f} bits")
    print(f"Variância ponderada dos comprimentos (total): {variancia_ponderada:.10f}\n")


def correlacao_pearson(data, varNames):
    for i in range(len(varNames) - 1):
        corr = np.corrcoef(data[varNames[i]], data["MPG"])
        print(f"Correlação de Pearson entre {data.columns[i]} e MPG: {corr[0, 1]}")


def calcular_informacao_mutua(data, indice):
    # Extrair a coluna "MPG" e a coluna da variável indicada pelo índice
    mpg = data.iloc[:, -1].to_numpy()  # Última coluna para MPG
    variavel = data.iloc[:, indice].to_numpy()
    
    total = len(mpg)  # Número total de pares
    
    # Obter valores únicos e contagens para calcular as probabilidades marginais
    valores_mpg, contagem_mpg = np.unique(mpg, return_counts=True)
    valores_variavel, contagem_variavel = np.unique(variavel, return_counts=True)
    
    prob_mpg = contagem_mpg / total
    prob_variavel = contagem_variavel / total
    
    # Cria uma matriz de pares para calcular a distribuição conjunta
    pares = np.column_stack((mpg, variavel))
    valores_pares, contagem_pares = np.unique(pares, axis=0, return_counts=True)
    
    # Calcular a informação mútua
    informacao_mutua = 0
    for (val_mpg, val_var), contagem_conjunta in zip(valores_pares, contagem_pares):
        # Probabilidade conjunta do par
        prob_conjunta = contagem_conjunta / total
        
        # Índices para as probabilidades marginais
        indice_mpg = np.where(valores_mpg == val_mpg)[0][0]
        indice_variavel = np.where(valores_variavel == val_var)[0][0]
        
        prob_marginal_mpg = prob_mpg[indice_mpg]
        prob_marginal_variavel = prob_variavel[indice_variavel]
        
        # Cálculo da informação mútua para o par atual
        informacao_mutua += prob_conjunta * np.log2(prob_conjunta / (prob_marginal_mpg * prob_marginal_variavel))
    
    return informacao_mutua


def estimar_MPG(data):
    pass

def main():

    # Carregar o arquivo Excel
    exelFile = "CarDataset.xlsx"
    data = pd.read_excel(exelFile)

    varNames = data.columns.values.tolist()

    # Plotar gráficos MPG vs outras variáveis
    j = 0
    for i in range(len(varNames) - 1):
        plt.subplot(3, 2, j+1)
        plt.plot(data[varNames[i]], data["MPG"], ".m")
        plt.title(f"MPG vs {varNames[i]}")
        plt.xlabel(varNames[i])
        plt.ylabel("MPG")
        j += 1

    plt.subplots_adjust(hspace=1.4)
    plt.subplots_adjust(wspace=0.5)
    plt.show()

    # Converter dados para uint16
    data_uint16 = data.select_dtypes(include=[np.number]).astype(np.uint16)

    # Número de bits do tipo de dado (para uint16)
    num_bits = data_uint16.iloc[:, 0].dtype.itemsize * 8

    # Criar o alfabeto como um intervalo de uint16
    alfabeto_geral = np.arange(0, 2**num_bits,  dtype=np.uint16)

    # Calcular e plotar as ocorrências
    ocorrencias_por_variavel = calcular_ocorrencias(data_uint16, alfabeto_geral)

    # Aplicar binning nas colunas e salvar as colunas binned no DataFrame
    data_uint16["Weight"] = binning(data_uint16, "Weight", alfabeto_geral, 39, ocorrencias_por_variavel["Weight"])
    data_uint16["Displacement"] = binning(data_uint16, "Displacement", alfabeto_geral, 5, ocorrencias_por_variavel["Displacement"])
    data_uint16["Horsepower"] = binning(data_uint16, "Horsepower", alfabeto_geral, 5, ocorrencias_por_variavel["Horsepower"])

    # Calcular e plotar as ocorrências para os novos valores binned
    colunas_binned = ["Weight", "Displacement", "Horsepower"]
    ocorrencias_binned = calcular_ocorrencias(data_uint16[colunas_binned], alfabeto_geral)

    # Calcular a média
    calculo_medio_bits(data_uint16)
    print("\n")
    #Huffmaan
    huffmaan(data_uint16)

    #Correlação de Pearson
    correlacao_pearson(data_uint16, varNames)

    #Informação Mútua

    #Ponto 10
    print("\n")
    for i in range (len(varNames) - 1):
        valor = calcular_informacao_mutua(data_uint16, i)
        indice = varNames[i]
        print(f"Informação mútua entre MPG e {indice} : {valor}" )

if __name__ == "__main__":
    main()
