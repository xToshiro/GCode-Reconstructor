import trimesh
from shapely.geometry import LineString, Polygon, MultiLineString
from shapely.ops import unary_union, linemerge
import numpy as np
import math

def create_ellipse_profile(w, h, resolution=8):
    """
    Creates an elliptical profile centered at (0,0) with width w and height h.
    resolution controls the number of segments per quadrant. Total vertices = 4 * resolution.
    """
    angles = np.linspace(0, 2 * np.pi, 4 * resolution, endpoint=False)
    x = (w / 2.0) * np.cos(angles)
    y = (h / 2.0) * np.sin(angles)
    return Polygon(np.column_stack((x, y)))

def create_stadium_profile(w, h, resolution=8):
    """
    Creates a stadium profile centered at (0,0) with total width w and total height h.
    The top and bottom are flat lines. The left and right ends are semicircles of radius h/2.
    resolution controls the number of segments in each semicircular end.
    Total vertices = 4 * resolution.
    """
    if w <= h:
        return create_ellipse_profile(w, h, resolution)
        
    r = h / 2.0
    d = w / 2.0 - r
    
    # Right semicircle (from -pi/2 to pi/2)
    theta_right = np.linspace(-np.pi/2, np.pi/2, 2 * resolution)
    x_right = d + r * np.cos(theta_right)
    y_right = r * np.sin(theta_right)
    
    # Left semicircle (from pi/2 to 3*pi/2)
    theta_left = np.linspace(np.pi/2, 1.5 * np.pi, 2 * resolution)
    x_left = -d + r * np.cos(theta_left)
    y_left = r * np.sin(theta_left)
    
    x = np.concatenate([x_right, x_left])
    y = np.concatenate([y_right, y_left])
    return Polygon(np.column_stack((x, y)))

def generate_3d_mesh(layers, simulation_types, nozzle_width, fallback_layer_height=0.4, resolution=8, progress_callback=None):
    """
    Generates a single 3D trimesh object from GCode layers.
    """
    if simulation_types is None:
        simulation_types = {}
        
    # Half width for the buffer
    radius = nozzle_width / 2.0
    
    # We will collect a trimesh representation for each layer and then concatenate them
    all_meshes = []
    
    # Determine the lowest Z in the entire file to avoid the floating layer issue
    min_z = min([l.z_height for l in layers if l.z_height is not None], default=0.0)
    
    for i, layer in enumerate(layers):
        if progress_callback:
            progress_callback(i, len(layers))
        layer_thickness = fallback_layer_height
        z_base = (layer.z_height - min_z)
        if z_base < 0:
            z_base = 0.0
            
        lines_by_style = {'line': [], 'square': [], 'tubular': [], 'stadium': []}
        for path_type, segments in layer.segments_by_type.items():
            if path_type not in simulation_types:
                continue
            sim_type = simulation_types.get(path_type, 'line')
            if sim_type not in lines_by_style:
                sim_type = 'line'
            for p1, p2 in segments:
                lines_by_style[sim_type].append((p1, p2))
                
        # Tubular processing
        if lines_by_style['tubular']:
            shapely_lines = [LineString([p1, p2]) for p1, p2 in lines_by_style['tubular']]
            merged = linemerge(shapely_lines)
            lines2d = [merged] if type(merged) == LineString else list(merged.geoms)
            
            poly_profile = create_ellipse_profile(nozzle_width, layer_thickness, resolution)
            z_center = z_base + layer_thickness / 2.0
            for ls in lines2d:
                pts = np.array(ls.coords)
                pts3d = np.zeros((len(pts), 3))
                pts3d[:, 0] = pts[:, 0]
                pts3d[:, 1] = pts[:, 1]
                try:
                    tube_mesh = trimesh.creation.sweep_polygon(poly_profile, pts3d)
                    tube_mesh.apply_translation((0, 0, z_center))
                    all_meshes.append(tube_mesh)
                except Exception as e:
                    print(f"Skipping tube sweep due to error: {e}")

        # Stadium processing
        if lines_by_style['stadium']:
            shapely_lines = [LineString([p1, p2]) for p1, p2 in lines_by_style['stadium']]
            merged = linemerge(shapely_lines)
            lines2d = [merged] if type(merged) == LineString else list(merged.geoms)
            
            poly_profile = create_stadium_profile(nozzle_width, layer_thickness, resolution)
            z_center = z_base + layer_thickness / 2.0
            for ls in lines2d:
                pts = np.array(ls.coords)
                pts3d = np.zeros((len(pts), 3))
                pts3d[:, 0] = pts[:, 0]
                pts3d[:, 1] = pts[:, 1]
                try:
                    tube_mesh = trimesh.creation.sweep_polygon(poly_profile, pts3d)
                    tube_mesh.apply_translation((0, 0, z_center))
                    all_meshes.append(tube_mesh)
                except Exception as e:
                    print(f"Skipping stadium sweep due to error: {e}")
                    
        # Square and Line processing (In 3D, 'line' acts mostly like 'square')
        flat_lines = lines_by_style['square'] + lines_by_style['line']
        if flat_lines:
            shapely_lines = [LineString([p1, p2]) for p1, p2 in flat_lines]
            merged_lines = linemerge(shapely_lines)
            layer_polygon = merged_lines.buffer(radius, cap_style=2, join_style=3)
            
            polys_to_extrude = []
            if type(layer_polygon) == Polygon:
                polys_to_extrude.append(layer_polygon)
            else:
                polys_to_extrude.extend(list(layer_polygon.geoms))
                
            for poly in polys_to_extrude:
                try:
                    mesh = trimesh.creation.extrude_polygon(poly, height=layer_thickness)
                    mesh.apply_translation((0, 0, z_base))
                    all_meshes.append(mesh)
                except Exception as e:
                    print(f"Skipping a polygon extrusion due to error: {e}")

    if progress_callback:
        progress_callback(len(layers), len(layers))
        
    if not all_meshes:
        return None
        
    # Concatenate all meshes into one
    # This is much faster than boolean union and valid as long as they just stack
    final_mesh = trimesh.util.concatenate(all_meshes)
    return final_mesh

def export_3d_model(layers, output_path, simulation_types=None, nozzle_width=0.4, layer_height=0.4, resolution=8, progress_callback=None):
    """
    Exports layers to a 3D file (STL/OBJ/STEP).
    """
    if simulation_types is None:
        simulation_types = {}
    try:
        is_step = output_path.lower().endswith('.step') or output_path.lower().endswith('.stp')
        
        if is_step:
            # Import build123d only when needed (it's somewhat heavy)
            try:
                import build123d as bd
            except ImportError:
                return False, "Failed to load STEP export library. Please run 'pip install build123d' in the environment."
                
            radius = nozzle_width / 2.0
            min_z = min([l.z_height for l in layers if l.z_height is not None], default=0.0)
            
            parts = []
            
            for layer in layers:
                layer_thickness = layer_height
                lines = []
                for path_type, segments in layer.segments_by_type.items():
                    if path_type not in simulation_types:
                        continue
                    
                    # For STEP, we treat everything as flat extruded paths for simplicity right now
                    for p1, p2 in segments:
                        lines.append(LineString([p1, p2]))
                        
                if not lines:
                    continue
                    
                merged_lines = linemerge(lines)
                layer_polygon = merged_lines.buffer(radius, cap_style=2, join_style=3)
                
                z_base = (layer.z_height - min_z)
                if z_base < 0:
                    z_base = 0.0
                    
                polys_to_extrude = []
                if type(layer_polygon) == Polygon:
                    polys_to_extrude.append(layer_polygon)
                else: 
                    polys_to_extrude.extend(list(layer_polygon.geoms))
                    
                for poly in polys_to_extrude:
                    # External contour
                    ext_coords = list(poly.exterior.coords)
                    # Convert coords to vec2
                    ext_pts = [(c[0], c[1]) for c in ext_coords]
                    
                    with bd.BuildPart() as p:
                        with bd.BuildSketch():
                            bd.Polygon(*ext_pts)
                            # Handle holes if any
                            for interior in poly.interiors:
                                int_pts = [(c[0], c[1]) for c in list(interior.coords)]
                                bd.Polygon(*int_pts, mode=bd.Mode.SUBTRACT)
                        bd.extrude(amount=layer_thickness)
                        
                    # Translate to correct Z
                    trans_part = p.part.locate(bd.Location((0, 0, z_base)))
                    parts.append(trans_part)
                    
            if not parts:
                return False, "No geometry generated."
                
            # Combine all parts
            final_part = parts[0]
            for other_part in parts[1:]:
                final_part = final_part + other_part
                
            bd.export_step(final_part, output_path)
            return True, "Exported STEP Successfully"
            
        else:
            # STL/OBJ fallback using trimesh (faster for meshes)
            mesh = generate_3d_mesh(layers, simulation_types, nozzle_width, layer_height, resolution=resolution, progress_callback=progress_callback)
            if mesh is None:
                return False, "No geometry generated (maybe no segments matched the types)."
                
            mesh.merge_vertices()
            mesh.export(output_path)
            return True, "Exported Successfully"
            
    except Exception as e:
        return False, str(e)

