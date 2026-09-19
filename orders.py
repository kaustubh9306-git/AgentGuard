# orders.py

class MockOrderAPI:
    def __init__(self):
        self.orders = []

    def execute_order(self, product, user_requirements):
        """
        Executes the purchase only if authorized.
        In a real system, this would call the payment gateway and order database.
        """
        order_id = f"ORD-{len(self.orders) + 1001}"
        order_record = {
            "order_id": order_id,
            "product_name": product["name"],
            "price": product["price"],
            "status": "SUCCESS"
        }
        self.orders.append(order_record)
        return order_record

# Global instance for the simulation
order_api = MockOrderAPI()

# orders.py

def execute_order(product):
    """
    Simulates calling the e-commerce purchase API 
    once AgentGuard approves the transaction.
    """
    return {
        "status": "success",
        "message": f"Order successfully placed for {product['name']} at ₹{product['price']}!",
        "order_id": "ORD-84920"
    }