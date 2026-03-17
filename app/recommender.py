from collections import Counter
from . import models


def dashboard_metrics(db, shopkeeper_id):
    logs = (
        db.query(models.SearchLog)
        .filter(models.SearchLog.shopkeeper_id == shopkeeper_id)
        .all()
    )

    total_searches = len(logs)
    product_names = [log.product.name for log in logs if log.product]
    top_products = Counter(product_names).most_common(5)

    return {
        "total_searches": total_searches,
        "unique_products_searched": len(set(product_names)),
        "top_product": top_products[0][0] if top_products else "No Data",
        "top_products": top_products,
    }