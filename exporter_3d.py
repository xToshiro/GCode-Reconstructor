import trimesh
from shapely.geometry import LineString, Polygon, MultiLineString
from shapely.ops import unary_union, linemerge
import numpy as np
import math

def generate_3d_mesh(layers, include_types, nozzle_width, fallback_layer_height=0.4, tubular=False, progress_callback=None):
    """
    Generates a single 3D trimesh object from GCode layers.
    """
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
            
        lines = []
        for path_type, segments in layer.segments_by_type.items():
            if include_types is not None and path_type not in include_types:
                continue
            for p1, p2 in segments:
                lines.append((p1, p2))
                
        if not lines:
            continue
            
        if tubular:
            # Generate continuous tubular sweeps
            # First, convert line segments to LineStrings
            shapely_lines = [LineString([p1, p2]) for p1, p2 in lines]
            # Merge into continuous paths
            merged = linemerge(shapely_lines)
            lines2d = [merged] if type(merged) == LineString else list(merged.geoms)
            
            # Create the 2D elliptical profile
            profile = trimesh.path.creation.circle(radius=radius)
            transform = np.eye(3)
            # Squash the circle vertically to match layer_thickness
            scale_z = layer_thickness / nozzle_width
            transform[1, 1] = scale_z
            profile.apply_transform(transform)
            poly_profile = profile.polygons_full[0]
            
            # Sweep along each path
            z_center = z_base + layer_thickness / 2.0
            for ls in lines2d:
                pts = np.array(ls.coords)
                # Convert 2D coords to 3D coords
                pts3d = np.zeros((len(pts), 3))
                pts3d[:, 0] = pts[:, 0]
                pts3d[:, 1] = pts[:, 1]
                # sweep_polygon builds around the path.
                try:
                    tube_mesh = trimesh.creation.sweep_polygon(poly_profile, pts3d)
                    tube_mesh.apply_translation((0, 0, z_center))
                    all_meshes.append(tube_mesh)
                except Exception as e:
                    print(f"Skipping tube sweep due to error: {e}")
        else:
            # Standard flat extrusion logic using shapely polygons
            shapely_lines = [LineString([p1, p2]) for p1, p2 in lines]
            buffered_lines = [line.buffer(radius, cap_style=1, join_style=1) for line in shapely_lines]
    
            # Union all polygons in this layer to avoid internal self-intersections
            layer_polygon = unary_union(buffered_lines)
            
            polys_to_extrude = []
            if type(layer_polygon) == Polygon:
                polys_to_extrude.append(layer_polygon)
            else: # MultiPolygon
                polys_to_extrude.extend(list(layer_polygon.geoms))
                
            for poly in polys_to_extrude:
                # Extrude 2D polygon to 3D mesh
                try:
                    mesh = trimesh.creation.extrude_polygon(poly, height=layer_thickness)
                    # Translate it to the correct Z height
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

def export_3d_model(layers, output_path, include_types=None, nozzle_width=0.4, layer_height=0.4, tubular=False, progress_callback=None):
    """
    Exports layers to a 3D file (STL/OBJ/STEP).
    """
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
                    if include_types is not None and path_type not in include_types:
                        continue
                    for p1, p2 in segments:
                        lines.append(LineString([p1, p2]))
                        
                if not lines:
                    continue
                    
                buffered_lines = [line.buffer(radius, cap_style=1, join_style=1) for line in lines]
                layer_polygon = unary_union(buffered_lines)
                
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
            mesh = generate_3d_mesh(layers, include_types, nozzle_width, layer_height, tubular=tubular, progress_callback=progress_callback)
            if mesh is None:
                return False, "No geometry generated (maybe no segments matched the types)."
                
            mesh.merge_vertices()
            mesh.export(output_path)
            return True, "Exported Successfully"
            
    except Exception as e:
        return False, str(e)

