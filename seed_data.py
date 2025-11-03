from extensions import db
from models import Department, Category
from app import app

with app.app_context():
    # Seed Departments (African + global)
    departments = [
        "Electronics", "Grocery", "Health & Beauty", "Bakery", "Dairy",
        "Meat & Seafood", "Frozen Foods", "Beverages", "Household Supplies", "Baby & Kids",
        "Pet Care", "Stationery", "Clothing", "Footwear", "Home Decor",
        "Cleaning Supplies", "Pharmacy", "Books", "Toys", "Automotive",
        "Agriculture", "Construction", "Mobile Money", "Textiles", "Cosmetics",
        "Traditional Medicine", "Livestock", "Furniture", "Kitchenware", "Hardware",
        "Sports & Fitness", "Jewelry", "Art & Crafts", "Travel & Luggage", "Security",
        "Solar & Energy", "Computing", "Printing Services", "Tailoring", "Cultural Wear"
    ]
    for name in departments:
        if not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name))

    db.session.commit()

    # Seed Categories (mapped to departments)
    category_map = {
        "Electronics": ["Mobile Phones", "TVs", "Laptops", "Chargers", "Speakers", "Cables", "Smart Watches", "Power Banks"],
        "Grocery": ["Maize Flour", "Beans", "Cooking Oil", "Salt", "Sugar", "Tea Leaves", "Spices", "Canned Goods"],
        "Health & Beauty": ["Body Lotion", "Shampoo", "Toothpaste", "Sanitary Pads", "Perfume", "Hair Gel", "Face Cream", "Deodorant"],
        "Bakery": ["Bread", "Mandazi", "Chapati", "Cakes", "Cookies", "Buns", "Donuts", "Croissants"],
        "Dairy": ["Milk", "Cheese", "Yogurt", "Butter", "Ghee", "Cream", "Ice Cream", "Powdered Milk"],
        "Clothing": ["Men's Wear", "Women's Wear", "Children's Wear", "School Uniforms", "Suits", "Jeans", "T-Shirts", "Dresses"],
        "Footwear": ["Sneakers", "Sandals", "Boots", "Heels", "Slippers", "School Shoes", "Loafers", "Flip-Flops"],
        "Books": ["Textbooks", "Novels", "Bibles", "Qurans", "Magazines", "Children's Books", "Atlases", "Dictionaries"],
        "Furniture": ["Sofas", "Beds", "Tables", "Chairs", "Wardrobes", "Cabinets", "TV Stands", "Office Desks"],
        "Agriculture": ["Seeds", "Fertilizers", "Pesticides", "Farm Tools", "Irrigation Kits", "Animal Feed", "Greenhouse Supplies", "Harvest Bags"]
    }

    for dept_name, categories in category_map.items():
        dept = Department.query.filter_by(name=dept_name).first()
        if dept:
            for cat_name in categories:
                if not Category.query.filter_by(name=cat_name, department_id=dept.id).first():
                    db.session.add(Category(name=cat_name, department_id=dept.id))

    db.session.commit()
    print("Seeding complete.")