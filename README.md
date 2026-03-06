# GCode 2D/3D Reconstructor 🖨️🔄

Um aplicativo robusto com interface gráfica (GUI) em Python para visualizar, analisar e converter arquivos GCode de impressão 3D em geometrias 2D (DXF) e modelos 3D (STL, OBJ, etc.).

Este projeto é **extremamente útil para casos em que se deseja estudar a estrutura do preenchimento interno (infill) de uma peça**, validar paredes, gerenciar suportes ou efetuar engenharia reversa de um GCode fatiado de volta para um modelo CAD.

---

## ✨ Principais Funcionalidades

- **Visualização Precisa (Preview 2D):** Renderização gráfica instantânea do GCode camada por camada, com simulação opcional das dimensões físicas do bico da impressora (Nozzle Width).
- **Filtragem de Estruturas:** Isole e visualize partes específicas da impressão:
  - `Preenchimento (Infill)`
  - `Parede Externa (Wall-Outer)`
  - `Parede Interna (Wall-Inner)`
  - `Saia e Borda (Skirt / Brim)`
  - `Suporte (Support)`
- **Exportação para DXF (2D):**
  - Exporte apenas a camada atual selecionada para um arquivo vetorial.
  - Exporte todas as camadas simultaneamente para uma pasta escolhida (gera um arquivo `.dxf` distinto para cada altura Z).
- **Exportação para Modelo 3D:**
  - Reconstrói todas as trajetórias selecionadas do GCode e as converte em um modelo 3D sólido (malha/mesh).
  - Preserva a espessura do bico e a altura da camada, ideal para verificar colapsos de preenchimento ou vazamentos no fluxo.
- **Suporte Multilíngue:** Interface disponível nativamente em Português e Inglês.

---

## 🛠️ Pré-requisitos e Dependências

O software foi desenvolvido em Python e requer algumas bibliotecas externas para funcionar corretamente. 

Certifique-se de ter o Python (versão 3.8 ou superior) instalado em seu sistema operacional e as seguintes dependências:
- `matplotlib`
- `shapely`
- `trimesh`
- `numpy`
- `ezdxf`

*(O projeto também usa bibliotecas padrão do Python como `tkinter`, `os` e `re`).*

---

## 🚀 Instalação e Execução

Existem duas formas de executar o **GCode Reconstructor**: usando o executável standalone (focado em usuários) ou via código-fonte (para desenvolvedores).

### Opção 1: Executável Standalone (Recomendado)

Se você utiliza **Windows**, pode usar o programa diretamente sem instalar dependências ou configurar ambiente virtual!
1. Baixe o arquivo `GCode-Reconstructor.exe` presente na raiz deste repositório (ou acesse a área de *Releases*).
2. Dê um duplo-clique no arquivo `.exe`.
3. A interface abrirá instantaneamente.

### Opção 2: Executar via Código-Fonte (Python)

Caso queira modificar o código, contribuir ou testar em outro sistema operacional (Linux/macOS):

**1. Clonar o repositório**
```bash
git clone https://github.com/SeuUsuario/GCode-Reconstructor.git
cd GCode-Reconstructor
```

**2. Criar e ativar um ambiente virtual**
- Windows: `python -m venv venv` ➡️ `venv\Scripts\activate`
- Linux/macOS: `python3 -m venv venv` ➡️ `source venv/bin/activate`

**3. Instalar as dependências**
```bash
pip install matplotlib shapely trimesh numpy ezdxf
```

**4. Executar o programa**
```bash
python main.py
```
*(No Windows, você também pode usar o arquivo `run.bat` para automatizar a ativação da venv e execução do App).*

---

## 📖 Mini Tutorial de Uso

Aprenda a utilizar o GCode Reconstructor com 4 passos simples:

### Passo 1: Carregar o GCode
1. Abra o aplicativo.
2. Clique no botão **"1. Carregar GCode"** (ou "1. Load GCode") localizado no painel lateral esquerdo.
3. Navegue pelas pastas do seu computador e selecione um arquivo `.gcode` previamente fatiado (no Cura, PrusaSlicer, Orca, etc.).
4. O software analisará as linhas do arquivo e atualizará a interface listando todas as alturas Z detectadas.

### Passo 2: Configurar Parâmetros
No bloco **"2. Parâmetros"**, ajuste a fidelidade da simulação do seu arquivo:
- **Largura do Bico (Nozzle Width):** Em milímetros (ex: 0.4). Usado tanto nas previsões em tela quanto nos cálculos matemáticos de modelagem.
- **Altura da Camada (Layer Height):** Em milímetros (ex: 0.2). Usado sobretudo ao criar a altura da extrusão dos modelos na exportação 3D.
- **Nozzle simulation (3D/2D):** Ao marcar esta opção, os gráficos renderizam linhas espessas condizentes com o tamanho físico da área de extrusão. Deixando desmarcado, a exibição será feita apenas do "esqueleto" e pontos de trajetória.

### Passo 3: Filtro de Linhas e Visualização de Camada
1. No bloco de exibição (Camada atual), use o controle deslizante (slider) ou clique diretamente no menu do Z (Z: xxx mm) para transitar pelas camadas.
2. Na área inferior direita estão os filtros que permitem ativar / desativar os **Tipos de Linha**. 
   - Exemplo de Uso: Caso queira focar a análise em como a espessura da estrutura interna vai se comportar, desmarque todas as caixas, exceto `FILL (Infill)`.
3. A janela principal e os botões de zoom abaixo dela permitem que você se aproxime bastante para checar se as linhas estão colidindo ou formando a geometria certa.

### Passo 4: Exportação
Satisfeito com o filtro da camada ou do arquivo todo? Utilize uma destas 3 funções:
- **Exportar Camada (DXF):** Extrai o contorno atual visualizado e monta um arquivo CAD bidimensional (DXF). Ótimo para enviar a um corte a laser acrílico validando fatias, por exemplo.
- **Exportar TUDO (Pasta DXF):** Exporta de forma silenciosa todas as alturas Z (sem precisar acessar uma por uma) diretamente para arquivos individuais em um diretório definido no seu computador.
- **Exportar Modelo 3D (Extrusão):** Uma ferramenta fantástica que converte toda as linhas filtradas do GCode atual aplicando altura e largura, permitindo extrair daquele GCode apenas o volume de impressão exato em arquivo 3D robusto.

---

## 👨‍💻 Autores
- **Autor:** Jairo Ivo Castro Brito
- **Orientador:** Bruno Vieira Bertoncini

## 🤝 Contribuições
Contribuições são bem-vindas! Se você encontrou um bug ou quer adicionar suporte a novos delimitadores ou leituras de extrusão relativas (E), fique a vontade para abrir uma *Issue* ou enviar um *Pull Request*.

## 📄 Licença
Consulte o arquivo `LICENSE` distribuído junto a este repositório para permissões relativas ao uso comercial, modificação e distribuição técnica e legal.