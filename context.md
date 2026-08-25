# Project Context: GCode Reconstructor 🖨️🔄

Este documento serve como referência de contexto de alto nível para agentes e desenvolvedores trabalhando no repositório **GCode-Reconstructor**.

## 📌 Visão Geral
O **GCode Reconstructor** é uma aplicação Python GUI (desenvolvida com `tkinter`) criada para visualizar, analisar e converter arquivos GCode de fatiamento 3D em geometrias vetoriais 2D (DXF) e modelos sólidos 3D (STL, OBJ, STEP).

A ferramenta é de extrema utilidade para:
- Estudar a estrutura do preenchimento interno (*infill*) de peças fatiadas.
- Efetuar engenharia reversa de caminhos de extrusão de volta para CAD.
- Validar colapsos ou sobreposições de material.
- Gerar fatias 2D para corte a laser (via exportação DXF).

---

## 🏛️ Arquitetura do Sistema

O projeto é dividido em quatro componentes principais de responsabilidade única:

1. **Interface do Usuário (GUI):**
   - **[main.py](file:///c:/Users/jairo/OneDrive/Desktop/Projetos/GCode-Reconstructor/main.py):** Implementa a interface principal com Tkinter, lida com a tradução em dois idiomas (PT/EN), controla os inputs do usuário, rendering 2D interativo das camadas via `matplotlib`/`shapely` e delega as ações de exportação.

2. **Parser de GCode:**
   - **[gcode_parser.py](file:///c:/Users/jairo/OneDrive/Desktop/Projetos/GCode-Reconstructor/gcode_parser.py):** Varre o arquivo GCode linha a linha. Rastreia o estado tridimensional (X, Y, Z) e de extrusão (E), e separa a informação em estruturas categorizadas (ex: `WALL-OUTER`, `WALL-INNER`, `FILL`, `SUPPORT`, `SKIRT`) dentro de objetos da classe `GCodeLayer`. Suporta extrusão absoluta (`M82`) e relativa (`M83`).

3. **Exportador Vetorial 2D:**
   - **[dxf_exporter.py](file:///c:/Users/jairo/OneDrive/Desktop/Projetos/GCode-Reconstructor/dxf_exporter.py):** Converte as trajetórias 2D de uma ou de todas as camadas para o formato vetorial `.dxf` usando a biblioteca `ezdxf`. Dependendo do modo de simulação, realiza operações de buffer no `shapely` para delinear a área correspondente à espessura física do bico.

4. **Exportador 3D:**
   - **[exporter_3d.py](file:///c:/Users/jairo/OneDrive/Desktop/Projetos/GCode-Reconstructor/exporter_3d.py):** Gera a representação tridimensional do filamento extrudado. Utiliza `trimesh` e `shapely` para STL/OBJ, e `build123d` de forma opcional para gerar arquivos STEP sólidos.

---

## 📐 Estilos de Simulação e Perfis

Ao processar as trajetórias das linhas de impressão, a ferramenta suporta quatro estilos de simulação distintos:

* **Linha (Line):** Renderiza as trajetórias como curvas ou segmentos 1D simples.
* **Quadrado (Square):** Expande os caminhos para um perfil retangular sólido 3D de largura igual à largura do bico e altura igual à altura da camada.
* **Tubular (Tubular):** Modela o filamento como um tubo de seção transversal elíptica (largura = diâmetro do bico, altura = altura da camada).
* **Estádio (Stadium) *[Adicionado na Release 1.6]*:** Modela a extrusão realista de filamento comprimido (faces superior e inferior planas, e laterais arredondadas como semicírculos).

---

## ⚙️ Controle de Resolução de Malha *[Adicionado na Release 1.6]*

O usuário pode definir um parâmetro numérico de **Resolução** (em segmentos) através da interface gráfica:
- Controla o número de subdivisões dos arcos no perfil **Estádio** e **Tubular** da varredura 3D.
- Define a quantidade de segmentos (`quad_segs`) utilizada nas curvas de expansão em 2D e 3D ao aplicar o método `.buffer()` do `shapely`.
- Permite gerar malhas de alta definição ou malhas leves de baixo polígono.

---

## 🛠️ Ambiente de Desenvolvimento e Dependências

Para rodar e testar o projeto, é necessário utilizar o Python 3.8+ (atualmente testado com Python 3.14.5) e as dependências listadas:
- `matplotlib`
- `shapely`
- `trimesh`
- `numpy`
- `ezdxf`
- `mapbox-earcut` (necessário para a triangulação de polígonos nas extrusões do `trimesh`)
- `build123d` (opcional, apenas para exportação de sólidos STEP)

### Como Configurar
1. Limpar/criar o ambiente virtual:
   ```bash
   python -m venv venv --clear
   ```
2. Instalar dependências:
   ```bash
   venv\Scripts\pip install matplotlib shapely trimesh numpy ezdxf mapbox-earcut
   ```
3. Executar o projeto:
   ```bash
   venv\Scripts\python main.py
   ```

### Script de Teste
Existe um script de integração e validação que testa o parsing, os perfis geométricos, a exportação DXF e a geração de malha 3D em diferentes resoluções:
* **[test_reconstructor.py](file:///c:/Users/jairo/OneDrive/Desktop/Projetos/GCode-Reconstructor/scratch/test_reconstructor.py):** Executável para validar regressões ou novos perfis geométricos.
