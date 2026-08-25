# Regras do Workspace: GCode Reconstructor

## 🐍 Diretrizes de Código
- **Estilo de Código (PEP 8):** Mantenha o estilo de código consistente, utilizando nomes descritivos em `snake_case` para funções e variáveis locais, e `CamelCase` para classes.
- **Traduções (Interface Multilíngue):** Qualquer novo elemento textual adicionado à GUI deve ser cadastrado no dicionário `TRANSLATIONS` de [main.py](file:///c:/Users/jairo/OneDrive/Desktop/Projetos/GCode-Reconstructor/main.py) em ambas as chaves `'en'` (Inglês) e `'pt'` (Português).
- **Integridade da Documentação:** Não exclua comentários explicativos ou docstrings que sirvam para esclarecer nuances de processamento de GCode ou algoritmos geométricos.

## 🛠️ Modificações Geométricas
- Ao editar lógicas de geração de malhas 3D e exportadores, assegure-se de que os estilos de visualização `Line`, `Square`, `Tubular` e `Stadium` continuem operando corretamente sob resoluções variadas.
- Caso precise atualizar dependências, certifique-se de que a biblioteca continue empacotável usando PyInstaller (conforme definido em `main.spec`).
