import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from gcode_parser import GCodeParser
from dxf_exporter import export_layer_to_dxf, export_all_layers_to_folder
from exporter_3d import export_3d_model
import os

TRANSLATIONS = {
    'en': {
        'title': 'GCode 2D/3D Reconstructor',
        'load_btn': '1. Load GCode',
        'no_file': 'No file loaded',
        'params': '2. Parameters',
        'nozzle_w': 'Nozzle Width (mm):',
        'layer_h': 'Layer Height (mm):',
        'sim_line': 'Line',
        'sim_square': 'Square',
        'sim_tubular': 'Tubular',
        'sim_stadium': 'Stadium',
        'resolution': 'Resolution (Segs):',
        'export_types': '3. Export/Preview Types:',
        'layer_nav': '4. Layer Navigation',
        'export_actions': '5. Export Actions',
        'btn_export_dxf': 'Export Current Layer (DXF)',
        'btn_export_all_dxf': 'Export ALL Layers (Folder DXF)',
        'btn_export_3d': 'Export 3D Model (STL/OBJ/STEP)',
        'about': 'About',
        'author': 'Author: Jairo Ivo Castro Brito | Advisor: Bruno Vieira Bertoncini',
        'license': 'License: GNU GENERAL PUBLIC LICENSE || Version 3, 29 June 2007',
        'lang': 'Language: ',
        'progress': 'Progress:',
        'msg_processing': 'The generation will start. This might take a while depending on file size...',
        'msg_success': 'Export completed successfully to:\n',
        'msg_error': 'Error during export:\n',
        'no_types': 'No path types selected.',
        'layer': 'Layer',
        'type_fill': 'FILL (Infill)',
        'type_wall-outer': 'WALL-OUTER',
        'type_wall-inner': 'WALL-INNER',
        'type_skirt': 'SKIRT / BRIM',
        'type_support': 'SUPPORT',
        'type_unknown': 'UNKNOWN'
    },
    'pt': {
        'title': 'Reconstrutor 2D/3D de GCode',
        'load_btn': '1. Carregar GCode',
        'no_file': 'Nenhum arquivo',
        'params': '2. Parâmetros',
        'nozzle_w': 'Largura do Bico (mm):',
        'layer_h': 'Altura da Camada (mm):',
        'sim_line': 'Linha',
        'sim_square': 'Quadrado',
        'sim_tubular': 'Tubular',
        'sim_stadium': 'Estádio',
        'resolution': 'Resolução (Segs):',
        'export_types': '3. Propriedades para Exportar:',
        'layer_nav': '4. Navegação por Camadas',
        'export_actions': '5. Ações de Exportação',
        'btn_export_dxf': 'Exportar Camada Atual (DXF)',
        'btn_export_all_dxf': 'Exportar TODAS Camadas (Pasta DXF)',
        'btn_export_3d': 'Exportar Modelo 3D (STL/OBJ/STEP)',
        'about': 'Sobre',
        'author': 'Autor: Jairo Ivo Castro Brito | Orientador: Bruno Vieira Bertoncini',
        'license': 'Licença: GPL v3',
        'lang': 'Idioma: ',
        'progress': 'Progresso:',
        'msg_processing': 'A geração vai começar. Pode demorar dependendo do arquivo...',
        'msg_success': 'Exportação concluída com sucesso para:\n',
        'msg_error': 'Erro durante exportação:\n',
        'no_types': 'Nenhum tipo de linha selecionada.',
        'layer': 'Camada',
        'type_fill': 'PREENCHIMENTO',
        'type_wall-outer': 'PAREDE EXTERNA',
        'type_wall-inner': 'PAREDE INTERNA',
        'type_skirt': 'BORDA / SAIA',
        'type_support': 'SUPORTE',
        'type_unknown': 'DESCONHECIDO'
    }
}

class GCodeToDXFApp:
    def __init__(self, root):
        self.root = root
        self.lang = 'pt'
        self.root.title(self.t('title'))
        self.root.geometry("1000x750")
        
        self.parser = GCodeParser()
        self.layers = []
        self.available_types = set()
        self.type_vars = {} 
        self.type_sim_vars = {}
        
        self._create_widgets()
        
    def t(self, key):
        return TRANSLATIONS[self.lang].get(key, key)
        
    def t_type(self, path_type):
        key = f"type_{path_type.lower()}"
        return TRANSLATIONS[self.lang].get(key, path_type)

    def _create_widgets(self):
        # Left Panel (Controls)
        self.control_canvas = tk.Canvas(self.root, width=320)
        self.control_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.control_canvas.yview)
        
        self.control_frame = ttk.Frame(self.control_canvas, padding="10")
        
        self.control_frame.bind(
            "<Configure>",
            lambda e: self.control_canvas.configure(
                scrollregion=self.control_canvas.bbox("all")
            )
        )
        self.control_canvas.create_window((0, 0), window=self.control_frame, anchor="nw")
        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)
        
        self.control_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.control_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Language Switch
        lang_frame = ttk.Frame(self.control_frame)
        lang_frame.pack(fill=tk.X, pady=(0,5))
        self.lbl_lang = ttk.Label(lang_frame, text=self.t('lang'))
        self.lbl_lang.pack(side=tk.LEFT)
        self.btn_lang = ttk.Button(lang_frame, text="EN/PT", command=self.toggle_language)
        self.btn_lang.pack(side=tk.LEFT)

        # Load Button
        self.btn_load = ttk.Button(self.control_frame, text=self.t('load_btn'), command=self.load_gcode)
        self.btn_load.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_file = ttk.Label(self.control_frame, text=self.t('no_file'), wraplength=250)
        self.lbl_file.pack(fill=tk.X, pady=(0, 20))
        
        # --- Parameter Inputs ---
        self.lbl_params = ttk.Label(self.control_frame, text=self.t('params'), font=("Helvetica", 10, "bold"))
        self.lbl_params.pack(anchor=tk.W, pady=(0, 5))
        param_frame = ttk.Frame(self.control_frame)
        param_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.lbl_nozzle = ttk.Label(param_frame, text=self.t('nozzle_w'))
        self.lbl_nozzle.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.nozzle_var = tk.DoubleVar(value=0.4)
        ttk.Entry(param_frame, textvariable=self.nozzle_var, width=10).grid(row=0, column=1, pady=2)
        
        self.lbl_layerh = ttk.Label(param_frame, text=self.t('layer_h'))
        self.lbl_layerh.grid(row=1, column=0, sticky=tk.W, pady=2)
        self.layer_height_var = tk.DoubleVar(value=0.4)
        ttk.Entry(param_frame, textvariable=self.layer_height_var, width=10).grid(row=1, column=1, pady=2)
        
        self.lbl_resolution = ttk.Label(param_frame, text=self.t('resolution'))
        self.lbl_resolution.grid(row=2, column=0, sticky=tk.W, pady=2)
        self.resolution_var = tk.IntVar(value=8)
        ttk.Entry(param_frame, textvariable=self.resolution_var, width=10).grid(row=2, column=1, pady=2)

        
        # --- Type Selection ---
        self.lbl_export_types = ttk.Label(self.control_frame, text=self.t('export_types'), font=("Helvetica", 10, "bold"))
        self.lbl_export_types.pack(anchor=tk.W)
        self.types_frame = ttk.Frame(self.control_frame)
        self.types_frame.pack(fill=tk.X, pady=(5, 20))
        
        # --- Layer Selection ---
        self.lbl_layer_nav = ttk.Label(self.control_frame, text=self.t('layer_nav'), font=("Helvetica", 10, "bold"))
        self.lbl_layer_nav.pack(anchor=tk.W)
        
        self.combo_layers = ttk.Combobox(self.control_frame, state="readonly", width=30)
        self.combo_layers.pack(fill=tk.X, pady=(5, 5))
        self.combo_layers.bind("<<ComboboxSelected>>", self.on_layer_selected)
        
        self.slider_layer = ttk.Scale(self.control_frame, from_=0, to=0, orient=tk.HORIZONTAL, command=self.on_slider_move)
        self.slider_layer.pack(fill=tk.X, pady=(0, 20))
        
        # --- Export Buttons ---
        self.lbl_export_acts = ttk.Label(self.control_frame, text=self.t('export_actions'), font=("Helvetica", 10, "bold"))
        self.lbl_export_acts.pack(anchor=tk.W)
        
        self.btn_export_dxf = ttk.Button(self.control_frame, text=self.t('btn_export_dxf'), command=self.export_dxf)
        self.btn_export_dxf.pack(fill=tk.X, pady=(5, 2))
        
        self.btn_export_all_dxf = ttk.Button(self.control_frame, text=self.t('btn_export_all_dxf'), command=self.export_all_dxf)
        self.btn_export_all_dxf.pack(fill=tk.X, pady=(2, 2))
        
        self.btn_export_3d = ttk.Button(self.control_frame, text=self.t('btn_export_3d'), command=self.export_3d)
        self.btn_export_3d.pack(fill=tk.X, pady=(2, 20))
        
        # --- Progress Bar ---
        self.lbl_progress = ttk.Label(self.control_frame, text=self.t('progress'))
        self.lbl_progress.pack(anchor=tk.W)
        self.progress_bar = ttk.Progressbar(self.control_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 20))

        # --- About Section ---
        self.lbl_about = ttk.Label(self.control_frame, text=self.t('about'), font=("Helvetica", 9, "bold"))
        self.lbl_about.pack(anchor=tk.W)
        self.lbl_author = ttk.Label(self.control_frame, text=self.t('author'), font=("Helvetica", 8))
        self.lbl_author.pack(anchor=tk.W)
        self.lbl_license = ttk.Label(self.control_frame, text=self.t('license'), font=("Helvetica", 8))
        self.lbl_license.pack(anchor=tk.W)

        # Right Panel (Preview)
        preview_frame = ttk.Frame(self.root, padding="10")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=preview_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax.axis('off')

    def toggle_language(self):
        self.lang = 'en' if self.lang == 'pt' else 'pt'
        self.root.title(self.t('title'))
        self.btn_load.config(text=self.t('load_btn'))
        if not self.layers:
            self.lbl_file.config(text=self.t('no_file'))
        self.lbl_params.config(text=self.t('params'))
        self.lbl_nozzle.config(text=self.t('nozzle_w'))
        self.lbl_layerh.config(text=self.t('layer_h'))
        self.lbl_resolution.config(text=self.t('resolution'))
        self.lbl_export_types.config(text=self.t('export_types'))
        self.lbl_layer_nav.config(text=self.t('layer_nav'))
        self.lbl_export_acts.config(text=self.t('export_actions'))
        self.btn_export_dxf.config(text=self.t('btn_export_dxf'))
        self.btn_export_all_dxf.config(text=self.t('btn_export_all_dxf'))
        self.btn_export_3d.config(text=self.t('btn_export_3d'))
        self.lbl_about.config(text=self.t('about'))
        self.lbl_author.config(text=self.t('author'))
        self.lbl_license.config(text=self.t('license'))
        self.lbl_lang.config(text=self.t('lang'))
        self.lbl_progress.config(text=self.t('progress'))
        self._update_layer_list()
        self._update_type_checkboxes()

    def update_progress(self, current, total):
        if total > 0:
            pct = (current / total) * 100
            self.progress_bar['value'] = pct
            self.root.update_idletasks()

    def load_gcode(self):
        filepath = filedialog.askopenfilename(
            title="Select GCode File",
            filetypes=(("GCode Files", "*.gcode"), ("All Files", "*.*"))
        )
        if not filepath:
            return
            
        self.lbl_file.config(text=os.path.basename(filepath))
        self.parser = GCodeParser()
        self.layers = self.parser.parse_file(filepath)
        
        if self.parser.layer_height > 0:
            self.layer_height_var.set(self.parser.layer_height)
            
        self.available_types = set()
        for layer in self.layers:
            for path_type in layer.segments_by_type.keys():
                self.available_types.add(path_type)
        
        self._update_layer_list()
        self._update_type_checkboxes()
        
        if self.layers:
            self.combo_layers.current(0)
            self.slider_layer.config(to=len(self.layers)-1)
            self.slider_layer.set(0)
            self.update_preview()

    def _update_layer_list(self):
        layer_names = []
        for lyr in self.layers:
            z_str = f"{lyr.z_height:.2f}" if lyr.z_height is not None else "??"
            layer_names.append(f"{self.t('layer')} {lyr.index} (Z: {z_str} mm)")
            
        self.combo_layers['values'] = layer_names
        
        # Keep selection valid
        idx = self.slider_layer.get()
        if self.layers and 0 <= idx < len(self.layers):
            self.combo_layers.current(int(idx))

    def _update_type_checkboxes(self):
        for widget in self.types_frame.winfo_children():
            widget.destroy()
            
        self.type_vars.clear()
        self.type_sim_vars.clear()
        
        if not self.available_types:
            ttk.Label(self.types_frame, text="No types found").pack(anchor=tk.W)
            return
            
        sim_options = [self.t('sim_line'), self.t('sim_square'), self.t('sim_tubular'), self.t('sim_stadium')]
        sim_options_keys = ['line', 'square', 'tubular', 'stadium']

        for ptype in sorted(self.available_types):
            row_frame = ttk.Frame(self.types_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            var = tk.BooleanVar(value=True)
            self.type_vars[ptype] = var
            chk = ttk.Checkbutton(row_frame, text=self.t_type(ptype), variable=var, command=self.update_preview)
            chk.pack(side=tk.LEFT)
            
            sim_var = tk.StringVar(value=sim_options[0])
            self.type_sim_vars[ptype] = sim_var
            cmb = ttk.Combobox(row_frame, textvariable=sim_var, values=sim_options, state="readonly", width=10)
            cmb.pack(side=tk.RIGHT)
            cmb.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

    def on_layer_selected(self, event=None):
        idx = self.combo_layers.current()
        if idx >= 0:
            self.slider_layer.set(idx)
        self.update_preview()
        
    def on_slider_move(self, value):
        idx = int(float(value))
        if idx != self.combo_layers.current():
            self.combo_layers.current(idx)
            self.update_preview()

    def update_preview(self):
        idx = self.combo_layers.current()
        if idx < 0 or idx >= len(self.layers):
            return
            
        layer = self.layers[idx]
        
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.set_title(f"Preview: Layer {layer.index}")
        
        has_data = False
        colors = plt.get_cmap('tab10')
        color_idx = 0
        
        try:
            nozzle_width = float(self.nozzle_var.get())
        except ValueError:
            nozzle_width = 0.4

        for path_type, segments in layer.segments_by_type.items():
            if path_type in self.type_vars and self.type_vars[path_type].get():
                has_data = True
                c = colors(color_idx % 10)
                
                # Get the selected simulation type for this particular path type
                opts_inv = {
                    self.t('sim_line'): 'line', 
                    self.t('sim_square'): 'square', 
                    self.t('sim_tubular'): 'tubular',
                    self.t('sim_stadium'): 'stadium'
                }
                sim_type = opts_inv.get(self.type_sim_vars[path_type].get(), 'line')
                
                if sim_type in ['square', 'tubular', 'stadium'] and nozzle_width > 0:
                    from shapely.geometry import LineString, Polygon
                    from shapely.ops import unary_union, linemerge
                    from matplotlib.patches import Polygon as MplPolygon
                    
                    # 1 = Round (Tubular/Stadium), 2 = Flat 
                    buffer_cap_style = 1 if sim_type in ['tubular', 'stadium'] else 2
                    # 1 = Round, 3 = Bevel (cuts off spikes at sharp angles)
                    buffer_join_style = 1 if sim_type in ['tubular', 'stadium'] else 3
                    
                    try:
                        resolution = int(self.resolution_var.get())
                    except ValueError:
                        resolution = 8
                    
                    lines = [LineString([p1, p2]) for p1, p2 in segments]
                    merged_lines = linemerge(lines)
                    layer_polygon = merged_lines.buffer(nozzle_width / 2.0, cap_style=buffer_cap_style, join_style=buffer_join_style, quad_segs=resolution)
                    
                    polys = []
                    if isinstance(layer_polygon, Polygon):
                        polys.append(layer_polygon)
                    elif hasattr(layer_polygon, 'geoms'):
                        polys.extend(list(layer_polygon.geoms))
                        
                    first = True
                    for poly in polys:
                        ext_coords = list(poly.exterior.coords)
                        mpl_poly = MplPolygon(ext_coords, closed=True, facecolor=c, edgecolor=c, alpha=0.5, label=self.t_type(path_type) if first else "")
                        self.ax.add_patch(mpl_poly)
                        first = False
                        
                        for interior in poly.interiors:
                            int_coords = list(interior.coords)
                            mpl_hole = MplPolygon(int_coords, closed=True, facecolor='white', edgecolor=c, alpha=1.0)
                            self.ax.add_patch(mpl_hole)
                            
                    # Invisible plot to ensure data limits are updated for the patches
                    xs = []
                    ys = []
                    for p1, p2 in segments:
                        xs.extend([p1[0], p2[0]])
                        ys.extend([p1[1], p2[1]])
                    if xs and ys:
                        self.ax.plot(xs, ys, alpha=0)
                else:
                    first = True
                    for p1, p2 in segments:
                        if first:
                            self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c, linewidth=1, label=self.t_type(path_type))
                            first = False
                        else:
                            self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c, linewidth=1)
            color_idx += 1
            
        if not has_data:
            self.ax.text(0.5, 0.5, "Empty layer", 
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes)
        else:
            self.ax.legend(loc='upper right', fontsize='small')
                         
        self.ax.axis('auto')
        self.canvas.draw()
        
    def get_selected_types(self):
        selected = {}
        # Reverse map translation to key
        opts_inv = {
            self.t('sim_line'): 'line', 
            self.t('sim_square'): 'square', 
            self.t('sim_tubular'): 'tubular',
            self.t('sim_stadium'): 'stadium'
        }
        
        for root_type, var in self.type_vars.items():
            if var.get():
                sim_str = self.type_sim_vars[root_type].get()
                selected[root_type] = opts_inv.get(sim_str, 'line')
        return selected

    def export_dxf(self):
        idx = self.combo_layers.current()
        if idx < 0 or idx >= len(self.layers): return
        layer = self.layers[idx]
        
        selected_types = self.get_selected_types()
        if not selected_types:
            messagebox.showwarning("Warning", self.t('no_types'))
            return
            
        z_str = f"{layer.z_height:.2f}" if layer.z_height is not None else "unknown"
        default_filename = f"Layer_{layer.index}_Z{z_str}.dxf"
        
        filepath = filedialog.asksaveasfilename(
            initialfile=default_filename, defaultextension=".dxf",
            filetypes=(("DXF Files", "*.dxf"), ("All Files", "*.*"))
        )
        if not filepath: return
        
        try:
            resolution = int(self.resolution_var.get())
        except ValueError:
            resolution = 8
        self.progress_bar['value'] = 0
        success, res = export_layer_to_dxf(layer, filepath, simulation_types=selected_types, nozzle_width=self.nozzle_var.get(), resolution=resolution)
        self.progress_bar['value'] = 100
        
        if success:
            messagebox.showinfo("Success", f"{self.t('msg_success')}{filepath}")
        else:
            messagebox.showerror("Export Failed", f"{self.t('msg_error')}{res}")
 
    def export_all_dxf(self):
        selected_types = self.get_selected_types()
        if not selected_types:
            messagebox.showwarning("Warning", self.t('no_types'))
            return
            
        folderpath = filedialog.askdirectory()
        if not folderpath: return
            
        try:
            resolution = int(self.resolution_var.get())
        except ValueError:
            resolution = 8
        try:
            self.progress_bar['value'] = 0
            export_all_layers_to_folder(self.layers, folderpath, simulation_types=selected_types, nozzle_width=self.nozzle_var.get(), resolution=resolution, progress_callback=self.update_progress)
            messagebox.showinfo("Success", f"{self.t('msg_success')}{folderpath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"{self.t('msg_error')}{str(e)}")
        finally:
            self.progress_bar['value'] = 0
 
    def export_3d(self):
        selected_types = self.get_selected_types()
        if not selected_types:
            messagebox.showwarning("Warning", self.t('no_types'))
            return
            
        filepath = filedialog.asksaveasfilename(
            initialfile="reconstructed_object.stl", defaultextension=".stl",
            filetypes=(("STL Files", "*.stl"), ("OBJ Files", "*.obj"), ("STEP Files", "*.step"), ("All Files", "*.*"))
        )
        if not filepath: return
            
        messagebox.showinfo("Processing", self.t('msg_processing'))
        self.root.update()
        self.progress_bar['value'] = 0
        
        try:
            resolution = int(self.resolution_var.get())
        except ValueError:
            resolution = 8
            
        success, res = export_3d_model(
            self.layers, filepath, selected_types, 
            self.nozzle_var.get(), self.layer_height_var.get(), 
            resolution=resolution,
            progress_callback=self.update_progress
        )
        self.progress_bar['value'] = 0
        
        if success:
            messagebox.showinfo("Success", f"{self.t('msg_success')}{filepath}")
        else:
            messagebox.showerror("Export Failed", f"{self.t('msg_error')}{res}")

def main():
    root = tk.Tk()
    app = GCodeToDXFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
