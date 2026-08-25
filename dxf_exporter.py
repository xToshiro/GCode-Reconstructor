import ezdxf
import os

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union, linemerge

def export_layer_to_dxf(gcode_layer, output_path, simulation_types=None, nozzle_width=0.0, resolution=8):
    """
    Exports a single GCodeLayer object to a DXF file.
    
    :param gcode_layer: GCodeLayer instance
    :param output_path: str, destination path for the .dxf file
    :param simulation_types: dict mapping segment types to their simulation style ('line', 'square', 'tubular', 'stadium')
    :param nozzle_width: float. If > 0, lines will be drawn as LWPOLYLINE with this width.
    :param resolution: int, segments per quadrant for the round buffer
    """
    if simulation_types is None:
        simulation_types = {}
        
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()
    doc.header['$INSUNITS'] = 4  # 4 = millimeters
    
    type_colors = {
        'WALL-OUTER': 1, # Red
        'WALL-INNER': 2, # Yellow
        'SKIRT': 3,      # Green
        'FILL': 4,       # Cyan
        'SUPPORT': 5,    # Blue
        'UNKNOWN': 7     # White/Black
    }
 
    created_dxf_layers = set()
    exported_count = 0
 
    for path_type, segments in gcode_layer.segments_by_type.items():
        if path_type not in simulation_types:
            continue
            
        dxf_layer_name = f"GCODE_{path_type.replace(' ', '_').upper()}"
        
        if dxf_layer_name not in created_dxf_layers:
            color = type_colors.get(path_type.upper(), 7)
            doc.layers.add(name=dxf_layer_name, color=color)
            created_dxf_layers.add(dxf_layer_name)
            
        sim_type = simulation_types.get(path_type, 'line')
            
        if sim_type in ['square', 'tubular', 'stadium'] and nozzle_width > 0:
            buffer_cap_style = 1 if sim_type in ['tubular', 'stadium'] else 2
            buffer_join_style = 1 if sim_type in ['tubular', 'stadium'] else 3
            
            # Draw outlined footprint polylines
            lines = [LineString([p1, p2]) for p1, p2 in segments]
            merged_lines = linemerge(lines)
            layer_polygon = merged_lines.buffer(nozzle_width / 2.0, cap_style=buffer_cap_style, join_style=buffer_join_style, quad_segs=resolution)
            
            polys = []
            if isinstance(layer_polygon, Polygon):
                polys.append(layer_polygon)
            elif hasattr(layer_polygon, 'geoms'):
                polys.extend(list(layer_polygon.geoms))
                
            for poly in polys:
                # Add exterior boundary
                points = list(poly.exterior.coords)
                msp.add_lwpolyline(points, dxfattribs={'layer': dxf_layer_name}, close=True)
                # Add holes (interiors)
                for interior in poly.interiors:
                    msp.add_lwpolyline(list(interior.coords), dxfattribs={'layer': dxf_layer_name}, close=True)
                exported_count += 1
        else:
            for (p1, p2) in segments:
                # Check if nozzle width is requested
                if nozzle_width > 0:
                    # Add LWPOLYLINE with const_width
                    msp.add_lwpolyline([p1, p2], dxfattribs={
                        'layer': dxf_layer_name,
                        'const_width': nozzle_width
                    })
                else:
                    # standard thin line
                    msp.add_line(p1, p2, dxfattribs={'layer': dxf_layer_name})
                exported_count += 1
            
    try:
        doc.saveas(output_path)
        return True, exported_count
    except Exception as e:
        return False, str(e)
 
def export_all_layers_to_folder(layers, output_folder, simulation_types=None, nozzle_width=0.0, resolution=8, progress_callback=None):
    """
    Exports all layers to individual DXF files inside the given folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for i, layer in enumerate(layers):
        if progress_callback:
            progress_callback(i, len(layers))
        z_str = f"{layer.z_height:.2f}" if layer.z_height is not None else "unknown"
        filename = f"Layer_{layer.index:03d}_Z{z_str}.dxf"
        out_path = os.path.join(output_folder, filename)
        
        export_layer_to_dxf(layer, out_path, simulation_types, nozzle_width, resolution)
        
    if progress_callback:
        progress_callback(len(layers), len(layers))

if __name__ == "__main__":
    from gcode_parser import GCodeParser
    import os
    
    # Quick test
    parser = GCodeParser()
    test_file = "Giróide 5mm (1).gcode"
    if os.path.exists(test_file):
        layers = parser.parse_file(test_file)
        if layers:
            # export layer 5 just FILL
            success, count = export_layer_to_dxf(layers[5], "test_layer_5_fill.dxf", include_types=['FILL'])
            print(f"Exported {count} fill segments to test_layer_5_fill.dxf: {success}")
            
            # export layer 5 all
            success, count = export_layer_to_dxf(layers[5], "test_layer_5_all.dxf")
            print(f"Exported {count} all segments to test_layer_5_all.dxf: {success}")
