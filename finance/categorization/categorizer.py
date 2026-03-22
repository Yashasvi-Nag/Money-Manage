class Categorizer:
    DEFAULT_RULES = {
        "swiggy": "food",
        "dominos": "food",
        "zomato": "food",
        "uber": "travel",
        "ola": "travel",
        "amazon": "shopping",
        "flipkart": "shopping",
        "netflix": "entertainment",
        "spotify": "entertainment",
        "electricity": "utilities",
        "gym": "health",
        "pharmacy": "health",
        "hospital": "health",
        "petrol": "fuel",
        "fuel": "fuel",
        "atm": "cash",
    }

    def __init__(self, db):
        self.db = db
        self.custom_mappings = {}
        for row in db.get_category_mappings():
            self.custom_mappings[row["keyword"]] = row["category"]

    def categorize(self, description):
        desc = description.lower()
        for keyword, category in self.custom_mappings.items():
            if keyword in desc:
                return category
        for keyword, category in self.DEFAULT_RULES.items():
            if keyword in desc:
                return category
        return "uncategorized"

    def add_custom_mapping(self, keyword, category):
        self.db.insert_category_mapping(keyword, category)
        self.custom_mappings[keyword] = category
