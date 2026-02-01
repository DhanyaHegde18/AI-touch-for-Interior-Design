from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename
import os, time, shutil, traceback, random

# Try to import AI renderer
try:
    from image_to_image_renderer import ImageToImageRenderer
    print("✅ ImageToImageRenderer imported successfully")
    AI_RENDERER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ ImageToImageRenderer import failed: {e}")
    ImageToImageRenderer = None
    AI_RENDERER_AVAILABLE = False

# Import furniture configuration
FURNITURE_DATABASE = {
    'bedroom': {
        'bed': [
            {'type': 'Single (90x200cm)', 'wood': 'Plywood', 'thickness': 18, 'grade': 'BWR', 'rs_sqft': 100, 'area_sqft': 36, 'total': 3600, 'lifetime': '5-8', 'budget': 'Budget', 'multiplyable': True},
            {'type': 'Double (120x200cm)', 'wood': 'MDF', 'thickness': 12, 'grade': 'MR', 'rs_sqft': 70, 'area_sqft': 48, 'total': 3360, 'lifetime': '4-7', 'budget': 'Budget', 'multiplyable': True},
            {'type': 'Queen (160x200cm)', 'wood': 'Engineered', 'thickness': 18, 'grade': 'BWP', 'rs_sqft': 450, 'area_sqft': 64, 'total': 28800, 'lifetime': '8-12', 'budget': 'Middle', 'multiplyable': True},
            {'type': 'King (180x200cm)', 'wood': 'Pine', 'thickness': 25, 'grade': 'Solid A', 'rs_sqft': 600, 'area_sqft': 72, 'total': 43200, 'lifetime': '12-20', 'budget': 'Middle', 'multiplyable': True},
            {'type': 'King (180x200cm)', 'wood': 'Sheesham', 'thickness': 25, 'grade': 'Solid A', 'rs_sqft': 1000, 'area_sqft': 72, 'total': 72000, 'lifetime': '15-25', 'budget': 'Premium', 'multiplyable': True},
            {'type': 'Extra Large (200x200cm)', 'wood': 'Teak', 'thickness': 25, 'grade': 'Solid AA', 'rs_sqft': 2000, 'area_sqft': 80, 'total': 160000, 'lifetime': '50+', 'budget': 'Premium', 'multiplyable': True}
        ],
        'wardrobe': [
            {'type': '3-door (6x7ft)', 'wood': 'Plywood', 'thickness': 12, 'grade': 'BWR', 'rs_sqft': 90, 'area_sqft': 120, 'total': 10800, 'lifetime': '5-8', 'budget': 'Budget', 'multiplyable': False},
            {'type': '4-door (7x7ft)', 'wood': 'MDF', 'thickness': 18, 'grade': 'MR', 'rs_sqft': 100, 'area_sqft': 140, 'total': 14000, 'lifetime': '6-10', 'budget': 'Budget', 'multiplyable': False},
            {'type': '4-door w/drawers (8x7ft)', 'wood': 'Pine', 'thickness': 25, 'grade': 'Solid A', 'rs_sqft': 650, 'area_sqft': 160, 'total': 104000, 'lifetime': '15-20', 'budget': 'Middle', 'multiplyable': False},
            {'type': 'Designer (8x8ft)', 'wood': 'Teak', 'thickness': 25, 'grade': 'Solid AA', 'rs_sqft': 2200, 'area_sqft': 180, 'total': 396000, 'lifetime': '50+', 'budget': 'Premium', 'multiplyable': False}
        ],
        'nightstand': [
            {'type': '2ft Basic', 'wood': 'Plywood', 'thickness': 18, 'grade': 'BWP', 'rs_sqft': 160, 'area_sqft': 20, 'total': 3200, 'lifetime': '8-12', 'budget': 'Budget', 'multiplyable': True},
            {'type': '3ft Standard', 'wood': 'Engineered', 'thickness': 18, 'grade': 'BWP', 'rs_sqft': 500, 'area_sqft': 30, 'total': 15000, 'lifetime': '10-15', 'budget': 'Middle', 'multiplyable': True},
            {'type': '4ft Drawers', 'wood': 'Pine', 'thickness': 25, 'grade': 'Solid A', 'rs_sqft': 700, 'area_sqft': 40, 'total': 28000, 'lifetime': '12-20', 'budget': 'Middle', 'multiplyable': True},
            {'type': '5ft Premium', 'wood': 'Teak', 'thickness': 25, 'grade': 'Solid AA', 'rs_sqft': 2500, 'area_sqft': 50, 'total': 125000, 'lifetime': '50+', 'budget': 'Premium', 'multiplyable': True}
        ]
    },
    'bathroom': {
        'vanity': [
            {'type': '4ft Single Sink', 'wood': 'Plywood', 'thickness': 18, 'grade': 'Marine BWP', 'rs_sqft': 200, 'area_sqft': 36, 'total': 7200, 'lifetime': '8-12', 'budget': 'Budget', 'multiplyable': False},
            {'type': '5ft Double Sink', 'wood': 'Pine', 'thickness': 25, 'grade': 'Marine Solid', 'rs_sqft': 800, 'area_sqft': 50, 'total': 40000, 'lifetime': '12-20', 'budget': 'Middle', 'multiplyable': False},
            {'type': '6ft Luxury', 'wood': 'Teak', 'thickness': 25, 'grade': 'Sealed AA', 'rs_sqft': 2500, 'area_sqft': 72, 'total': 180000, 'lifetime': '50+', 'budget': 'Premium', 'multiplyable': False}
        ],
        'mirror_cabinet': [
            {'type': 'Wall 3ft', 'wood': 'MDF', 'thickness': 12, 'grade': 'Waterproof', 'rs_sqft': 70, 'area_sqft': 18, 'total': 1260, 'lifetime': '3-6', 'budget': 'Budget', 'multiplyable': True},
            {'type': 'Floor 4ft', 'wood': 'Plywood', 'thickness': 18, 'grade': 'BWP', 'rs_sqft': 180, 'area_sqft': 32, 'total': 5760, 'lifetime': '7-12', 'budget': 'Budget', 'multiplyable': True},
            {'type': 'Tall 6ft', 'wood': 'Sheesham', 'thickness': 25, 'grade': 'Sealed', 'rs_sqft': 1200, 'area_sqft': 60, 'total': 72000, 'lifetime': '15-25', 'budget': 'Premium', 'multiplyable': True}
        ]
    },
    'kitchen': {
        'counter': [
            {'type': '6ft Basic', 'wood': 'Plywood', 'thickness': 18, 'grade': 'BWP', 'rs_sqft': 150, 'area_sqft': 36, 'total': 5400, 'lifetime': '8-12', 'budget': 'Budget', 'multiplyable': False},
            {'type': '8ft Standard', 'wood': 'MDF', 'thickness': 18, 'grade': 'MR', 'rs_sqft': 90, 'area_sqft': 48, 'total': 4320, 'lifetime': '6-10', 'budget': 'Budget', 'multiplyable': False},
            {'type': '10ft L-Shape', 'wood': 'Pine', 'thickness': 25, 'grade': 'Solid A', 'rs_sqft': 650, 'area_sqft': 80, 'total': 52000, 'lifetime': '15-20', 'budget': 'Middle', 'multiplyable': False},
            {'type': '12ft Island', 'wood': 'Teak', 'thickness': 25, 'grade': 'Solid AA', 'rs_sqft': 2200, 'area_sqft': 120, 'total': 264000, 'lifetime': '50+', 'budget': 'Premium', 'multiplyable': False}
        ],
        'wall_cabinet': [
            {'type': '4ft Single', 'wood': 'MDF', 'thickness': 12, 'grade': 'MR', 'rs_sqft': 70, 'area_sqft': 24, 'total': 1680, 'lifetime': '4-8', 'budget': 'Budget', 'multiplyable': True},
            {'type': '6ft Double', 'wood': 'Plywood', 'thickness': 18, 'grade': 'BWR', 'rs_sqft': 100, 'area_sqft': 36, 'total': 3600, 'lifetime': '5-10', 'budget': 'Budget', 'multiplyable': True},
            {'type': '8ft Tall', 'wood': 'Sheesham', 'thickness': 25, 'grade': 'Solid A', 'rs_sqft': 1000, 'area_sqft': 60, 'total': 60000, 'lifetime': '15-25', 'budget': 'Premium', 'multiplyable': True}
        ]
    },
    'living_hall': {
        'sofa': [
            {'type': '2-Seater (5ft)', 'wood': 'Plywood', 'thickness': 18, 'grade': 'BWR', 'rs_sqft': 110, 'area_sqft': 50, 'total': 5500, 'lifetime': '5-10', 'budget': 'Budget', 'multiplyable': True},
            {'type': '3-Seater (7ft)', 'wood': 'MDF', 'thickness': 18, 'grade': 'MR', 'rs_sqft': 90, 'area_sqft': 70, 'total': 6300, 'lifetime': '6-12', 'budget': 'Budget', 'multiplyable': True},
            {'type': 'L-Shape (10ft)', 'wood': 'Pine', 'thickness': 25, 'grade': 'Solid A', 'rs_sqft': 650, 'area_sqft': 120, 'total': 78000, 'lifetime': '15-25', 'budget': 'Middle', 'multiplyable': True},
            {'type': 'Sectional (12ft)', 'wood': 'Teak', 'thickness': 25, 'grade': 'Solid AA', 'rs_sqft': 2200, 'area_sqft': 160, 'total': 352000, 'lifetime': '50+', 'budget': 'Premium', 'multiplyable': True}
        ],
        'tv_unit': [
            {'type': '4ft Basic', 'wood': 'MDF', 'thickness': 12, 'grade': 'MR', 'rs_sqft': 60, 'area_sqft': 24, 'total': 1440, 'lifetime': '4-8', 'budget': 'Budget', 'multiplyable': False},
            {'type': '5ft Standard', 'wood': 'Plywood', 'thickness': 18, 'grade': 'BWR', 'rs_sqft': 100, 'area_sqft': 36, 'total': 3600, 'lifetime': '6-12', 'budget': 'Budget', 'multiplyable': False},
            {'type': '6ft w/Shelves', 'wood': 'Sheesham', 'thickness': 25, 'grade': 'Solid A', 'rs_sqft': 1000, 'area_sqft': 54, 'total': 54000, 'lifetime': '15-25', 'budget': 'Premium', 'multiplyable': False}
        ],
        'coffee_table': [
            {'type': '3x2ft Basic', 'wood': 'Plywood', 'thickness': 18, 'grade': 'BWR', 'rs_sqft': 90, 'area_sqft': 18, 'total': 1620, 'lifetime': '5-8', 'budget': 'Budget', 'multiplyable': True},
            {'type': '4x2ft Glass Top', 'wood': 'Engineered', 'thickness': 18, 'grade': 'BWP', 'rs_sqft': 500, 'area_sqft': 24, 'total': 12000, 'lifetime': '10-15', 'budget': 'Middle', 'multiplyable': True}
        ]
    }
}


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'interioai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'interioai-secret-key-change-in-production'

db = SQLAlchemy(app)

UPLOAD_DIR = os.path.join(basedir, 'uploads')
OUTPUT_DIR = os.path.join(basedir, 'output')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    designs = db.relationship('Design', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'designs_count': len(self.designs) if self.designs else 0
        }


class Design(db.Model):
    __tablename__ = 'design'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    style = db.Column(db.String(50), nullable=False)
    palette = db.Column(db.String(100), nullable=False)
    width = db.Column(db.String(20), nullable=False)
    length = db.Column(db.String(20), nullable=False)
    estimated_cost = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_type': self.room_type,
            'style': self.style,
            'palette': self.palette,
            'width': self.width,
            'length': self.length,
            'estimated_cost': self.estimated_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'email', 'password']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        new_user = User(name=data['name'], email=data['email'], password=generate_password_hash(data['password']))
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User registered successfully', 'user': new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        return jsonify({'success': True, 'message': 'Login successful', 'user': user.to_dict(), 'user_id': user.id}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# NEW FURNITURE ENDPOINTS
@app.route('/api/furniture/<room_type>', methods=['GET'])
def get_furniture(room_type):
    """Get furniture options for a specific room type"""
    try:
        room_key = room_type.lower().replace(' ', '_')
        furniture = FURNITURE_DATABASE.get(room_key, FURNITURE_DATABASE['bedroom'])
        return jsonify({'success': True, 'furniture': furniture}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/furniture/calculate-cost', methods=['POST'])
def calculate_furniture_cost():
    """Calculate total cost from selected furniture items"""
    try:
        data = request.get_json() or {}
        selections = data.get('selections', [])
        
        total = 0
        items_breakdown = []
        budget_breakdown = {'Budget': 0, 'Middle': 0, 'Premium': 0}
        
        for selection in selections:
            category = selection.get('category')
            item_index = selection.get('itemIndex', 0)
            quantity = int(selection.get('quantity', 1))
            room_type = selection.get('room_type', 'bedroom')
            
            room_key = room_type.lower().replace(' ', '_')
            furniture = FURNITURE_DATABASE.get(room_key, FURNITURE_DATABASE['bedroom'])
            
            if category in furniture and 0 <= item_index < len(furniture[category]):
                item = furniture[category][item_index]
                item_total = int(item.get('total', 0)) * max(1, quantity)
                total += item_total
                budget = item.get('budget', 'Budget')
                if budget not in budget_breakdown:
                    budget_breakdown[budget] = 0
                budget_breakdown[budget] += item_total
                
                items_breakdown.append({
                    'category': category,
                    'type': item.get('type'),
                    'wood': item.get('wood'),
                    'quantity': quantity,
                    'unit_price': item.get('total'),
                    'total': item_total,
                    'budget': budget,
                    'lifetime': item.get('lifetime')
                })
        
        return jsonify({
            'success': True,
            'total_cost': total,
            'items_breakdown': items_breakdown,
            'budget_breakdown': budget_breakdown,
            'items_count': len(items_breakdown)
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        return jsonify({'success': True, 'user': user.to_dict()}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/designs', methods=['POST'])
def save_design():
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        user = None
        if user_id is not None:
            try:
                user_id = int(user_id)
                user = User.query.get(user_id)
            except:
                user = None

        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        required_fields = ['room_type', 'style', 'palette', 'width', 'length']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        new_design = Design(user_id=user_id, room_type=data['room_type'], style=data['style'],
                           palette=data['palette'], width=data['width'], length=data['length'],
                           estimated_cost=data.get('estimated_cost'))
        db.session.add(new_design)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Design saved successfully', 'design': new_design.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/designs/<int:user_id>', methods=['GET'])
def get_user_designs(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        designs = Design.query.filter_by(user_id=user_id).order_by(Design.created_at.desc()).all()
        return jsonify({'success': True, 'designs': [d.to_dict() for d in designs], 'total': len(designs)}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'success': True, 'message': 'Backend is running', 'ai_available': AI_RENDERER_AVAILABLE,
                   'timestamp': datetime.utcnow().isoformat()}), 200

@app.route('/', methods=['GET'])
def home():
    return send_file(os.path.join(basedir, 'front.html'))


@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route('/api/generate', methods=['POST'])
@app.route('/generate', methods=['POST'])
def generate():
    try:
        print("\n" + "="*80)
        print("🎨 GENERATION REQUEST RECEIVED")
        print("="*80)
        
        room_type = request.form.get('roomType') or 'Living Hall'
        style = request.form.get('style') or 'Modern'
        palette = request.form.get('palette') or request.form.get('customColor') or 'neutral'
        width = request.form.get('width', '10')
        length = request.form.get('length', '12')
        user_id = request.form.get('user_id')

        print(f"\n📊 Parameters: {room_type}, {style}, {palette}, {width}ft × {length}ft")

        user_obj = None
        if user_id:
            try:
                user_id = int(user_id)
                user_obj = User.query.get(user_id)
            except Exception:
                print("   ⚠️ user_id parse failed or user not found")
                user_id = None
                user_obj = None

        photo = request.files.get('photo')
        if not photo:
            return jsonify({'success': False, 'error': 'No input image provided'}), 400

        # ensure safe, non-empty filename
        orig_name = getattr(photo, 'filename', '') or ''
        safe_name = secure_filename(orig_name)
        if not safe_name:
            safe_name = f"upload_{int(time.time())}.png"

        timestamp = int(time.time())
        original_filename = f"{timestamp}_{safe_name}"
        before_filename = f"before_{original_filename}"
        before_path = os.path.join(UPLOAD_DIR, before_filename)

        photo.save(before_path)

        after_filename = f"after_{original_filename}"
        after_path = os.path.join(OUTPUT_DIR, after_filename)

        furniture_by_room = {
            'bedroom': ['bed', 'nightstand', 'dresser', 'wardrobe', 'bedside lamp', 'rug'],
            'kitchen': ['dining table', 'chairs', 'bar stools', 'pendant lights', 'kitchen island', 'cabinets'],
            'living hall': ['sofa', 'coffee table', 'TV stand', 'armchair', 'floor lamp', 'rug', 'side table'],
            'living room': ['sofa', 'coffee table', 'TV stand', 'armchair', 'floor lamp', 'rug', 'side table'],
            'bathroom': ['vanity', 'mirror', 'storage cabinet', 'towel rack', 'bath mat', 'shelf']
        }
        
        suggested_items = furniture_by_room.get(room_type.lower(), ['sofa', 'coffee table', 'chair', 'lamp', 'rug'])

        room_descriptions = {
            'bedroom': f"A {style} bedroom with {palette} tones, cozy bed, nightstands, and warm lighting",
            'kitchen': f"A {style} kitchen with {palette} colors, dining table, chairs, and modern appliances",
            'living hall': f"A {style} living room with {palette} tones, comfortable sofa, coffee table, and modern furniture",
            'living room': f"A {style} living room with {palette} tones, comfortable sofa, coffee table, and modern furniture",
            'bathroom': f"A {style} bathroom with {palette} colors, elegant vanity, mirror, and modern fixtures"
        }
        
        description = room_descriptions.get(room_type.lower(), f"A {style} interior with {palette} tones and modern furniture")

        room_data = {
            'room_type': room_type.lower().replace(' ', '_'),
            'style': style,
            'palette': palette,
            'description': description,
            'suggested_items': suggested_items,
            'is_empty': True
        }

        print(f"\n🤖 AI Available: {AI_RENDERER_AVAILABLE}")
        
        if AI_RENDERER_AVAILABLE and ImageToImageRenderer is not None:
            try:
                print("   🎨 Initializing AI renderer...")
                renderer = ImageToImageRenderer()
                
                print("   🚀 Generating furnished design...")
                # defensive call: renderer may return a path or write file directly
                result = renderer.edit_room_image(
                    original_image_path=before_path,
                    room_data=room_data,
                    output_path=after_path,
                    strength=0.75
                )
                
                # if renderer wrote to a different path, try to handle it
                if os.path.exists(after_path):
                    print(f"   ✅ AI generation successful to {after_path}")
                else:
                    # if result is a path and exists, copy it
                    if isinstance(result, str) and os.path.exists(result):
                        shutil.copy(result, after_path)
                        print("   ✅ AI generation successful (from result path)")
                    else:
                        # fallback: copy original
                        print("   ⚠️ AI returned nothing usable; copying original image as fallback")
                        shutil.copy(before_path, after_path)
                    
            except Exception as e:
                print(f"   ❌ AI error: {e}")
                traceback.print_exc()
                try:
                    shutil.copy(before_path, after_path)
                except Exception as e2:
                    print("   ❌ Failed to copy fallback image:", e2)
        else:
            print("   ⚠️ AI not available, copying original")
            shutil.copy(before_path, after_path)

        print(f"\n{'='*80}")
        print("✅ GENERATION COMPLETE")
        print(f"{'='*80}\n")

        return jsonify({
            'success': True,
            'user_id': user_id,
            'before_url': f"/uploads/{before_filename}",
            'after_url': f"/output/{after_filename}",
            'room_type': room_type
        }), 200

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        "api_base": request.host_url.rstrip('/')
    })

if __name__ == '__main__':
    init_db()
    
    print("\n" + "="*80)
    print("🏠 INTERIOAI BACKEND SERVER")
    print("="*80)
    print(f"✅ Database: interioai.db")
    print(f"✅ AI Renderer: {'Available ✓' if AI_RENDERER_AVAILABLE else 'Not Available ✗'}")
    if AI_RENDERER_AVAILABLE:
        print("   🎨 Stable Diffusion + ControlNet ready")
    else:
        print("   ⚠️ AI models not loaded - will copy images only")
    print("\n🌐 Server: http://localhost:5000")
    print("="*80 + "\n")
    
    print("\n🌐 Server starting on a free port (auto)...")
    app.run(debug=True, host="127.0.0.1", port=0)
