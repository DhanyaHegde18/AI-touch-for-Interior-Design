import torch
import cv2
import numpy as np
from PIL import Image
import urllib.request

class DimensionEstimator:
    """
    Estimates room dimensions from a single image using MiDaS depth estimation
    """
    
    def __init__(self, model_type='DPT_Large'):
        """
        Initialize the dimension estimator
        
        Args:
            model_type: 'DPT_Large', 'DPT_Hybrid', or 'MiDaS_small' (faster but less accurate)
        """
        print("🔧 Initializing Dimension Estimator...")
        
        # Load MiDaS model from PyTorch Hub
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"   Using device: {self.device}")
        
        try:
            self.model = torch.hub.load('intel-isl/MiDaS', model_type, trust_repo=True)
            self.model.to(self.device)
            self.model.eval()
            
            # Load transforms
            midas_transforms = torch.hub.load('intel-isl/MiDaS', 'transforms', trust_repo=True)
            
            if model_type == 'DPT_Large' or model_type == 'DPT_Hybrid':
                self.transform = midas_transforms.dpt_transform
            else:
                self.transform = midas_transforms.small_transform
            
            print(f"✅ Model loaded: {model_type}")
            
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            print("   Falling back to MiDaS_small...")
            self.model = torch.hub.load('intel-isl/MiDaS', 'MiDaS_small', trust_repo=True)
            self.model.to(self.device)
            self.model.eval()
            midas_transforms = torch.hub.load('intel-isl/MiDaS', 'transforms', trust_repo=True)
            self.transform = midas_transforms.small_transform
        
        # Average human height for scale reference (in meters)
        self.reference_height = 1.7
    
    def estimate_dimensions(self, image_path, known_object_height=None):
        """
        Estimate room dimensions from image
        
        Args:
            image_path: Path to room image
            known_object_height: Optional tuple (object_name, height_in_meters) for calibration
            
        Returns:
            dict: Estimated room dimensions
        """
        print(f"\n📐 Estimating dimensions for: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Could not load image: {image_path}")
            return None
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Get depth map
        depth_map = self._get_depth_map(img_rgb)
        
        # Estimate dimensions
        dimensions = self._calculate_dimensions(depth_map, img_rgb.shape, known_object_height)
        
        # Add visualization info
        dimensions['depth_map'] = depth_map
        dimensions['original_shape'] = img_rgb.shape
        
        return dimensions
    
    def _get_depth_map(self, image):
        """Generate depth map from image"""
        # Prepare image for model
        input_batch = self.transform(image).to(self.device)
        
        # Predict depth
        with torch.no_grad():
            prediction = self.model(input_batch)
            
            # Resize to original resolution
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=image.shape[:2],
                mode='bicubic',
                align_corners=False
            ).squeeze()
        
        depth_map = prediction.cpu().numpy()
        
        # Normalize depth map
        depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
        
        return depth_map
    
    def _calculate_dimensions(self, depth_map, image_shape, known_object_height=None):
        """
        Calculate room dimensions from depth map
        
        Args:
            depth_map: Normalized depth map
            image_shape: (height, width, channels)
            known_object_height: Optional calibration object
        """
        height, width = depth_map.shape
        
        # Find floor and ceiling (bottom and top 20% of image)
        floor_depth = np.median(depth_map[int(height * 0.8):, :])
        ceiling_depth = np.median(depth_map[:int(height * 0.2), :])
        
        # Find walls (left, right, and back)
        left_wall_depth = np.median(depth_map[:, :int(width * 0.1)])
        right_wall_depth = np.median(depth_map[:, int(width * 0.9):])
        back_wall_depth = np.max(depth_map[int(height * 0.3):int(height * 0.7), 
                                           int(width * 0.3):int(width * 0.7)])
        
        # Estimate scale factor (using average room height of 2.7m / 9ft)
        estimated_room_height = 2.7  # meters
        
        if known_object_height:
            # If we have a known object (e.g., detected person, door), use it for calibration
            estimated_room_height = known_object_height[1] / (1 - ceiling_depth)
        
        # Calculate dimensions
        # Depth values are inverse (closer = larger value)
        room_depth = self._depth_to_meters(back_wall_depth - floor_depth, estimated_room_height)
        room_width = self._depth_to_meters(abs(left_wall_depth - right_wall_depth), estimated_room_height)
        room_height = estimated_room_height
        
        # Calculate area and volume
        floor_area = room_depth * room_width
        volume = floor_area * room_height
        
        # Convert to feet for US users
        room_depth_ft = room_depth * 3.28084
        room_width_ft = room_width * 3.28084
        room_height_ft = room_height * 3.28084
        floor_area_sqft = floor_area * 10.7639
        
        dimensions = {
            'length_m': round(room_depth, 2),
            'width_m': round(room_width, 2),
            'height_m': round(room_height, 2),
            'length_ft': round(room_depth_ft, 2),
            'width_ft': round(room_width_ft, 2),
            'height_ft': round(room_height_ft, 2),
            'floor_area_sqm': round(floor_area, 2),
            'floor_area_sqft': round(floor_area_sqft, 2),
            'volume_cum': round(volume, 2),
            'confidence': self._estimate_confidence(depth_map),
            'depth_statistics': {
                'floor': float(floor_depth),
                'ceiling': float(ceiling_depth),
                'back_wall': float(back_wall_depth)
            }
        }
        
        return dimensions
    
    def _depth_to_meters(self, depth_diff, reference_height):
        """Convert relative depth to meters using reference height"""
        # Simple proportional conversion
        # This is an approximation - real-world accuracy depends on camera parameters
        estimated_meters = abs(depth_diff) * reference_height * 4.5
        
        # Clamp to reasonable room dimensions (2m - 15m)
        return max(2.0, min(15.0, estimated_meters))
    
    def _estimate_confidence(self, depth_map):
        """
        Estimate confidence in dimension calculation
        Based on depth map quality and variation
        """
        # Calculate standard deviation (lower = more uniform = better)
        std_dev = np.std(depth_map)
        
        # Calculate gradient variance (higher = more distinct features)
        grad_x = np.gradient(depth_map, axis=1)
        grad_y = np.gradient(depth_map, axis=0)
        gradient_mag = np.sqrt(grad_x**2 + grad_y**2)
        edge_strength = np.mean(gradient_mag)
        
        # Confidence score (0-100)
        confidence = min(100, int((edge_strength * 100) * (1 - std_dev)))
        
        if confidence > 70:
            return "High"
        elif confidence > 40:
            return "Medium"
        else:
            return "Low"
    
    def save_depth_visualization(self, dimensions, output_path='depth_visualization.png'):
        """
        Save depth map visualization
        
        Args:
            dimensions: Result from estimate_dimensions()
            output_path: Output file path
        """
        if 'depth_map' not in dimensions:
            print("❌ No depth map found in dimensions")
            return None
        
        depth_map = dimensions['depth_map']
        
        # Create colorized depth map
        depth_colored = cv2.applyColorMap(
            (depth_map * 255).astype(np.uint8), 
            cv2.COLORMAP_PLASMA
        )
        
        # Add text overlay with dimensions
        h, w = depth_colored.shape[:2]
        overlay = depth_colored.copy()
        
        # Add semi-transparent background for text
        cv2.rectangle(overlay, (10, 10), (w - 10, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, depth_colored, 0.3, 0, depth_colored)
        
        # Add dimension text
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_pos = 35
        cv2.putText(depth_colored, f"Length: {dimensions['length_m']}m ({dimensions['length_ft']}ft)", 
                    (20, y_pos), font, 0.6, (255, 255, 255), 2)
        y_pos += 30
        cv2.putText(depth_colored, f"Width: {dimensions['width_m']}m ({dimensions['width_ft']}ft)", 
                    (20, y_pos), font, 0.6, (255, 255, 255), 2)
        y_pos += 30
        cv2.putText(depth_colored, f"Height: {dimensions['height_m']}m ({dimensions['height_ft']}ft)", 
                    (20, y_pos), font, 0.6, (255, 255, 255), 2)
        y_pos += 30
        cv2.putText(depth_colored, f"Area: {dimensions['floor_area_sqm']}sqm ({dimensions['floor_area_sqft']}sqft)", 
                    (20, y_pos), font, 0.6, (255, 255, 255), 2)
        
        # Save
        cv2.imwrite(output_path, depth_colored)
        print(f"✅ Depth visualization saved: {output_path}")
        
        return output_path
    
    def generate_dimension_report(self, dimensions):
        """Generate text report for dimensions"""
        if not dimensions:
            return "❌ No dimension data available"
        
        report = []
        report.append("\n" + "=" * 60)
        report.append("ROOM DIMENSION ESTIMATION")
        report.append("=" * 60)
        
        report.append(f"\n📏 Dimensions (Metric):")
        report.append(f"   Length: {dimensions['length_m']} meters")
        report.append(f"   Width:  {dimensions['width_m']} meters")
        report.append(f"   Height: {dimensions['height_m']} meters")
        
        report.append(f"\n📏 Dimensions (Imperial):")
        report.append(f"   Length: {dimensions['length_ft']} feet")
        report.append(f"   Width:  {dimensions['width_ft']} feet")
        report.append(f"   Height: {dimensions['height_ft']} feet")
        
        report.append(f"\n📐 Area & Volume:")
        report.append(f"   Floor Area: {dimensions['floor_area_sqm']} m² ({dimensions['floor_area_sqft']} sq ft)")
        report.append(f"   Volume: {dimensions['volume_cum']} m³")
        
        report.append(f"\n🎯 Confidence: {dimensions['confidence']}")
        
        report.append("\n⚠️  Note: Dimensions are estimated using depth estimation AI.")
        report.append("   For accurate measurements, use physical measuring tools.")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    # Initialize estimator
    estimator = DimensionEstimator(model_type='DPT_Large')
    
    # Estimate dimensions
    image_path = 'images/img2.jpg'
    
    if os.path.exists(image_path):
        dimensions = estimator.estimate_dimensions(image_path)
        
        if dimensions:
            # Print report
            print(estimator.generate_dimension_report(dimensions))
            
            # Save visualization
            estimator.save_depth_visualization(dimensions, 'room_depth_map.png')
    else:
        print(f"❌ Image not found: {image_path}")