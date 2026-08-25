---
name: GCode Reconstructor Specialist
description: Assisting with development, debugging, and extensions to the GCode-Reconstructor project.
---
# GCode Reconstructor Specialist Skill

Esta skill fornece diretrizes técnicas para desenvolvedores e agentes ao trabalhar no projeto GCode-Reconstructor.

## 📐 Diretrizes de Modelagem e Matemática 3D
- **Orientação de Perfis 2D para Varredura (Sweep):** 
  Ao criar geometrias para varreduras 3D no `trimesh` (usando `sweep_polygon`), a largura física da extrusão (nozzle width) deve se alinhar ao eixo **X** da seção transversal e a altura da camada (layer height) deve se alinhar ao eixo **Y** da seção transversal. O Y do perfil 2D será mapeado para a coordenada vertical (Z) do espaço 3D.
- **Formulação do Perfil Estádio:** 
  O perfil estádio é composto por retas horizontais de comprimento $W - H$ no topo ($Y = +H/2$) e base ($Y = -H/2$), conectadas por tampas circulares de raio $R = H/2$ nas laterais.
- **Resolução de Curvas:** 
  Sempre repasse o parâmetro `resolution` (segs por quadrante) para operações de `.buffer(..., quad_segs=resolution)` e para os geradores de perfil de varredura elíptico e de estádio.

## 🔍 Parsing de GCode
- **Padrões de Comentários de Fatiador:**
  Sempre suporte os comentários gerados pelos fatiadores mais comuns (Cura, PrusaSlicer, SuperSlicer, Orca, Bambu Studio):
  - `;LAYER:` para marcar a mudança de camada.
  - `;TYPE:` para identificar o tipo de trajetória (`FILL`, `WALL-OUTER`, `WALL-INNER`, `SUPPORT`, `SKIRT`).
  - `;LAYER HEIGHT:` para ler a altura padrão.
- **Estado de Extrusão:** 
  Rastreie corretamente a extrusão absoluta (`M82`) e relativa (`M83`) e as reinicializações de coordenadas (`G92 E0`).

## 🧪 Validação e Testes
- Sempre execute o script de validação local após qualquer modificação em `exporter_3d.py`, `dxf_exporter.py` ou `gcode_parser.py`:
  ```bash
  venv\Scripts\python.exe scratch\test_reconstructor.py
  ```
