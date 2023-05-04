

class LostItemError(Exception):
    def __init__(self, stock_items: int, final_result_items: int):
        self.text = "Some items were lost\n" \
                    f"Items in stock: {stock_items}\n" \
                    f"Items in assortiment: {final_result_items}"