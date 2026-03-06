import re
import os

class GCodeLayer:
    def __init__(self, index):
        self.index = index
        self.z_height = None
        # segments: dict of {type: [((x1,y1), (x2,y2)), ...]}
        self.segments_by_type = {}

    def add_segment(self, path_type, p1, p2):
        if path_type not in self.segments_by_type:
            self.segments_by_type[path_type] = []
        self.segments_by_type[path_type].append((p1, p2))

    def __repr__(self):
        return f"Layer {self.index} (Z={self.z_height}) - {sum(len(v) for v in self.segments_by_type.values())} segments"

class GCodeParser:
    def __init__(self):
        self.layers = []
        
        # coordinate tracking
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.e = 0.0
        
        self.is_absolute_e = True
        
        self.current_layer = None
        self.current_type = "UNKNOWN"
        self.layer_height = None

    def parse_file(self, filepath):
        self.layers = []
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.e = 0.0
        self.current_layer = None
        self.current_type = "UNKNOWN"
        self.is_absolute_e = True
        self.layer_height = None

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"GCode file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                self._parse_line(line.strip())
                
        # Return only layers that have some segments or Z height
        valid_layers = [lyr for lyr in self.layers if lyr.z_height is not None or len(lyr.segments_by_type) > 0]
        return valid_layers

    def _parse_line(self, line):
        if not line:
            return
            
        # Ignore comments but process some specific ones like ;LAYER, ;TYPE, ;Layer height
        if line.startswith(';'):
            upper_line = line.upper()
            if upper_line.startswith(';LAYER:'):
                try:
                    layer_idx = int(upper_line.split(':')[1])
                    self.current_layer = GCodeLayer(layer_idx)
                    self.layers.append(self.current_layer)
                except ValueError:
                    pass
            elif upper_line.startswith(';TYPE:'):
                self.current_type = upper_line.split(':')[1].strip()
            elif upper_line.startswith(';LAYER HEIGHT:'):
                try:
                    self.layer_height = float(upper_line.split(':')[1])
                except ValueError:
                    pass
            return
            
        # Strip inline comments
        if ';' in line:
            line = line.split(';')[0].strip()
            
        parts = line.split()
        if not parts:
            return
            
        cmd = parts[0].upper()
        
        if cmd == 'M82':
            self.is_absolute_e = True
        elif cmd == 'M83':
            self.is_absolute_e = False
        elif cmd == 'G92':
            # Reset coordinates
            for p in parts[1:]:
                upper_p = p.upper()
                if upper_p.startswith('E'):
                    self.e = float(upper_p[1:])
                elif upper_p.startswith('X'):
                    self.x = float(upper_p[1:])
                elif upper_p.startswith('Y'):
                    self.y = float(upper_p[1:])
                elif upper_p.startswith('Z'):
                    self.z = float(upper_p[1:])
        elif cmd in ('G0', 'G1'):
            # Move command
            new_x = self.x
            new_y = self.y
            new_z = self.z
            new_e = self.e
            
            x_moved = False
            y_moved = False
            is_extruding = False
            
            for p in parts[1:]:
                upper_p = p.upper()
                try:
                    val = float(upper_p[1:])
                    if upper_p.startswith('X'):
                        new_x = val
                        x_moved = True
                    elif upper_p.startswith('Y'):
                        new_y = val
                        y_moved = True
                    elif upper_p.startswith('Z'):
                        new_z = val
                    elif upper_p.startswith('E'):
                        if self.is_absolute_e:
                            if val > self.e:
                                is_extruding = True
                            new_e = val
                        else:
                            if val > 0:
                                is_extruding = True
                            new_e = self.e + val # actually keep it absolute internally
                except ValueError:
                    pass
            
            # If moving and extruding, add segment
            if (x_moved or y_moved) and is_extruding:
                if self.current_layer is not None:
                    # Update layer Z only when extruding to avoid recording Z-hops or end script raises
                    if self.current_layer.z_height is None:
                        self.current_layer.z_height = self.z
                        
                    p1 = (self.x, self.y)
                    p2 = (new_x, new_y)
                    # Only add if we actually moved
                    if p1 != p2:
                        self.current_layer.add_segment(self.current_type, p1, p2)
            
            # Update state
            self.x = new_x
            self.y = new_y
            self.z = new_z
            self.e = new_e

if __name__ == "__main__":
    # Test
    parser = GCodeParser()
    test_file = "Giróide 5mm (1).gcode"
    if os.path.exists(test_file):
        layers = parser.parse_file(test_file)
        print(f"Parsed {len(layers)} layers.")
        for layer in layers[:5]:
            print(layer)
            for t, segs in layer.segments_by_type.items():
                print(f"  Type {t}: {len(segs)} segments")
