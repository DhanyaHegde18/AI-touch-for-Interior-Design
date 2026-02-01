"""
design_generator.py
Creates 2D floor plans and 3D room visualizations
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os


class CompleteDesignGenerator:
    """
    Generates complete design visualizations:
    - 2D floor plans
    - 3D room diagrams
    """
    
    def __init__(self):
        """Initialize design generator"""
        # Standard furniture dimensions (width, length, height) in meters
        self.furniture_dims = {
            'bed': (2.0, 1.8, 0.5),
            'couch': (2.2, 0.9, 0.8),
            'sofa': (2.2, 0.9, 0.8),
            'chair': (0.6, 0.6, 0.9),
            'table': (1.2, 0.8, 0.75),
            'nightstand': (0.5, 0.4, 0.6),
            'lamp': (0.3, 0.3, 1.5),
            'frame': (0.05, 1.0, 0.8),
            'curtains': (0.1, 2.5, 2.4),
            'pillow': (0.4, 0.4, 0.2),
            'chandelier': (0.8, 0.8, 0.5),
            'rug': (2.5, 2.0, 0.02),
            'plant': (0.4, 0.4, 0.8),
            'tv': (0.1, 1.2, 0.7),
            'bookshelf': (0.4, 1.5, 2.0),
            'desk': (1.2, 0.6, 0.75),
            'dresser': (1.0, 0.5, 1.2),
        }
    
    def generate_all_designs(self, room_type, current_items, suggested_items, 
                            dimensions=None, base_filename='room'):
        """
        Generate all design visualizations
        
        Args:
            room_type: Type of room (bedroom, living_room, etc.)
            current_items: List of detected furniture
            suggested_items: List of suggested additions
            dimensions: Room dimensions dict (optional)
            base_filename: Base name for output files
            
        Returns:
            dict: Paths to generated files
        """
        
        # Default dimensions if not provided
        if dimensions:
            room_dims = (
                dimensions.get('width_m', 5.0),
                dimensions.get('length_m', 6.0),
                dimensions.get('height_m', 3.0)
            )
        else:
            room_dims = (5.0, 6.0, 3.0)
        
        output_files = {}
        
        # Generate 2D floor plan
        try:
            floor_plan_path = self.generate_2d_floor_plan(
                room_type=room_type,
                current_items=current_items,
                suggested_items=suggested_items,
                room_dims=room_dims,
                output_path=f"{base_filename}_2d_floor.png"
            )
            output_files['2d_floor_plan'] = floor_plan_path
            print(f"✅ 2D Floor Plan: {floor_plan_path}")
        except Exception as e:
            print(f"⚠️ 2D floor plan failed: {e}")
        
        # Generate 3D visualization
        try:
            viz_3d_path = self.generate_3d_visualization(
                room_type=room_type,
                current_items=current_items,
                suggested_items=suggested_items,
                room_dims=room_dims,
                output_path=f"{base_filename}_3d_visual.png"
            )
            output_files['3d_visualization'] = viz_3d_path
            print(f"✅ 3D Visualization: {viz_3d_path}")
        except Exception as e:
            print(f"⚠️ 3D visualization failed: {e}")
        
        return output_files
    
    def generate_2d_floor_plan(self, room_type, current_items, suggested_items, 
                               room_dims, output_path='2d_floor_plan.png'):
        """Generate 2D floor plan"""
        
        # Create canvas
        canvas_size = (1200, 900)
        img = Image.new('RGB', canvas_size, 'white')
        draw = ImageDraw.Draw(img)
        
        # Room outline
        padding = 100
        room_rect = [
            padding, 
            padding + 80,
            canvas_size[0] - padding,
            canvas_size[1] - padding
        ]
        draw.rectangle(room_rect, outline='black', width=4)
        
        # Title
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font_title = ImageFont.load_default()
            font_label = ImageFont.load_default()
        
        title = f"2D Floor Plan: {room_type.replace('_', ' ').title()}"
        draw.text((canvas_size[0]//2 - 150, 30), title, fill='black', font=font_title)
        
        # Draw furniture
        room_width = room_rect[2] - room_rect[0]
        room_height = room_rect[3] - room_rect[1]
        
        scale_x = room_width / room_dims[0]
        scale_y = room_height / room_dims[1]
        
        positions = []
        
        # Draw current furniture (blue)
        for item in current_items:
            dims = self.furniture_dims.get(item, (0.5, 0.5, 0.5))
            
            # Find non-overlapping position
            for _ in range(20):
                x = np.random.randint(room_rect[0] + 20, room_rect[2] - int(dims[0]*scale_x) - 20)
                y = np.random.randint(room_rect[1] + 20, room_rect[3] - int(dims[1]*scale_y) - 20)
                
                w = int(dims[0] * scale_x)
                h = int(dims[1] * scale_y)
                
                # Check overlap
                overlap = False
                for px, py, pw, ph in positions:
                    if not (x + w < px or x > px + pw or y + h < py or y > py + ph):
                        overlap = True
                        break
                
                if not overlap:
                    draw.rectangle([x, y, x+w, y+h], fill='lightblue', outline='blue', width=2)
                    draw.text((x+5, y+5), item, fill='darkblue', font=font_label)
                    positions.append((x, y, w, h))
                    break
        
        # Draw suggested furniture (orange)
        for item in suggested_items[:6]:
            dims = self.furniture_dims.get(item, (0.5, 0.5, 0.5))
            
            for _ in range(20):
                x = np.random.randint(room_rect[0] + 20, room_rect[2] - int(dims[0]*scale_x) - 20)
                y = np.random.randint(room_rect[1] + 20, room_rect[3] - int(dims[1]*scale_y) - 20)
                
                w = int(dims[0] * scale_x)
                h = int(dims[1] * scale_y)
                
                overlap = False
                for px, py, pw, ph in positions:
                    if not (x + w < px or x > px + pw or y + h < py or y > py + ph):
                        overlap = True
                        break
                
                if not overlap:
                    draw.rectangle([x, y, x+w, y+h], fill='lightyellow', outline='orange', width=2)
                    draw.text((x+5, y+5), f"{item}\n(suggested)", fill='darkorange', font=font_label)
                    positions.append((x, y, w, h))
                    break
        
        # Legend
        legend_y = canvas_size[1] - 60
        draw.rectangle([120, legend_y, 170, legend_y+30], fill='lightblue', outline='blue', width=2)
        draw.text((180, legend_y+5), "Current Furniture", fill='black', font=font_label)
        
        draw.rectangle([400, legend_y, 450, legend_y+30], fill='lightyellow', outline='orange', width=2)
        draw.text((460, legend_y+5), "Suggested Items", fill='black', font=font_label)
        
        # Save
        img.save(output_path)
        return output_path
    
    def generate_3d_visualization(self, room_type, current_items, suggested_items,
                                  room_dims, output_path='3d_visualization.png'):
        """Generate 3D room visualization"""
        
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        room_w, room_l, room_h = room_dims
        
        # Draw floor
        floor = Poly3DCollection([[(0,0,0), (room_w,0,0), (room_w,room_l,0), (0,room_l,0)]], 
                                alpha=0.3, facecolor='tan', edgecolor='black', linewidth=1.5)
        ax.add_collection3d(floor)
        
        # Draw walls
        walls = [
            [(0,0,0), (room_w,0,0), (room_w,0,room_h), (0,0,room_h)],
            [(0,room_l,0), (room_w,room_l,0), (room_w,room_l,room_h), (0,room_l,room_h)],
            [(0,0,0), (0,room_l,0), (0,room_l,room_h), (0,0,room_h)],
            [(room_w,0,0), (room_w,room_l,0), (room_w,room_l,room_h), (room_w,0,room_h)]
        ]
        
        for wall in walls:
            w = Poly3DCollection([wall], alpha=0.1, facecolor='lightgray', 
                                edgecolor='black', linewidth=1)
            ax.add_collection3d(w)
        
        # Grid lines
        for i in np.linspace(0, room_h, 6):
            ax.plot([0, room_w], [0, 0], [i, i], 'gray', alpha=0.2, linewidth=0.5)
            ax.plot([0, room_w], [room_l, room_l], [i, i], 'gray', alpha=0.2, linewidth=0.5)
        
        positions = []
        
        # Draw current furniture (orange)
        for item in current_items:
            dims = self.furniture_dims.get(item, (0.5, 0.5, 0.5))
            pos = self._find_position(dims, room_dims, positions, item)
            
            furniture = self._create_box(pos, dims, 'darkorange', 0.8)
            ax.add_collection3d(furniture)
            
            ax.text(pos[0], pos[1], pos[2] + dims[2] + 0.1, 
                   item.capitalize(), fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            positions.append((pos[0], pos[1], dims[0], dims[1], item))
        
        # Draw suggested furniture (wheat)
        for item in suggested_items[:6]:
            dims = self.furniture_dims.get(item, (0.5, 0.5, 0.5))
            pos = self._find_position(dims, room_dims, positions, item, True)
            
            furniture = self._create_box(pos, dims, 'wheat', 0.6)
            ax.add_collection3d(furniture)
            
            ax.text(pos[0], pos[1], pos[2] + dims[2] + 0.1, 
                   f"{item.capitalize()}\n(suggested)", fontsize=8, style='italic',
                   bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
            
            positions.append((pos[0], pos[1], dims[0], dims[1], item))
        
        # Labels
        ax.set_xlabel('Width (m)', fontsize=11)
        ax.set_ylabel('Length (m)', fontsize=11)
        ax.set_zlabel('Height (m)', fontsize=11)
        
        ax.set_xlim(0, room_w)
        ax.set_ylim(0, room_l)
        ax.set_zlim(0, room_h)
        
        # Title
        title = f'3D View: {room_type.replace("_", " ").title()}\n{room_w:.1f}m × {room_l:.1f}m × {room_h:.1f}m'
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='darkorange', label='Current Furniture'),
            Patch(facecolor='wheat', label='Suggested Items')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        ax.view_init(elev=25, azim=45)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _create_box(self, position, size, color, alpha=0.7):
        """Create 3D box for furniture"""
        x, y, z = position
        dx, dy, dz = size
        
        vertices = [
            [x, y, z], [x+dx, y, z], [x+dx, y+dy, z], [x, y+dy, z],
            [x, y, z+dz], [x+dx, y, z+dz], [x+dx, y+dy, z+dz], [x, y+dy, z+dz]
        ]
        
        faces = [
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[2], vertices[3], vertices[7], vertices[6]],
            [vertices[0], vertices[3], vertices[7], vertices[4]],
            [vertices[1], vertices[2], vertices[6], vertices[5]],
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]]
        ]
        
        return Poly3DCollection(faces, facecolors=color, edgecolors='black', 
                               alpha=alpha, linewidths=0.5)
    
    def _find_position(self, dims, room_dims, positions, item_type, is_suggested=False):
        """Find non-overlapping position for furniture"""
        room_w, room_l, room_h = room_dims
        fw, fl, fh = dims
        
        # Special placement rules
        if item_type == 'curtains':
            return (room_w - 0.15, 0.2, room_h - fh)
        elif item_type == 'frame':
            return (0.05, room_l/2, 1.5)
        elif item_type == 'chandelier':
            return (room_w/2 - fw/2, room_l/2 - fl/2, room_h - fh - 0.2)
        elif item_type == 'rug':
            return (room_w/2 - fw/2, room_l/2 - fl/2, 0.01)
        elif item_type in ['bed', 'couch', 'sofa']:
            return (0.3, 0.5, 0) if not is_suggested else (room_w - fw - 0.3, room_l/2, 0)
        elif item_type == 'table':
            return (room_w/2 - fw/2, room_l/2 - fl/2, 0)
        
        # Random placement for other items
        for _ in range(30):
            x = np.random.uniform(0.4, room_w - fw - 0.4)
            y = np.random.uniform(0.4, room_l - fl - 0.4)
            z = 0
            
            overlap = False
            for ex, ey, ew, el, _ in positions:
                if (x < ex + ew + 0.2 and x + fw + 0.2 > ex and 
                    y < ey + el + 0.2 and y + fl + 0.2 > ey):
                    overlap = True
                    break
            
            if not overlap:
                return (x, y, z)
        
        return (0.5, 0.5, 0)


# Test function
if __name__ == "__main__":
    print("="*70)
    print("🎨 DESIGN GENERATOR TEST")
    print("="*70)
    
    generator = CompleteDesignGenerator()
    
    # Test data
    current_items = ['couch', 'table', 'chair', 'lamp']
    suggested_items = ['rug', 'plant', 'bookshelf', 'frame']
    
    dimensions = {
        'width_m': 5.0,
        'length_m': 6.0,
        'height_m': 3.0
    }
    
    print("\nGenerating designs...")
    
    files = generator.generate_all_designs(
        room_type='living_room',
        current_items=current_items,
        suggested_items=suggested_items,
        dimensions=dimensions,
        base_filename='test_room'
    )
    
    print("\n" + "="*70)
    print("✅ DESIGN GENERATION COMPLETE")
    print("="*70)
    
    for file_type, file_path in files.items():
        print(f"📁 {file_type}: {file_path}")