from typing import Dict, List

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer


# -----------------------------
# Shop type normalization
# -----------------------------
SHOP_TYPE_ALIASES = {
    "minimart": "minimart",
    "mini mart": "minimart",
    "mini_mart": "minimart",
    "grocery shop": "minimart",
    "grocery_shop": "minimart",

    "snack shop": "snack_shop",
    "snack_shop": "snack_shop",
    "snack & beverage store": "snack_shop",
    "snack and beverage store": "snack_shop",

    "general store": "general_store",
    "general_store": "general_store",
}

SHOP_DISPLAY_NAMES = {
    "minimart": "Mini Mart",
    "snack_shop": "Snack Shop",
    "general_store": "General Store",
}


def normalize_shop_type(shop_type: str) -> str:
    key = shop_type.strip().lower().replace("-", " ").replace("_", " ")
    if key not in SHOP_TYPE_ALIASES:
        raise ValueError(
            f"Invalid shop type '{shop_type}'. "
            f"Use one of: minimart, snack_shop, general_store"
        )
    return SHOP_TYPE_ALIASES[key]


def display_shop_type(shop_type: str) -> str:
    return SHOP_DISPLAY_NAMES[normalize_shop_type(shop_type)]


# -----------------------------
# Inventory by shop type
# -----------------------------
SHOP_INVENTORY = {
    "minimart": [
        "Bread", "Butter", "Jam", "Milk", "Tea", "Sugar",
        "Biscuits", "Instant Noodles", "Soup Pack", "Namkeen"
    ],
    "snack_shop": [
        "Chips", "Namkeen", "Cold Drink", "Juice",
        "Chocolate", "Ice Cream", "Biscuits", "Tea", "Coffee"
    ],
    "general_store": [
        "Soap", "Shampoo", "Detergent", "Umbrella",
        "Dry Fruits", "Tea", "Sugar", "Milk", "Biscuits", "Coffee"
    ],
}


def get_inventory_for_shop_type(shop_type: str) -> List[str]:
    shop_type = normalize_shop_type(shop_type)
    return SHOP_INVENTORY[shop_type]


# -----------------------------
# Simulated transaction data
# Use exact product names from seed.py
# -----------------------------
SHOP_TRANSACTIONS: Dict[str, List[List[str]]] = {
    "minimart": [
        ["Bread", "Milk", "Butter"],
        ["Bread", "Jam", "Butter"],
        ["Milk", "Bread", "Biscuits"],
        ["Bread", "Tea", "Sugar"],
        ["Instant Noodles", "Soup Pack", "Tea"],
        ["Milk", "Tea", "Sugar"],
        ["Bread", "Butter", "Jam"],
        ["Milk", "Bread", "Butter"],
        ["Biscuits", "Tea", "Sugar"],
        ["Bread", "Milk", "Jam"],
        ["Instant Noodles", "Tea", "Namkeen"],
        ["Bread", "Milk", "Chocolate"],
    ],
    "snack_shop": [
        ["Chips", "Cold Drink", "Chocolate"],
        ["Chips", "Juice", "Namkeen"],
        ["Biscuits", "Tea", "Chocolate"],
        ["Tea", "Chips", "Namkeen"],
        ["Cold Drink", "Chips", "Chocolate"],
        ["Juice", "Biscuits", "Chips"],
        ["Chocolate", "Ice Cream", "Cold Drink"],
        ["Namkeen", "Tea", "Biscuits"],
        ["Chips", "Chocolate", "Cold Drink"],
        ["Juice", "Cold Drink", "Namkeen"],
        ["Ice Cream", "Chocolate", "Cold Drink"],
        ["Chips", "Biscuits", "Juice"],
    ],
    "general_store": [
        ["Soap", "Shampoo", "Detergent"],
        ["Soap", "Shampoo"],
        ["Detergent", "Soap", "Umbrella"],
        ["Sugar", "Tea", "Milk"],
        ["Soap", "Detergent"],
        ["Umbrella", "Soap", "Detergent"],
        ["Dry Fruits", "Coffee", "Chocolate"],
        ["Soup Pack", "Tea", "Coffee"],
        ["Sugar", "Tea", "Biscuits"],
        ["Milk", "Sugar", "Tea"],
        ["Soap", "Shampoo", "Detergent"],
        ["Dry Fruits", "Coffee", "Biscuits"],
    ],
}


def build_shop_model(transactions: List[List[str]]) -> Dict:
    mlb = MultiLabelBinarizer()
    binary_matrix = mlb.fit_transform(transactions)

    transaction_item_df = pd.DataFrame(binary_matrix, columns=mlb.classes_)
    item_vectors = transaction_item_df.T

    similarity_matrix = cosine_similarity(item_vectors)

    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=item_vectors.index,
        columns=item_vectors.index
    )

    return {
        "mlb": mlb,
        "transaction_item_df": transaction_item_df,
        "similarity_df": similarity_df,
        "items": list(item_vectors.index),
    }


MODELS = {
    shop_type: build_shop_model(transactions)
    for shop_type, transactions in SHOP_TRANSACTIONS.items()
}


def recommend(item_name: str, shop_type: str, top_n: int = 4) -> List[Dict]:
    shop_type = normalize_shop_type(shop_type)
    top_n = max(3, min(top_n, 5))

    model = MODELS[shop_type]
    similarity_df = model["similarity_df"]

    item_lookup = {name.lower(): name for name in similarity_df.index}
    selected_item = item_lookup.get(item_name.strip().lower())

    if not selected_item:
        raise ValueError(
            f"Item '{item_name}' not found for shop type '{shop_type}'."
        )

    scores = similarity_df.loc[selected_item]
    sorted_scores = scores.drop(selected_item).sort_values(ascending=False)
    sorted_scores = sorted_scores[sorted_scores > 0]

    top_items = sorted_scores.head(top_n)

    return [
        {"name": item, "score": round(float(score), 4)}
        for item, score in top_items.items()
    ]