# GCode 2D/3D Reconstructor 🖨️🔄

[Read in English](#english) | [Leia em Português](#português)

---

<h2 id="english">🇬🇧 English</h2>

A robust Python GUI application to visualize, analyze, and convert 3D printing GCode files into 2D geometries (DXF) and 3D models (STL, OBJ, etc.).

This project is **extremely useful when you want to study the internal infill structure of a part**, validate walls, manage supports, or reverse-engineer a sliced GCode back into a CAD model.

### ✨ Key Features

- **Accurate Visualization (2D Preview):** Instant graphical rendering of GCode layer by layer, with optional physical simulation of the printer's nozzle width.
- **Structure Filtering:** Isolate and visualize specific parts of the print:
  - `FILL (Infill)`
  - `WALL-OUTER`
  - `WALL-INNER`
  - `SKIRT / BRIM`
  - `SUPPORT`
- **DXF (2D) Export:**
  - Export only the currently selected layer to a vector file.
  - Export all layers simultaneously to a chosen folder (generates a distinct `.dxf` file for each Z height).
- **3D Model Export:**
  - Reconstructs all selected GCode paths and converts them into a solid 3D model (mesh).
  - Preserves nozzle width and layer height, ideal for checking infill collapses or flow leakage.
- **Multilingual Support:** Interface available natively in Portuguese and English.

### 🛠️ Prerequisites & Dependencies

The software was developed in Python and requires standard Python libraries (`tkinter`, `os`, `re`) as well as a few external libraries. Ensure you have Python (3.8+) installed:
- `matplotlib`
- `shapely`
- `trimesh`
- `numpy`
- `ezdxf`

### 🚀 Installation & Execution

There are two ways to run the **GCode Reconstructor**: using the standalone executable (user-focused) or via source code (for developers).

#### Option 1: Standalone Executable (Recommended)
If you use **Windows**, you can run the program directly without installing dependencies or setting up a virtual environment!
1. Download the `GCode-Reconstructor.exe` file present in the root of this repository (or access the *Releases* area).
2. Double-click the `.exe` file.
3. The interface will open instantly.

#### Option 2: Run via Source Code (Python)
If you want to modify the code, contribute, or test on another OS (Linux/macOS):

**1. Clone the repository**
```bash
git clone https://github.com/SeuUsuario/GCode-Reconstructor.git
cd GCode-Reconstructor
```

**2. Create and activate a virtual environment**
- Windows: `python -m venv venv` ➡️ `venv\Scripts\activate`
- Linux/macOS: `python3 -m venv venv` ➡️ `source venv/bin/activate`

**3. Install dependencies**
```bash
pip install matplotlib shapely trimesh numpy ezdxf
```

**4. Run the program**
```bash
python main.py
```
*(On Windows, you can also use the `run.bat` file to automate venv activation and App execution).*

### 📖 Mini Usage Tutorial

Learn how to use GCode Reconstructor in 4 easy steps:

**Step 1: Load GCode**
1. Open the application.
2. Click the **"1. Load GCode"** button on the left panel.
3. Browse your computer and select a previously sliced `.gcode` file (from Cura, PrusaSlicer, Orca, etc.).
4. The software will analyze the file lines and update the interface listing all detected Z heights.

**Step 2: Setup Parameters**
In the **"2. Parameters"** block, adjust the simulation fidelity:
- **Nozzle Width (mm):** (e.g., 0.4). Used in screen previews and mathematical modeling calculations.
- **Layer Height (mm):** (e.g., 0.2). Mainly used when creating extrusion height for 3D exporting.
- **Nozzle simulation (3D/2D):** Checking this renders thick lines matching the physical extrusion area. Unchecking shows only the trajectory "skeleton".

**Step 3: Line Filtering and Layer View**
1. In the display block, use the slider or click the Z menu to transition through layers.
2. The bottom-right filters let you toggle **Line Types**. 
   - *Example:* To focus strictly on infill thickness, uncheck everything except `FILL (Infill)`.
3. Use the main window and zoom buttons to closely check line geometry.

**Step 4: Exporting**
Once satisfied with the layer or file filter:
- **Export Layer (DXF):** Extracts current viewed outline to a 2D CAD file. Great for laser-cutting acrylic slices.
- **Export ALL (Folder DXF):** Silently exports all Z heights to individual files in a chosen directory.
- **Export 3D Model:** Converts all filtered GCode lines into a solid, robust 3D file representing the exact print volume.

### 👨‍💻 Authors
- **Author:** Jairo Ivo Castro Brito
- **Advisor:** Bruno Vieira Bertoncini

### 🤝 Contributions
Contributions are welcome! If you found a bug or want to add support for new delimiters or relative extrusion readings (E), feel free to open an *Issue* or submit a *Pull Request*.

### 📄 License
Check the `LICENSE` file distributed with this repository for permissions regarding commercial use, modification, and technical/legal distribution.

---

<h2 id="português">🇧🇷 Português</h2>

Um aplicativo robusto com interface gráfica (GUI) em Python para visualizar, analisar e converter arquivos GCode de impressão 3D em geometrias 2D (DXF) e modelos 3D (STL, OBJ, etc.).

Este projeto é **extremamente útil para casos em que se deseja estudar a estrutura do preenchimento interno (infill) de uma peça**, validar paredes, gerenciar suportes ou efetuar engenharia reversa de um GCode fatiado de volta para um modelo CAD.

### ✨ Principais Funcionalidades

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

### 🛠️ Pré-requisitos e Dependências

O software foi desenvolvido em Python e requer algumas bibliotecas externas para funcionar corretamente. 

Certifique-se de ter o Python (versão 3.8 ou superior) instalado em seu sistema operacional e as seguintes dependências:
- `matplotlib`
- `shapely`
- `trimesh`
- `numpy`
- `ezdxf`

*(O projeto também usa bibliotecas padrão do Python como `tkinter`, `os` e `re`).*

### 🚀 Instalação e Execução

Existem duas formas de executar o **GCode Reconstructor**: usando o executável standalone (focado em usuários) ou via código-fonte (para desenvolvedores).

#### Opção 1: Executável Standalone (Recomendado)

Se você utiliza **Windows**, pode usar o programa diretamente sem instalar dependências ou configurar ambiente virtual!
1. Baixe o arquivo `GCode-Reconstructor.exe` presente na raiz deste repositório (ou acesse a área de *Releases*).
2. Dê um duplo-clique no arquivo `.exe`.
3. A interface abrirá instantaneamente.

#### Opção 2: Executar via Código-Fonte (Python)

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

### 📖 Mini Tutorial de Uso

Aprenda a utilizar o GCode Reconstructor com 4 passos simples:

**Passo 1: Carregar o GCode**
1. Abra o aplicativo.
2. Clique no botão **"1. Carregar GCode"** (ou "1. Load GCode") localizado no painel lateral esquerdo.
3. Navegue pelas pastas do seu computador e selecione um arquivo `.gcode` previamente fatiado (no Cura, PrusaSlicer, Orca, etc.).
4. O software analisará as linhas do arquivo e atualizará a interface listando todas as alturas Z detectadas.

**Passo 2: Configurar Parâmetros**
No bloco **"2. Parâmetros"**, ajuste a fidelidade da simulação do seu arquivo:
- **Largura do Bico (Nozzle Width):** Em milímetros (ex: 0.4). Usado tanto nas previsões em tela quanto nos cálculos matemáticos de modelagem.
- **Altura da Camada (Layer Height):** Em milímetros (ex: 0.2). Usado sobretudo ao criar a altura da extrusão dos modelos na exportação 3D.
- **Nozzle simulation (3D/2D):** Ao marcar esta opção, os gráficos renderizam linhas espessas condizentes com o tamanho físico da área de extrusão. Deixando desmarcado, a exibição será feita apenas do "esqueleto" e pontos de trajetória.

**Passo 3: Filtro de Linhas e Visualização de Camada**
1. No bloco de exibição (Camada atual), use o controle deslizante (slider) ou clique diretamente no menu do Z (Z: xxx mm) para transitar pelas camadas.
2. Na área inferior direita estão os filtros que permitem ativar / desativar os **Tipos de Linha**. 
   - Exemplo de Uso: Caso queira focar a análise em como a espessura da estrutura interna vai se comportar, desmarque todas as caixas, exceto `FILL (Infill)`.
3. A janela principal e os botões de zoom abaixo dela permitem que você se aproxime bastante para checar se as linhas estão colidindo ou formando a geometria certa.

**Passo 4: Exportação**
Satisfeito com o filtro da camada ou do arquivo todo? Utilize uma destas 3 funções:
- **Exportar Camada (DXF):** Extrai o contorno atual visualizado e monta um arquivo CAD bidimensional (DXF). Ótimo para enviar a um corte a laser acrílico validando fatias, por exemplo.
- **Exportar TUDO (Pasta DXF):** Exporta de forma silenciosa todas as alturas Z (sem precisar acessar uma por uma) diretamente para arquivos individuais em um diretório definido no seu computador.
- **Exportar Modelo 3D (Extrusão):** Uma ferramenta fantástica que converte toda as linhas filtradas do GCode atual aplicando altura e largura, permitindo extrair daquele GCode apenas o volume de impressão exato em arquivo 3D robusto.

### 👨‍💻 Autores
- **Autor:** Jairo Ivo Castro Brito
- **Orientador:** Bruno Vieira Bertoncini

### 🤝 Contribuições
Contribuições são bem-vindas! Se você encontrou um bug ou quer adicionar suporte a novos delimitadores ou leituras de extrusão relativas (E), fique a vontade para abrir uma *Issue* ou enviar um *Pull Request*.

### 📄 Licença
Consulte o arquivo `LICENSE` distribuído junto a este repositório para permissões relativas ao uso comercial, modificação e distribuição técnica e legal.