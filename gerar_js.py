import pandas as pd
import json

# 1. Lê o seu Excel (O nome da aba padrão do Excel geralmente é 'Sheet1', mude se necessário)
df = pd.read_excel('categorias.xlsx', sheet_name='Sheet1')

# Garante que não tem espaços vazios atrapalhando
df = df.dropna()

# 2. Agrupa todas as subcategorias debaixo de cada categoria
agrupado = df.groupby('Categoria')['Subcategoria'].apply(lambda x: x.tolist()).to_dict()

# 3. Transforma o dicionário do Python em texto de JavaScript bonitinho
# O ensure_ascii=False garante que acentos (Alimentação) fiquem corretos
js_code = "const subcategoriasPorCategoria = " + json.dumps(agrupado, ensure_ascii=False, indent=4) + ";"

# 4. Mostra o resultado na tela para você copiar
print("--- COPIE O TEXTO ABAIXO E COLE NO SEU HTML ---\n")
print(js_code)