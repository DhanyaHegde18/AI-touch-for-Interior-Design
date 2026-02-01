"""
Flask Backend API for InterioAI - LOCAL STABLE DIFFUSION VERSION
100% FREE - Runs on your computer
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import base64
from datetime import datetime
from interioai_complete import InterioAI
import json

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ai_system = None

def init_ai_system():
    """Initialize AI system once"""
    global ai_system
    if ai_system is None:
        ai_system = InterioAI(
            model_path='runs/detect/train/weights/best.pt',
            enable_dimensions=True,
            dimension_model='MiDaS_small'
        )

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'ai_enabled': True,
        'api_provider': 'Local Stable Diffusion (FREE)',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_room():
    """Main endpoint to analyze room image with USER PREFERENCES"""
    
    try:
        # Initialize AI system
        init_ai_system()
        
        # Validate file upload
        if 'roomPhoto' not in request.files:
            return jsonify({'error': 'No image file uploaded'}), 400
        
        file = request.files['roomPhoto']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use PNG, JPG, or JPEG'}), 400
        
        # GET USER PREFERENCES FROM FRONTEND
        room_type = request.form.get('roomType', 'Living Hall').strip()
        style = request.form.get('style', 'Modern').strip()
        width_range = request.form.get('width', '5-8')
        length_range = request.form.get('length', '5-8')
        palette = request.form.get('palette', '').strip()
        furniture_pref = request.form.get('furniture', '').strip()
        
        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{timestamp}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"\n🎨 Processing design request...")
        print(f"   Room Type: {room_type}")
        print(f"   Style: {style}")
        print(f"   Color Palette: {palette}")
        print(f"   Dimensions: {width_range} x {length_range}")
        print(f"   API: Local Stable Diffusion (FREE)")
        
        # Determine edit strength based on room type
        edit_strength_map = {
            'bedroom': 0.75,
            'kitchen': 0.70,
            'living hall': 0.80,
            'living room': 0.80,
            'bathroom': 0.65,
            'pooja room': 0.75,
            'dining room': 0.75,
            'office': 0.75,
            'study room': 0.75
        }
        edit_strength = edit_strength_map.get(room_type.lower(), 0.75)
        
        # RUN ANALYSIS WITH USER PREFERENCES
        results = ai_system.analyze_room(
            image_path=filepath,
            budget_level='mid-range',
            estimate_dimensions=True,
            generate_design=False,
            edit_image=True,
            edit_strength=edit_strength,
            create_comparison=True,
            user_room_type=room_type,
            user_style=style,
            user_palette=palette,
            user_furniture_prefs=furniture_pref
        )
        
        # Prepare response
        response_data = {
            'success': True,
            'timestamp': timestamp,
            'roomType': room_type,
            'style': style,
            'palette': palette,
            'api_provider': 'Local Stable Diffusion',
            'detectedItems': results.get('detected_objects', []),
            'suggestedItems': results['analysis']['suggestions']['add_items'][:6],
            'estimatedCost': results['cost_breakdown']['total'] if results['cost_breakdown'] else 0,
            'files': {}
        }
        
        # Add dimension info
        if results.get('dimensions'):
            response_data['dimensions'] = {
                'length': round(results['dimensions']['length_m'], 1),
                'width': round(results['dimensions']['width_m'], 1),
                'height': round(results['dimensions']['height_m'], 1),
                'area_sqm': round(results['dimensions']['floor_area_sqm'], 1),
                'area_sqft': round(results['dimensions']['floor_area_sqft'], 0)
            }
        
        # Convert images to base64
        if results.get('edited_image') and os.path.exists(results['edited_image']):
            with open(results['edited_image'], 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                response_data['files']['edited_image'] = f"data:image/png;base64,{img_data}"
        
        if results.get('comparison_image') and os.path.exists(results['comparison_image']):
            with open(results['comparison_image'], 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                response_data['files']['comparison_image'] = f"data:image/png;base64,{img_data}"
        
        response_data['files']['original_path'] = filepath
        response_data['files']['edited_path'] = results.get('edited_image', '')
        
        print(f"✅ Analysis complete!")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated file"""
    try:
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏠 INTERIOAI FLASK API SERVER - LOCAL STABLE DIFFUSION")
    print("="*70)
    
    print("\n✅ Using LOCAL Stable Diffusion (100% FREE)")
    print("   No API costs - runs on your computer!")
    
    print("\n✨ FEATURES:")
    print("   ✅ 100% FREE - no costs ever")
    print("   ✅ User's room type & style preferences")
    print("   ✅ Color palette customization")
    print("   ✅ Cost in Indian Rupees")
    print("   ✅ Photorealistic designs")
    print("   ✅ GPU accelerated (detected)")
    
    print("\n🚀 Starting server on http://localhost:5000")
    print("📡 API Endpoints:")
    print("   GET  /api/health")
    print("   POST /api/analyze")
    print("   GET  /api/download/<filename>")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)