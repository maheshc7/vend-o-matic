import json


class VendingMachine:
    '''
    A class to represent a vending machine that manages inventory and coin transactions.

    Attributes:
        file_path (str): The path to the JSON file containing the inventory data.
        inventory (dict): A dictionary representing the available beverages and their stock.
        coins (int): The current amount of coins inserted into the vending machine.
    '''

    def __init__(self, file_path):
        self.file_path = file_path
        self.inventory = self.load_inventory()
        self.coins = 0

    def load_inventory(self):
        '''
        Loads the inventory from the JSON file.

        Returns:
            dict: A dictionary containing the beverages and their corresponding name, stock and price, 
                  with integer keys for item IDs.
        '''
        with open(self.file_path, encoding="utf-8") as file:
            beverages = json.load(file)
            beverages = {int(k): v for k, v in beverages.items()}
            return beverages

    def save_inventory(self):
        '''
        Saves the current inventory state back to the JSON file.
        This method updates the JSON file to reflect changes made to the inventory.
        '''
        with open(self.file_path, 'w', encoding="utf-8") as file:
            json.dump(self.inventory, file, indent=4)

    def insert_coin(self, coin):
        '''
        Inserts a coin into the vending machine.

        Args:
            coin (int): The value of the coin being inserted. Only accepts a coin of value 1.
        '''
        if coin == 1:
            self.coins += coin

    def eject_coins(self):
        '''
        Returns the coins currently in the vending machine back to the user.

        Returns:
            int: The total amount of coins that are being returned.
        '''
        return_coins = self.coins
        self.coins = 0
        return return_coins

    def get_coins(self):
        # Return the current coin balance
        return self.coins

    def get_inventory(self, item_id=None):
        '''
        Retrieves the stock of beverages in the inventory.

        Args:
            item_id (int, optional): The ID of a specific beverage to retrieve stock for.

        Returns:
            list or int: If no item_id is provided, returns a list of stock levels for all items.
                          If item_id is provided, returns the stock level for that specific item.
        '''
        if not item_id:
            return [item["stock"] for item_id, item in self.inventory.items()]
        else:
            if item_id in self.inventory:
                return self.inventory[item_id]["stock"]

    def dispense_item(self, item_id):
        '''
        Dispenses the specified item if conditions are met (item exists, in stock, and sufficient coins).

        Args:
            item_id (int): The ID of the beverage to dispense.

        Returns:
            tuple: A tuple containing the response code, change amount, and quantity vended.
                   - 200: Successful transaction, with change and quantity.
                   - 404: Item not found or out of stock, with coins unchanged.
                   - 403: Insufficient coins for the transaction, with coins unchanged.
        '''
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
