"""
Updated Suggestion Engine with User Preference Support
Accepts force_room_type parameter to respect user's choice
"""

class InteriorSuggestionEngine:
    """Generate furniture suggestions based on detected items and user preferences"""
    
    def __init__(self):
        # Room-specific furniture requirements
        self.room_furniture = {
            'living_room': {
                'essential': ['sofa', 'coffee table', 'tv stand'],
                'common': ['armchair', 'side table', 'floor lamp', 'rug', 'bookshelf'],
                'luxury': ['ottoman', 'console table', 'accent chair']
            },
            'bedroom': {
                'essential': ['bed', 'nightstand', 'wardrobe'],
                'common': ['dresser', 'bedside lamp', 'rug', 'mirror'],
                'luxury': ['vanity', 'reading chair', 'bench']
            },
            'kitchen': {
                'essential': ['dining table', 'chairs'],
                'common': ['bar stools', 'pendant lights', 'kitchen island'],
                'luxury': ['wine rack', 'bar cart']
            },
            'dining_room': {
                'essential': ['dining table', 'dining chairs'],
                'common': ['sideboard', 'pendant light', 'centerpiece', 'rug'],
                'luxury': ['china cabinet', 'bar cart', 'wall art']
            },
            'bathroom': {
                'essential': ['vanity', 'mirror'],
                'common': ['storage cabinet', 'towel rack', 'bath mat'],
                'luxury': ['decorative shelf', 'plant stand']
            },
            'office': {
                'essential': ['desk', 'office chair'],
                'common': ['bookshelf', 'desk lamp', 'filing cabinet', 'rug'],
                'luxury': ['credenza', 'reading chair', 'wall shelves']
            }
        }
        
        # Style characteristics
        self.styles = {
            'modern': {
                'keywords': ['modern', 'contemporary', 'minimalist'],
                'colors': ['gray', 'white', 'black', 'navy'],
                'materials': ['glass', 'metal', 'leather']
            },
            'indian': {
                'keywords': ['traditional', 'ethnic', 'carved', 'ornate'],
                'colors': ['red', 'gold', 'maroon', 'orange'],
                'materials': ['wood', 'brass', 'silk']
            },
            'minimalist': {
                'keywords': ['simple', 'clean', 'minimal', 'functional'],
                'colors': ['white', 'beige', 'gray'],
                'materials': ['wood', 'concrete', 'linen']
            },
            'scandinavian': {
                'keywords': ['light', 'cozy', 'natural', 'simple'],
                'colors': ['white', 'light gray', 'beige', 'pastel'],
                'materials': ['light wood', 'wool', 'cotton']
            },
            'italian': {
                'keywords': ['elegant', 'sophisticated', 'luxurious'],
                'colors': ['cream', 'gold', 'burgundy'],
                'materials': ['marble', 'velvet', 'leather']
            }
        }
    
    def analyze_room(self, detected_objects, force_room_type=None):
        """
        Analyze room and generate suggestions
        
        Args:
            detected_objects: List of detected furniture items
            force_room_type: Override room type detection (e.g., 'bedroom', 'kitchen')
        
        Returns:
            dict: Analysis results with suggestions
        """
        
        # ✅ USE FORCED ROOM TYPE if provided
        if force_room_type:
            room_type = force_room_type
            print(f"   Using specified room type: {room_type}")
        else:
            room_type = self._identify_room_type(detected_objects)
        
        current_style = self._identify_style(detected_objects)
        missing_essentials = self._find_missing_essentials(detected_objects, room_type)
        suggested_additions = self._suggest_additions(detected_objects, room_type)
        layout_suggestions = self._suggest_layout_improvements(detected_objects, room_type)
        
        return {
            'room_type': room_type,
            'current_style': current_style,
            'detected_count': len(detected_objects),
            'suggestions': {
                'missing_essentials': missing_essentials,
                'add_items': suggested_additions,
                'layout_tips': layout_suggestions
            }
        }
    
    def _identify_room_type(self, detected_objects):
        """Identify room type from detected furniture"""
        
        # Room type indicators
        room_indicators = {
            'bedroom': ['bed', 'nightstand', 'dresser', 'wardrobe'],
            'living_room': ['sofa', 'tv stand', 'coffee table', 'armchair'],
            'kitchen': ['stove', 'refrigerator', 'sink', 'kitchen island'],
            'dining_room': ['dining table', 'dining chair', 'sideboard'],
            'bathroom': ['toilet', 'sink', 'bathtub', 'shower'],
            'office': ['desk', 'office chair', 'filing cabinet', 'bookshelf']
        }
        
        # Count matches for each room type
        scores = {}
        for room_type, indicators in room_indicators.items():
            score = sum(1 for item in detected_objects if any(ind in item.lower() for ind in indicators))
            if score > 0:
                scores[room_type] = score
        
        # Return room with highest score, default to living room
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return 'living_room'
    
    def _identify_style(self, detected_objects):
        """Identify interior style from detected items"""
        
        # Style detection based on keywords
        style_scores = {}
        
        for style, characteristics in self.styles.items():
            score = 0
            for obj in detected_objects:
                obj_lower = obj.lower()
                # Check if any style keywords appear in object names
                if any(keyword in obj_lower for keyword in characteristics['keywords']):
                    score += 1
            
            if score > 0:
                style_scores[style] = score
        
        if style_scores:
            return max(style_scores.items(), key=lambda x: x[1])[0]
        
        return 'modern'  # Default style
    
    def _find_missing_essentials(self, detected_objects, room_type):
        """Find essential furniture that's missing"""
        
        if room_type not in self.room_furniture:
            return []
        
        essentials = self.room_furniture[room_type]['essential']
        detected_lower = [obj.lower() for obj in detected_objects]
        
        missing = []
        for essential in essentials:
            # Check if essential item or similar item exists
            if not any(essential in det or det in essential for det in detected_lower):
                missing.append(essential)
        
        return missing
    
    def _suggest_additions(self, detected_objects, room_type):
        """Suggest additional furniture to enhance the room"""
        
        if room_type not in self.room_furniture:
            room_type = 'living_room'
        
        # Get all furniture for this room type
        all_furniture = (
            self.room_furniture[room_type]['essential'] +
            self.room_furniture[room_type]['common'] +
            self.room_furniture[room_type]['luxury']
        )
        
        detected_lower = [obj.lower() for obj in detected_objects]
        
        # Find items not yet in room
        suggestions = []
        for furniture in all_furniture:
            if not any(furniture in det or det in furniture for det in detected_lower):
                suggestions.append(furniture)
        
        # Prioritize essentials and common items
        essentials = [s for s in suggestions if s in self.room_furniture[room_type]['essential']]
        common = [s for s in suggestions if s in self.room_furniture[room_type]['common']]
        luxury = [s for s in suggestions if s in self.room_furniture[room_type]['luxury']]
        
        # Return prioritized list (essentials first, then common, then luxury)
        return essentials + common[:3] + luxury[:2]
    
    def _suggest_layout_improvements(self, detected_objects, room_type):
        """Suggest layout improvements"""
        
        tips = []
        
        # General tips based on room type
        room_tips = {
            'living_room': [
                'Arrange seating to encourage conversation',
                'Place TV at comfortable viewing distance',
                'Use area rug to define seating area'
            ],
            'bedroom': [
                'Position bed as focal point',
                'Ensure adequate lighting with bedside lamps',
                'Create symmetry with matching nightstands'
            ],
            'kitchen': [
                'Maintain work triangle between stove, sink, and fridge',
                'Ensure adequate counter space for prep work',
                'Add task lighting above work areas'
            ],
            'dining_room': [
                'Center dining table in room',
                'Allow 36 inches clearance around table',
                'Hang pendant light 30-36 inches above table'
            ],
            'office': [
                'Position desk near natural light',
                'Ensure ergonomic chair placement',
                'Organize with adequate storage'
            ],
            'bathroom': [
                'Maximize storage with cabinets and shelves',
                'Ensure proper ventilation',
                'Use water-resistant materials'
            ]
        }
        
        tips = room_tips.get(room_type, [
            'Ensure good traffic flow',
            'Balance furniture placement',
            'Use appropriate lighting'
        ])
        
        return tips[:3]
    
    def generate_report(self, analysis):
        """Generate text report from analysis"""
        
        report_lines = []
        
        report_lines.append(f"Room Type: {analysis['room_type'].replace('_', ' ').title()}")
        report_lines.append(f"Current Style: {analysis['current_style'].title()}")
        report_lines.append(f"Detected Items: {analysis['detected_count']}")
        
        if analysis['suggestions']['missing_essentials']:
            report_lines.append(f"\nMissing Essentials:")
            for item in analysis['suggestions']['missing_essentials']:
                report_lines.append(f"  - {item.title()}")
        
        if analysis['suggestions']['add_items']:
            report_lines.append(f"\nSuggested Additions:")
            for item in analysis['suggestions']['add_items'][:6]:
                report_lines.append(f"  - {item.title()}")
        
        if analysis['suggestions']['layout_tips']:
            report_lines.append(f"\nLayout Tips:")
            for tip in analysis['suggestions']['layout_tips']:
                report_lines.append(f"  - {tip}")
        
        return "\n".join(report_lines)


# Test
if __name__ == "__main__":
    engine = InteriorSuggestionEngine()
    
    # Test with empty bedroom
    print("="*60)
    print("TEST 1: Empty Bedroom (User Specified)")
    print("="*60)
    result = engine.analyze_room([], force_room_type='bedroom')
    print(engine.generate_report(result))
    
    # Test with living room
    print("\n" + "="*60)
    print("TEST 2: Living Room with Some Furniture")
    print("="*60)
    detected = ['sofa', 'tv stand']
    result = engine.analyze_room(detected, force_room_type='living_room')
    print(engine.generate_report(result))
    
    # Test with kitchen
    print("\n" + "="*60)
    print("TEST 3: Kitchen (User Specified)")
    print("="*60)
    result = engine.analyze_room([], force_room_type='kitchen')
    print(engine.generate_report(result))