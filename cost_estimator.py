"""
Cost Estimator - Indian Rupees Version
All prices in INR (₹)
"""

class CostEstimator:
    """Estimate furniture costs in Indian Rupees"""
    
    def __init__(self):
        # ✅ FURNITURE PRICES IN INDIAN RUPEES (₹)
        # Based on average Indian market prices (Urban Ladder, Pepperfry, IKEA India)
        
        self.furniture_prices = {
            # Living Room
            'sofa': {'budget': 15000, 'mid-range': 35000, 'premium': 75000},
            'coffee table': {'budget': 3000, 'mid-range': 8000, 'premium': 20000},
            'tv stand': {'budget': 4000, 'mid-range': 12000, 'premium': 30000},
            'armchair': {'budget': 8000, 'mid-range': 18000, 'premium': 40000},
            'side table': {'budget': 2000, 'mid-range': 5000, 'premium': 12000},
            'floor lamp': {'budget': 1500, 'mid-range': 4000, 'premium': 10000},
            'rug': {'budget': 2500, 'mid-range': 8000, 'premium': 25000},
            'bookshelf': {'budget': 5000, 'mid-range': 12000, 'premium': 30000},
            'ottoman': {'budget': 4000, 'mid-range': 9000, 'premium': 20000},
            'console table': {'budget': 6000, 'mid-range': 15000, 'premium': 35000},
            
            # Bedroom
            'bed': {'budget': 12000, 'mid-range': 30000, 'premium': 80000},
            'nightstand': {'budget': 3000, 'mid-range': 7000, 'premium': 18000},
            'wardrobe': {'budget': 15000, 'mid-range': 35000, 'premium': 90000},
            'dresser': {'budget': 8000, 'mid-range': 18000, 'premium': 45000},
            'bedside lamp': {'budget': 1000, 'mid-range': 3000, 'premium': 8000},
            'mirror': {'budget': 2000, 'mid-range': 5000, 'premium': 15000},
            'vanity': {'budget': 10000, 'mid-range': 25000, 'premium': 60000},
            'reading chair': {'budget': 6000, 'mid-range': 15000, 'premium': 35000},
            'bench': {'budget': 4000, 'mid-range': 10000, 'premium': 25000},
            'reading lamp': {'budget': 1500, 'mid-range': 4000, 'premium': 10000},
            
            # Kitchen & Dining
            'dining table': {'budget': 10000, 'mid-range': 25000, 'premium': 65000},
            'dining chair': {'budget': 2000, 'mid-range': 5000, 'premium': 12000},
            'dining chairs': {'budget': 8000, 'mid-range': 20000, 'premium': 48000},  # Set of 4
            'bar stool': {'budget': 2000, 'mid-range': 5000, 'premium': 12000},
            'bar stools': {'budget': 6000, 'mid-range': 15000, 'premium': 36000},  # Set of 3
            'pendant light': {'budget': 2000, 'mid-range': 6000, 'premium': 18000},
            'pendant lights': {'budget': 5000, 'mid-range': 15000, 'premium': 45000},  # Set of 3
            'kitchen island': {'budget': 20000, 'mid-range': 45000, 'premium': 100000},
            'sideboard': {'budget': 12000, 'mid-range': 30000, 'premium': 75000},
            'wine rack': {'budget': 3000, 'mid-range': 8000, 'premium': 20000},
            'bar cart': {'budget': 5000, 'mid-range': 12000, 'premium': 30000},
            'chairs': {'budget': 6000, 'mid-range': 15000, 'premium': 36000},  # Set of 4
            
            # Office
            'desk': {'budget': 8000, 'mid-range': 18000, 'premium': 45000},
            'office chair': {'budget': 6000, 'mid-range': 15000, 'premium': 40000},
            'filing cabinet': {'budget': 5000, 'mid-range': 12000, 'premium': 28000},
            'desk lamp': {'budget': 1200, 'mid-range': 3500, 'premium': 9000},
            'credenza': {'budget': 15000, 'mid-range': 35000, 'premium': 80000},
            'study desk': {'budget': 7000, 'mid-range': 16000, 'premium': 40000},
            'chair': {'budget': 3000, 'mid-range': 8000, 'premium': 20000},
            
            # Bathroom
            'vanity': {'budget': 10000, 'mid-range': 25000, 'premium': 60000},
            'storage cabinet': {'budget': 6000, 'mid-range': 15000, 'premium': 35000},
            'towel rack': {'budget': 800, 'mid-range': 2000, 'premium': 5000},
            'bath mat': {'budget': 500, 'mid-range': 1500, 'premium': 4000},
            'decorative shelf': {'budget': 2000, 'mid-range': 5000, 'premium': 12000},
            'plant stand': {'budget': 1500, 'mid-range': 4000, 'premium': 10000},
            
            # Indian Specific Items
            'puja shelf': {'budget': 5000, 'mid-range': 12000, 'premium': 30000},
            'wooden puja mandir': {'budget': 10000, 'mid-range': 25000, 'premium': 65000},
            'deity idols': {'budget': 2000, 'mid-range': 5000, 'premium': 15000},
            'diya stand': {'budget': 1000, 'mid-range': 3000, 'premium': 8000},
            'brass diya': {'budget': 800, 'mid-range': 2000, 'premium': 6000},
            'prayer mat': {'budget': 500, 'mid-range': 1500, 'premium': 4000},
            'incense holder': {'budget': 400, 'mid-range': 1000, 'premium': 3000},
            'incense stand': {'budget': 600, 'mid-range': 1500, 'premium': 4000},
            'prayer bells': {'budget': 800, 'mid-range': 2500, 'premium': 7000},
            'traditional rug': {'budget': 3000, 'mid-range': 10000, 'premium': 30000},
            'ethnic wall art': {'budget': 2000, 'mid-range': 6000, 'premium': 18000},
            
            # Miscellaneous
            'wall art': {'budget': 1500, 'mid-range': 5000, 'premium': 15000},
            'centerpiece': {'budget': 1000, 'mid-range': 3000, 'premium': 9000},
            'wall shelves': {'budget': 3000, 'mid-range': 8000, 'premium': 20000},
            'toy storage': {'budget': 4000, 'mid-range': 10000, 'premium': 25000},
            'play table': {'budget': 5000, 'mid-range': 12000, 'premium': 28000},
            'bean bags': {'budget': 2000, 'mid-range': 5000, 'premium': 12000},
            'coat rack': {'budget': 2000, 'mid-range': 5000, 'premium': 12000},
        }
        
        # Installation and delivery costs (% of subtotal)
        self.installation_rate = 0.10  # 10% for installation/delivery
    
    def estimate_cost(self, furniture_items, budget_level='mid-range'):
        """
        Estimate total cost for furniture items
        
        Args:
            furniture_items: List of furniture item names
            budget_level: 'budget', 'mid-range', or 'premium'
        
        Returns:
            dict: Cost breakdown in INR
        """
        
        if budget_level not in ['budget', 'mid-range', 'premium']:
            budget_level = 'mid-range'
        
        items_with_costs = []
        subtotal = 0
        
        for item in furniture_items:
            item_lower = item.lower().strip()
            
            # Try exact match first
            if item_lower in self.furniture_prices:
                cost = self.furniture_prices[item_lower][budget_level]
                items_with_costs.append({
                    'name': item.title(),
                    'cost': cost,
                    'quantity': 1
                })
                subtotal += cost
            else:
                # Try partial match
                matched = False
                for key in self.furniture_prices:
                    if key in item_lower or item_lower in key:
                        cost = self.furniture_prices[key][budget_level]
                        items_with_costs.append({
                            'name': item.title(),
                            'cost': cost,
                            'quantity': 1
                        })
                        subtotal += cost
                        matched = True
                        break
                
                if not matched:
                    # Default price for unknown items
                    default_cost = 5000 if budget_level == 'budget' else (12000 if budget_level == 'mid-range' else 30000)
                    items_with_costs.append({
                        'name': item.title(),
                        'cost': default_cost,
                        'quantity': 1
                    })
                    subtotal += default_cost
        
        installation = subtotal * self.installation_rate
        total = subtotal + installation
        
        return {
            'items': items_with_costs,
            'subtotal': subtotal,
            'installation': installation,
            'total': total,
            'currency': 'INR',
            'budget_level': budget_level
        }
    
    def compare_budgets(self, furniture_items):
        """Compare costs across all budget levels"""
        
        comparisons = {}
        
        for level in ['budget', 'mid-range', 'premium']:
            comparisons[level] = self.estimate_cost(furniture_items, level)
        
        return comparisons
    
    def generate_cost_report(self, cost_breakdown):
        """Generate formatted cost report in INR"""
        
        if not cost_breakdown:
            return "No cost information available"
        
        lines = []
        lines.append(f"Budget Level: {cost_breakdown['budget_level'].title()}")
        lines.append(f"Currency: Indian Rupees (₹)")
        lines.append("\nItem Breakdown:")
        
        for item in cost_breakdown['items']:
            lines.append(f"  {item['name']}: ₹{item['cost']:,.2f}")
        
        lines.append(f"\nSubtotal: ₹{cost_breakdown['subtotal']:,.2f}")
        lines.append(f"Installation & Delivery (10%): ₹{cost_breakdown['installation']:,.2f}")
        lines.append(f"\nTOTAL COST: ₹{cost_breakdown['total']:,.2f}")
        
        return "\n".join(lines)
    
    def generate_comparison_report(self, comparisons):
        """Generate budget comparison report"""
        
        if not comparisons:
            return "No comparison data available"
        
        lines = []
        lines.append("Budget Comparison (in ₹):")
        lines.append("=" * 50)
        
        for level in ['budget', 'mid-range', 'premium']:
            if level in comparisons:
                total = comparisons[level]['total']
                lines.append(f"{level.title()}: ₹{total:,.2f}")
        
        return "\n".join(lines)


# Test
if __name__ == "__main__":
    estimator = CostEstimator()
    
    print("="*60)
    print("COST ESTIMATION TEST - INDIAN RUPEES")
    print("="*60)
    
    # Test bedroom furniture
    bedroom_items = ['bed', 'nightstand', 'wardrobe', 'dresser', 'bedside lamp']
    
    print("\nBedroom Furniture:")
    print(", ".join(bedroom_items))
    
    print("\n" + "="*60)
    print("MID-RANGE ESTIMATE")
    print("="*60)
    cost = estimator.estimate_cost(bedroom_items, 'mid-range')
    print(estimator.generate_cost_report(cost))
    
    print("\n" + "="*60)
    print("BUDGET COMPARISON")
    print("="*60)
    comparison = estimator.compare_budgets(bedroom_items)
    print(estimator.generate_comparison_report(comparison))
    
    # Test Indian specific items
    print("\n\n" + "="*60)
    print("POOJA ROOM FURNITURE")
    print("="*60)
    pooja_items = ['wooden puja mandir', 'deity idols', 'diya stand', 'prayer mat']
    cost = estimator.estimate_cost(pooja_items, 'mid-range')
    print(estimator.generate_cost_report(cost))