import json


class VendingMachine:
    def __init__(self, file_path):
        self.file_path = file_path
        self.inventory = self.load_inventory()
        self.coins = 0

    def load_inventory(self):
        with open(self.file_path, encoding="utf-8") as file:
            beverages = json.load(file)
            beverages = {int(k): v for k, v in beverages.items()}
            return beverages

    def save_inventory(self):
        with open(self.file_path, 'w', encoding="utf-8") as file:
            json.dump(self.inventory, file, indent=4)

    def insert_coin(self, coin):
        if coin == 1:
            self.coins += coin

    def eject_coins(self):
        return_coins = self.coins
        self.coins = 0
        return return_coins

    def get_coins(self):
        return self.coins

    def get_inventory(self, item_id=None):
        if not item_id:
            return [item["stock"] for item_id, item in self.inventory.items()]
        else:
            if item_id in self.inventory:
                return self.inventory[item_id]["stock"]

    def dispense_item(self, item_id):
        # Item not found
        if item_id not in self.inventory:
            return 404, self.coins, None

        item = self.inventory[item_id]

        # Item out of stock
        if item['stock'] == 0:
            return 404, self.coins, None

        # Insufficient coins
        if self.coins < item['price']:
            return 403, self.coins, None

        # Success
        item['stock'] -= 1
        change = self.coins - item['price']
        self.coins = change
        self.eject_coins()
        self.save_inventory()

        return 200, change, 1
