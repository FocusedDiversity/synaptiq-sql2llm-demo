"""Static data for generating realistic vehicle records."""

# Make -> list of models
VEHICLE_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma", "Tundra", "Prius", "4Runner", "Sienna"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "HR-V", "Odyssey", "Ridgeline", "Fit"],
    "Ford": ["F-150", "Escape", "Explorer", "Mustang", "Edge", "Bronco", "Ranger", "Expedition"],
    "Chevrolet": ["Silverado", "Equinox", "Malibu", "Traverse", "Tahoe", "Camaro", "Colorado", "Suburban"],
    "Nissan": ["Altima", "Rogue", "Sentra", "Pathfinder", "Frontier", "Murano", "Maxima", "Kicks"],
    "Hyundai": ["Elantra", "Tucson", "Santa Fe", "Sonata", "Kona", "Palisade", "Venue"],
    "Kia": ["Forte", "Sportage", "Seltos", "Sorento", "Telluride", "Soul", "K5"],
    "Subaru": ["Outback", "Forester", "Crosstrek", "Impreza", "Ascent", "WRX"],
    "Volkswagen": ["Jetta", "Tiguan", "Atlas", "Taos", "Golf", "ID.4"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "X1"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE", "A-Class"],
    "Jeep": ["Wrangler", "Grand Cherokee", "Cherokee", "Compass", "Gladiator"],
    "Ram": ["1500", "2500", "ProMaster"],
    "GMC": ["Sierra", "Terrain", "Acadia", "Yukon", "Canyon"],
    "Mazda": ["CX-5", "Mazda3", "CX-30", "CX-50", "MX-5 Miata"],
    "Lexus": ["RX", "ES", "NX", "IS", "GX"],
    "Audi": ["A4", "Q5", "A3", "Q7", "Q3"],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X"],
    "Dodge": ["Charger", "Challenger", "Durango", "Hornet"],
    "Buick": ["Encore", "Envision", "Enclave"],
}

# Model -> vehicle type mapping
MODEL_TYPES = {
    # Sedans
    "Camry": "sedan", "Corolla": "sedan", "Prius": "sedan",
    "Civic": "sedan", "Accord": "sedan", "Fit": "sedan",
    "Mustang": "coupe", "Malibu": "sedan",
    "Altima": "sedan", "Sentra": "sedan", "Maxima": "sedan",
    "Elantra": "sedan", "Sonata": "sedan",
    "Forte": "sedan", "K5": "sedan",
    "Impreza": "sedan", "WRX": "sedan",
    "Jetta": "sedan", "Golf": "sedan",
    "3 Series": "sedan", "5 Series": "sedan",
    "C-Class": "sedan", "E-Class": "sedan", "A-Class": "sedan",
    "Mazda3": "sedan", "MX-5 Miata": "coupe",
    "ES": "sedan", "IS": "sedan",
    "A4": "sedan", "A3": "sedan",
    "Model 3": "sedan", "Model S": "sedan",
    "Charger": "sedan", "Challenger": "coupe",
    "Soul": "sedan", "Venue": "sedan", "Kicks": "sedan",
    # SUVs
    "RAV4": "suv", "Highlander": "suv", "4Runner": "suv",
    "CR-V": "suv", "Pilot": "suv", "HR-V": "suv",
    "Escape": "suv", "Explorer": "suv", "Edge": "suv", "Bronco": "suv", "Expedition": "suv",
    "Equinox": "suv", "Traverse": "suv", "Tahoe": "suv", "Suburban": "suv",
    "Rogue": "suv", "Pathfinder": "suv", "Murano": "suv",
    "Tucson": "suv", "Santa Fe": "suv", "Kona": "suv", "Palisade": "suv",
    "Sportage": "suv", "Seltos": "suv", "Sorento": "suv", "Telluride": "suv",
    "Outback": "suv", "Forester": "suv", "Crosstrek": "suv", "Ascent": "suv",
    "Tiguan": "suv", "Atlas": "suv", "Taos": "suv", "ID.4": "suv",
    "X3": "suv", "X5": "suv", "X1": "suv",
    "GLC": "suv", "GLE": "suv",
    "Wrangler": "suv", "Grand Cherokee": "suv", "Cherokee": "suv", "Compass": "suv",
    "Terrain": "suv", "Acadia": "suv", "Yukon": "suv",
    "CX-5": "suv", "CX-30": "suv", "CX-50": "suv",
    "RX": "suv", "NX": "suv", "GX": "suv",
    "Q5": "suv", "Q7": "suv", "Q3": "suv",
    "Model Y": "suv", "Model X": "suv",
    "Durango": "suv", "Hornet": "suv",
    "Encore": "suv", "Envision": "suv", "Enclave": "suv",
    # Trucks
    "Tacoma": "truck", "Tundra": "truck",
    "F-150": "truck", "Ranger": "truck",
    "Silverado": "truck", "Colorado": "truck",
    "Frontier": "truck",
    "Ridgeline": "truck",
    "Gladiator": "truck",
    "1500": "truck", "2500": "truck",
    "Sierra": "truck", "Canyon": "truck",
    "Camaro": "coupe",
    # Vans
    "Sienna": "van", "Odyssey": "van", "ProMaster": "van",
}

COLORS = [
    "White", "Black", "Silver", "Gray", "Red", "Blue", "Brown",
    "Green", "Beige", "Orange", "Gold", "Yellow", "Purple",
    "Burgundy", "Navy", "Charcoal",
]

# Weighted distribution - white/black/silver/gray are most common
COLOR_WEIGHTS = [
    18, 16, 14, 12, 8, 7, 5,
    3, 3, 2, 2, 1, 1,
    2, 3, 3,
]

# Make popularity weights (roughly reflects US market share)
MAKE_WEIGHTS = {
    "Toyota": 15, "Honda": 10, "Ford": 14, "Chevrolet": 12, "Nissan": 7,
    "Hyundai": 6, "Kia": 5, "Subaru": 4, "Volkswagen": 3, "BMW": 3,
    "Mercedes-Benz": 3, "Jeep": 6, "Ram": 5, "GMC": 4, "Mazda": 3,
    "Lexus": 2, "Audi": 2, "Tesla": 4, "Dodge": 3, "Buick": 2,
}
