from extensions import db
from models import Department, Category, Type
from app import app

with app.app_context():
    # Full hierarchy: Category → Types
    type_map = {
        "Mobile Phones": [
            "Smartphones", "Feature Phones", "Dual SIM Phones", "Android Phones", "iPhones",
            "Refurbished Phones", "Gaming Phones", "Budget Phones", "5G Phones", "Foldable Phones",
            "Touchscreen Phones", "Mini Phones", "Business Phones", "Camera Phones", "Rugged Phones",
            "Kids Phones", "Senior Phones", "Solar Phones", "Voice Phones", "Stylus Phones"
        ],
        "TVs": [
            "LED TVs", "Smart TVs", "OLED TVs", "QLED TVs", "4K TVs",
            "HD TVs", "Curved TVs", "Flat Screen TVs", "Mini TVs", "Portable TVs",
            "Digital TVs", "Satellite TVs", "TV Combos", "TV Monitors", "TV Projectors",
            "TV Boxes", "Streaming TVs", "Wall-Mount TVs", "TVs with DVD", "TVs with Soundbar"
        ],
        "Laptops": [
            "Gaming Laptop", "Business Laptop", "Student Laptop", "2-in-1 Convertible", "Ultrabook",
            "Chromebook", "MacBook", "Windows Laptop", "Linux Laptop", "Touchscreen Laptop",
            "Budget Laptop", "High-Performance Laptop", "Workstation", "Thin & Light", "Rugged Laptop",
            "Netbook", "Mini Laptop", "Portable Laptop", "Developer Laptop", "Multimedia Laptop"
        ],
        "Chargers": [
            "USB Chargers", "Type-C Chargers", "Wireless Chargers", "Fast Chargers", "Solar Chargers",
            "Laptop Chargers", "Car Chargers", "Multi-Port Chargers", "Universal Chargers", "Power Adapters",
            "Wall Chargers", "Travel Chargers", "MagSafe Chargers", "Smart Chargers", "Battery Chargers",
            "Docking Chargers", "Charging Stations", "Foldable Chargers", "Compact Chargers", "Heavy-Duty Chargers"
        ],
        "Speakers": [
            "Bluetooth Speakers", "Portable Speakers", "Home Theater", "Soundbars", "Smart Speakers",
            "Mini Speakers", "Waterproof Speakers", "Bass Speakers", "Wireless Speakers", "USB Speakers",
            "Rechargeable Speakers", "Outdoor Speakers", "Party Speakers", "Studio Monitors", "Ceiling Speakers",
            "Wall Speakers", "Bookshelf Speakers", "Subwoofers", "PA Speakers", "Solar Speakers"
        ],
        "Cables": [
            "USB Cables", "HDMI Cables", "Ethernet Cables", "Power Cables", "Audio Cables",
            "Video Cables", "Charging Cables", "Data Cables", "Extension Cables", "Lightning Cables",
            "Type-C Cables", "Micro USB Cables", "Coaxial Cables", "DisplayPort Cables", "VGA Cables",
            "Splitter Cables", "Adapter Cables", "Braided Cables", "Flat Cables", "Retractable Cables"
        ],
        "Smart Watches": [
            "Fitness Trackers", "Android Watches", "Apple Watches", "Hybrid Watches", "GPS Watches",
            "Kids Smartwatches", "Senior Smartwatches", "Luxury Smartwatches", "Budget Smartwatches", "Touchscreen Watches",
            "Waterproof Watches", "Solar Watches", "Bluetooth Watches", "Call-Enabled Watches", "Health Monitoring Watches",
            "Sleep Tracking Watches", "Sports Watches", "Fashion Watches", "Digital Watches", "Voice-Controlled Watches"
        ],
        "Power Banks": [
            "10,000mAh", "20,000mAh", "Solar Power Banks", "Fast Charging", "Wireless Power Banks",
            "Mini Power Banks", "Laptop Power Banks", "Multi-Port Power Banks", "Slim Power Banks", "Heavy-Duty Power Banks",
            "LED Display Power Banks", "USB-C Power Banks", "Magnetic Power Banks", "Waterproof Power Banks", "Smart Power Banks",
            "High Capacity", "Budget Power Banks", "Portable Chargers", "Emergency Power Banks", "Universal Power Banks"
        ],
        "Maize Flour": [
            "Super Maize", "Organic Maize", "Fortified Maize", "White Maize", "Yellow Maize",
            "Stone Ground Maize", "Sifted Maize", "Whole Grain Maize", "Maize Meal", "Maize Grits",
            "Maize Bran", "Maize Semolina", "Maize Porridge", "Maize Mix", "Maize Snacks",
            "Maize Baking Flour", "Maize Ugali Flour", "Maize Chapati Flour", "Maize Pancake Mix", "Maize Dumpling Mix"
        ],
        "Beans": [
            "Red Beans", "Yellow Beans", "Mixed Beans", "Black Beans", "Kidney Beans",
            "Pinto Beans", "White Beans", "Green Beans", "Soy Beans", "Lima Beans",
            "Butter Beans", "Navy Beans", "Mung Beans", "Bambara Beans", "Cowpeas",
            "Chickpeas", "Broad Beans", "Bean Flour", "Bean Snacks", "Bean Soup Mix"
        ],
        "Cooking Oil": [
            "Sunflower Oil", "Palm Oil", "Vegetable Oil", "Olive Oil", "Canola Oil",
            "Soybean Oil", "Coconut Oil", "Groundnut Oil", "Sesame Oil", "Corn Oil",
            "Avocado Oil", "Mustard Oil", "Blended Oil", "Refined Oil", "Cold Pressed Oil",
            "Organic Oil", "Deep Frying Oil", "Spray Oil", "Infused Oil", "Ghee"
        ],
        "Textbooks": [
            "Math Textbooks", "Science Textbooks", "Literature Textbooks", "History Textbooks", "Geography Textbooks",
            "Biology Textbooks", "Chemistry Textbooks", "Physics Textbooks", "Business Textbooks", "Economics Textbooks",
            "Civics Textbooks", "Religious Textbooks", "Agriculture Textbooks", "ICT Textbooks", "Language Textbooks",
            "Art Textbooks", "Music Textbooks", "Drama Textbooks", "Environmental Textbooks", "Entrepreneurship Textbooks"
        ],
        "Novels": [
            "African Fiction", "Romance", "Thrillers", "Mystery", "Historical Fiction",
            "Fantasy", "Science Fiction", "Adventure", "Drama", "Horror",
            "Young Adult", "Classic Novels", "Short Stories", "Graphic Novels", "Detective Novels",
            "Inspirational", "Political Fiction", "Satire", "Realistic Fiction", "Spiritual Fiction"
        ]
    }

    for cat_name, type_list in type_map.items():
        cat = Category.query.filter_by(name=cat_name).first()
        if cat:
            for type_name in type_list:
                if not Type.query.filter_by(name=type_name, category_id=cat.id).first():
                    db.session.add(Type(name=type_name, category_id=cat.id))

    db.session.commit()
    print("Type seeding complete.")