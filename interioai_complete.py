"""
InterioAI Complete System - LOCAL STABLE DIFFUSION VERSION
✅ 100% FREE (runs on your computer)
✅ Uses user preferences (room type, style, colors)
✅ Cost in Indian Rupees (₹)
"""

from ultralytics import YOLO
from suggestion_engine import InteriorSuggestionEngine
from cost_estimator import CostEstimator
from dimension_estimator import DimensionEstimator
from design_generator import CompleteDesignGenerator
from image_to_image_renderer import ImageToImageRenderer
import os
import sys
from PIL import Image


class InterioAI:
    """
    Complete Interior Design AI System - LOCAL STABLE DIFFUSION
    ✅ 100% FREE - runs on your computer
    ✅ User preferences (room type, style, colors)
    ✅ Cost in Indian Rupees
    """
    
    USD_TO_INR = 83.0
    
    def __init__(self, model_path='runs/detect/train/weights/best.pt', 
                 enable_dimensions=True, dimension_model='MiDaS_small'):
        """Initialize all components"""
        print("🏠 Initializing InterioAI System...")
        print("   API Provider: Local Stable Diffusion (FREE)")
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found at: {model_path}")
            sys.exit(1)
        
        self.model = YOLO(model_path)
        print(f"✅ Detection model loaded")
        
        self.suggestion_engine = InteriorSuggestionEngine()
        self.cost_estimator = CostEstimator()
        self.design_generator = CompleteDesignGenerator()
        
        # Initialize Local Stable Diffusion renderer
        self.image_editor = ImageToImageRenderer()
        
        self.dimension_estimator = None
        if enable_dimensions:
            try:
                self.dimension_estimator = DimensionEstimator(model_type=dimension_model)
            except Exception as e:
                print(f"⚠️ Could not load dimension estimator: {e}")
        
        print("✅ All components initialized!")
        print("="*60)
    
    def analyze_room(self, image_path, budget_level='mid-range', 
                     estimate_dimensions=True, generate_design=False,
                     edit_image=True, edit_strength=0.75, create_comparison=True,
                     user_room_type=None, user_style=None, user_palette=None, 
                     user_furniture_prefs=None):
        """
        Complete room analysis with USER preferences
        
        Args:
            image_path: Path to room image
            budget_level: 'budget', 'mid-range', or 'premium'
            estimate_dimensions: Whether to estimate dimensions
            generate_design: Whether to generate 2D/3D diagrams
            edit_image: Whether to edit with AI
            edit_strength: 0.65-0.85 (higher = more changes)
            create_comparison: Whether to create before/after
            user_room_type: User's room type
            user_style: User's style
            user_palette: User's color preference
            user_furniture_prefs: User's furniture preferences
            
        Returns:
            dict: Complete analysis results with costs in INR
        """
        print(f"\n🔍 Analyzing: {os.path.basename(image_path)}")
        print("="*60)
        
        # Step 1: Detect furniture
        print("\n📸 Step 1: Detecting existing furniture...")
        detected_objects = self._detect_furniture(image_path)
        
        if not detected_objects:
            print("⚠️  No furniture detected - will furnish room")
        else:
            print(f"✅ Detected {len(detected_objects)} items: {', '.join(detected_objects)}")
        
        # Step 2: Estimate dimensions
        dimensions = None
        if estimate_dimensions and self.dimension_estimator:
            print("\n📐 Step 2: Estimating room dimensions...")
            try:
                dimensions = self.dimension_estimator.estimate_dimensions(image_path)
                if dimensions:
                    print(f"✅ Dimensions: {dimensions['length_m']:.1f}m × {dimensions['width_m']:.1f}m × {dimensions['height_m']:.1f}m")
                    print(f"   Area: {dimensions['floor_area_sqft']:.0f} sq ft")
            except Exception as e:
                print(f"⚠️ Dimension estimation failed: {e}")
        
        # Step 3: Generate suggestions
        step_num = 3 if dimensions else 2
        print(f"\n💡 Step {step_num}: Generating suggestions for YOUR design...")
        
        if user_room_type:
            print(f"   Using your room type: {user_room_type}")
            room_type_map = {
                'Living Hall': 'living_room',
                'Living Room': 'living_room',
                'Bedroom': 'bedroom',
                'Kitchen': 'kitchen',
                'Bathroom': 'bathroom',
                'Pooja Room': 'living_room',
                'Dining Room': 'dining_room',
                'Office': 'office',
                'Study Room': 'office'
            }
            mapped_room_type = room_type_map.get(user_room_type, 'living_room')
        else:
            mapped_room_type = None
        
        analysis = self.suggestion_engine.analyze_room(
            detected_objects, 
            force_room_type=mapped_room_type
        )
        
        if user_room_type:
            analysis['room_type'] = user_room_type.lower().replace(' ', '_')
        if user_style:
            analysis['current_style'] = user_style
        
        print(f"✅ Room Type: {user_room_type or analysis['room_type']}")
        print(f"✅ Style: {user_style or analysis['current_style']}")
        if user_palette:
            print(f"✅ Color Palette: {user_palette}")
        
        if not analysis['suggestions']['add_items'] or len(detected_objects) == 0:
            print("   ℹ️  Adding essential furniture for room type...")
            analysis['suggestions']['add_items'] = self._get_essential_furniture(
                user_room_type or analysis['room_type'],
                user_style or analysis['current_style']
            )
        
        print(f"✅ Suggestions: {len(analysis['suggestions']['add_items'])} items")
        if analysis['suggestions']['add_items']:
            print(f"   Items: {', '.join(analysis['suggestions']['add_items'][:5])}")
        
        # Step 4: Generate Designs (OPTIONAL)
        step_num += 1
        design_files = None
        if generate_design:
            print(f"\n🎨 Step {step_num}: Creating diagrams...")
            try:
                base_filename = os.path.splitext(os.path.basename(image_path))[0]
                design_files = self.design_generator.generate_all_designs(
                    room_type=analysis['room_type'],
                    current_items=detected_objects,
                    suggested_items=analysis['suggestions']['add_items'],
                    dimensions=dimensions,
                    base_filename=base_filename
                )
            except Exception as e:
                print(f"⚠️ Design generation failed: {e}")
        
        # Step 5: Edit Image with Local Stable Diffusion
        step_num += 1
        edited_image = None
        comparison_image = None
        
        if edit_image and analysis['suggestions']['add_items']:
            print(f"\n✨ Step {step_num}: Creating photorealistic design (Local SD)...")
            if user_style:
                print(f"   Applying {user_style} style")
            if user_palette:
                print(f"   Using {user_palette} color scheme")
            
            try:
                base_filename = os.path.splitext(os.path.basename(image_path))[0]
                edited_filename = f"{base_filename}_designed.png"
                
                room_data = {
                    'room_type': user_room_type or analysis['room_type'],
                    'style': user_style or analysis['current_style'],
                    'palette': user_palette or '',
                    'furniture_prefs': user_furniture_prefs or '',
                    'suggested_items': analysis['suggestions']['add_items'][:6],
                    'is_empty': len(detected_objects) == 0
                }
                
                edited_image = self.image_editor.edit_room_image(
                    original_image_path=image_path,
                    room_data=room_data,
                    output_path=edited_filename,
                    strength=edit_strength if detected_objects else 0.80
                )
                
                if edited_image and create_comparison:
                    comparison_filename = f"{base_filename}_before_after.png"
                    comparison_image = self.image_editor.create_comparison(
                        original_path=image_path,
                        edited_path=edited_image,
                        output_path=comparison_filename
                    )
                
            except Exception as e:
                print(f"⚠️ Image editing failed: {e}")
        
        # Step 6: Calculate costs in INR
        step_num += 1
        print(f"\n💰 Step {step_num}: Calculating costs in Indian Rupees...")
        suggested_items = analysis['suggestions']['add_items']
        
        if suggested_items:
            cost_breakdown = self.cost_estimator.estimate_cost(suggested_items, budget_level)
            cost_breakdown_inr = self._convert_to_inr(cost_breakdown)
            print(f"✅ Estimated cost ({budget_level}): ₹{cost_breakdown_inr['total']:,.2f}")
        else:
            cost_breakdown_inr = None
            print("ℹ️  No new items to estimate")
        
        # Compile results
        results = {
            'image_path': image_path,
            'detected_objects': detected_objects,
            'dimensions': dimensions,
            'analysis': analysis,
            'design_files': design_files,
            'edited_image': edited_image,
            'comparison_image': comparison_image,
            'cost_breakdown': cost_breakdown_inr,
            'user_preferences': {
                'room_type': user_room_type,
                'style': user_style,
                'palette': user_palette,
                'furniture_prefs': user_furniture_prefs
            }
        }
        
        print("\n✅ Analysis complete!")
        return results
    
    def _convert_to_inr(self, cost_breakdown):
        """Convert cost breakdown from USD to INR"""
        if not cost_breakdown:
            return None
        
        inr_breakdown = {
            'items': [],
            'subtotal': cost_breakdown['subtotal'] * self.USD_TO_INR,
            'installation': cost_breakdown['installation'] * self.USD_TO_INR,
            'total': cost_breakdown['total'] * self.USD_TO_INR
        }
        
        for item in cost_breakdown['items']:
            inr_breakdown['items'].append({
                'name': item['name'],
                'cost': item['cost'] * self.USD_TO_INR,
                'quantity': item['quantity']
            })
        
        return inr_breakdown
    
    def _detect_furniture(self, image_path):
        """Detect furniture in image"""
        try:
            test_img = Image.open(image_path)
            test_img.verify()
            test_img = Image.open(image_path)
            
            if test_img.mode != 'RGB':
                test_img = test_img.convert('RGB')
                temp_path = image_path.replace('.jpg', '_temp.jpg').replace('.png', '_temp.png')
                test_img.save(temp_path)
                image_path = temp_path
            
            results = self.model.predict(image_path, conf=0.15, imgsz=640, verbose=False)
            
            detected_objects = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    detected_objects.append(class_name)
            
            return detected_objects
            
        except Exception as e:
            print(f"⚠️  Detection error: {e}")
            return []
    
    def _get_essential_furniture(self, room_type, style='modern'):
        """Get essential furniture based on room type and style"""
        
        furniture_sets = {
            'bedroom': ['bed', 'nightstand', 'dresser', 'wardrobe', 'reading lamp', 'rug'],
            'kitchen': ['dining table', 'chairs', 'bar stools', 'pendant lights', 'kitchen island'],
            'living_room': ['sofa', 'coffee table', 'armchair', 'TV stand', 'side table', 'floor lamp'],
            'living_hall': ['sofa', 'coffee table', 'armchair', 'TV stand', 'side table', 'floor lamp'],
            'bathroom': ['vanity', 'mirror', 'storage cabinet', 'towel rack', 'bath mat'],
            'pooja_room': ['puja shelf', 'deity idols', 'diya stand', 'prayer mat', 'incense holder'],
            'dining_room': ['dining table', 'dining chairs', 'sideboard', 'pendant light', 'centerpiece'],
            'office': ['desk', 'office chair', 'bookshelf', 'desk lamp', 'filing cabinet'],
            'study_room': ['study desk', 'chair', 'bookshelf', 'desk lamp', 'storage cabinet']
        }
        
        base_furniture = furniture_sets.get(room_type.lower(), furniture_sets['living_room'])
        
        if style.lower() == 'indian':
            if 'pooja' in room_type.lower():
                base_furniture = ['wooden puja mandir', 'brass diya', 'prayer bells', 'incense stand', 'deity idols', 'prayer mat']
            else:
                base_furniture = base_furniture[:4] + ['traditional rug', 'ethnic wall art']
        
        return base_furniture[:6]
    
    def generate_complete_report(self, results, output_file='interioai_report.txt'):
        """Generate report with INR costs"""
        if not results:
            return None
        
        report_lines = []
        
        report_lines.append("="*70)
        report_lines.append("🏠 INTERIOAI - ROOM DESIGN REPORT")
        report_lines.append("="*70)
        report_lines.append(f"\n📁 Image: {os.path.basename(results['image_path'])}")
        report_lines.append(f"📅 Date: {self._get_timestamp()}")
        report_lines.append(f"🎨 API Provider: Local Stable Diffusion (FREE)")
        
        if results.get('user_preferences'):
            prefs = results['user_preferences']
            report_lines.append("\n" + "="*70)
            report_lines.append("YOUR DESIGN PREFERENCES")
            report_lines.append("="*70)
            if prefs.get('room_type'):
                report_lines.append(f"Room Type: {prefs['room_type']}")
            if prefs.get('style'):
                report_lines.append(f"Style: {prefs['style']}")
            if prefs.get('palette'):
                report_lines.append(f"Color Palette: {prefs['palette']}")
        
        report_lines.append("\n" + "="*70)
        report_lines.append("DETECTED FURNITURE")
        report_lines.append("="*70)
        if results['detected_objects']:
            for i, item in enumerate(results['detected_objects'], 1):
                report_lines.append(f"{i}. {item.title()}")
        else:
            report_lines.append("No furniture detected")
        
        if results.get('dimensions'):
            report_lines.append("\n" + "="*70)
            report_lines.append("ROOM DIMENSIONS")
            report_lines.append("="*70)
            dim = results['dimensions']
            report_lines.append(f"Length: {dim['length_m']:.1f} m")
            report_lines.append(f"Width: {dim['width_m']:.1f} m")
            report_lines.append(f"Height: {dim['height_m']:.1f} m")
            report_lines.append(f"Area: {dim['floor_area_sqft']:.0f} sq ft")
        
        if results['analysis']['suggestions']['add_items']:
            report_lines.append("\n" + "="*70)
            report_lines.append("SUGGESTED FURNITURE")
            report_lines.append("="*70)
            for i, item in enumerate(results['analysis']['suggestions']['add_items'], 1):
                report_lines.append(f"{i}. {item.title()}")
        
        if results['cost_breakdown']:
            report_lines.append("\n" + "="*70)
            report_lines.append("COST ESTIMATE (Indian Rupees)")
            report_lines.append("="*70)
            
            for item in results['cost_breakdown']['items']:
                report_lines.append(f"{item['name']}: ₹{item['cost']:,.2f}")
            
            report_lines.append(f"\nSubtotal: ₹{results['cost_breakdown']['subtotal']:,.2f}")
            report_lines.append(f"Installation: ₹{results['cost_breakdown']['installation']:,.2f}")
            report_lines.append(f"TOTAL: ₹{results['cost_breakdown']['total']:,.2f}")
        
        report_lines.append("\n" + "="*70)
        report_lines.append("GENERATED FILES")
        report_lines.append("="*70)
        
        if results.get('edited_image'):
            report_lines.append(f"✅ Photorealistic Design: {results['edited_image']}")
        if results.get('comparison_image'):
            report_lines.append(f"✅ Before/After: {results['comparison_image']}")
        
        report_lines.append("\n" + "="*70)
        report_lines.append("Thank you for using InterioAI!")
        report_lines.append("100% FREE - Local Stable Diffusion")
        report_lines.append("="*70)
        
        report_content = "\n".join(report_lines)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return output_file
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Main execution
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("✨ INTERIOAI - LOCAL STABLE DIFFUSION VERSION")
    print("="*70)
    print("✅ 100% FREE - runs on your computer")
    print("   No API costs, no credits needed!")
    
    # Initialize InterioAI
    ai = InterioAI(
        model_path='runs/detect/train/weights/best.pt',
        enable_dimensions=True,
        dimension_model='MiDaS_small'
    )
    
    print("\n" + "="*70)
    print("🏠 ROOM DESIGN WITH YOUR PREFERENCES")
    print("="*70)
    
    # Get image
    default_image = 'images/img2.jpg'
    print(f"\nDefault image: {default_image}")
    user_image = input("Enter image path (or press Enter): ").strip()
    image_path = user_image if user_image else default_image
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    # Validate image
    try:
        test_img = Image.open(image_path)
        test_img.verify()
        test_img.close()
        print(f"✅ Image validated")
    except Exception as e:
        print(f"❌ Cannot read image: {e}")
        sys.exit(1)
    
    # GET USER PREFERENCES
    print("\n" + "="*70)
    print("YOUR DESIGN PREFERENCES")
    print("="*70)
    
    print("\n1. Room Type:")
    print("   a) Living Hall")
    print("   b) Bedroom")
    print("   c) Kitchen")
    print("   d) Bathroom")
    print("   e) Pooja Room")
    
    room_choice = input("\nSelect (a-e) or press Enter for Living Hall: ").strip().lower()
    room_map = {
        'a': 'Living Hall',
        'b': 'Bedroom',
        'c': 'Kitchen',
        'd': 'Bathroom',
        'e': 'Pooja Room'
    }
    user_room_type = room_map.get(room_choice, 'Living Hall')
    print(f"✅ Selected: {user_room_type}")
    
    print("\n2. Style:")
    print("   a) Modern")
    print("   b) Indian")
    print("   c) Minimalist")
    
    style_choice = input("\nSelect (a-c) or press Enter for Modern: ").strip().lower()
    style_map = {
        'a': 'Modern',
        'b': 'Indian',
        'c': 'Minimalist'
    }
    user_style = style_map.get(style_choice, 'Modern')
    print(f"✅ Selected: {user_style}")
    
    print("\n3. Color Palette:")
    print("   a) Pink")
    print("   b) Light Blue")
    print("   c) Lavender")
    
    palette_choice = input("\nSelect (a-c) or press Enter to skip: ").strip().lower()
    palette_map = {
        'a': 'pink',
        'b': 'light blue',
        'c': 'lavender'
    }
    user_palette = palette_map.get(palette_choice, '')
    if user_palette:
        print(f"✅ Selected: {user_palette}")
    
    edit_strength = 0.75
    
    print("\n" + "="*70)
    print("PROCESSING YOUR DESIGN (LOCAL STABLE DIFFUSION)...")
    print("="*70)
    
    try:
        results = ai.analyze_room(
            image_path=image_path,
            budget_level='mid-range',
            estimate_dimensions=True,
            generate_design=False,
            edit_image=True,
            edit_strength=edit_strength,
            create_comparison=True,
            user_room_type=user_room_type,
            user_style=user_style,
            user_palette=user_palette,
            user_furniture_prefs=None
        )
        
        if results:
            report_path = ai.generate_complete_report(results)
            
            print("\n" + "="*70)
            print("✅ DESIGN COMPLETE - FILES GENERATED")
            print("="*70)
            print(f"\n📝 Report: {report_path}")
            
            if results.get('edited_image'):
                print(f"\n✨ YOUR PHOTOREALISTIC DESIGN:")
                print(f"   🎨 {results['edited_image']}")
                print(f"   Generated with Local Stable Diffusion (FREE)")
                
                if results.get('comparison_image'):
                    print(f"\n🔀 Before/After: {results['comparison_image']}")
            
            if results['cost_breakdown']:
                print(f"\n💰 Total Cost: ₹{results['cost_breakdown']['total']:,.2f}")
            
            print("\n✅ All files saved!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        