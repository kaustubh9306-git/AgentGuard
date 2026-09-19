from products import products


def search_products(category, max_price=None, min_storage=None):
    results = []

    for product in products:

        if product["category"] != category:
            continue

        if max_price is not None and product["price"] > max_price:
            continue

        if min_storage is not None and product["storage_gb"] < min_storage:
            continue

        results.append(product)

    return results