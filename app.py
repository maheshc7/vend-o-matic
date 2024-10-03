import os
import json
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from vending_machine import VendingMachine


class Coin(BaseModel):
    '''
    Model representing the coin inserted into the vending machine.
    The coin field accepts exactly one denomination (here: one US quarter, denoted by integer value 1).
    '''
    coin: Annotated[int, Field(strict=True, ge=1, le=1)]


app = FastAPI()

# Set the path to the beverages JSON file, which stores the current inventory
data_file = os.path.join(os.path.dirname(__file__), 'data', 'beverages.json')
vending_machine = VendingMachine(data_file)


@app.put("/", status_code=status.HTTP_204_NO_CONTENT)
def insert_coin(coin_input: Coin, response: Response):
    '''
    Endpoint to insert a coin into the vending machine.
    Accepts a single coin and updates the machine's coin balance.

    Args:
        coin_input (Coin): The coin input, limited to one coin.
        response (Response): The response object used to set custom headers.

    Response Headers:
        X-Coins: The current total number of coins in the machine.

    Returns:
        An empty response body with a 204 No Content status.
    '''
    vending_machine.insert_coin(coin_input.coin)
    response.headers["X-Coins"] = str(vending_machine.coins)
    return {}


@ app.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def return_coins(response: Response):
    '''
    Endpoint to return all inserted coins from the vending machine.
    Resets the coin balance to zero and returns all coins to the user.

    Args:
        response (Response): The response object used to set custom headers.

    Response Headers:
        X-Coins: The number of coins returned to the user.

    Returns:
        An empty response body with a 204 No Content status.
    '''
    balance_coins = vending_machine.eject_coins()
    response.headers["X-Coins"] = str(balance_coins)
    return {}


@ app.get("/inventory")
def get_inventory():
    '''
    Endpoint to get the current inventory of all items in the vending machine.

    Returns:
        JSON list of all items with their remaining stock.
    '''
    return vending_machine.get_inventory()


@ app.get("/inventory/{item_id}")
def get_item(item_id: int):
    '''
    Endpoint to retrieve the current stock of an item by its ID.

    Args:
        item_id (int): The ID of the item.

    Returns:
        The remaining stock of the item, or a 404 error if the item is not found.
    '''
    item_qty = vending_machine.get_inventory(item_id=item_id)
    if item_qty is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_qty


@ app.put("/inventory/{item_id}")
def purchase_item(item_id: int):
    '''
    Endpoint to attempt purchasing an item from the vending machine.

    Args:
        item_id (int): The ID of the item to be purchased.

    Returns:
        - On success: Returns 200 with the number of items vended and any balance coins.
        - On insufficient coins: Returns 403 with the coin balance.
        - On out of stock: Returns 404 with the coin balance.
    '''
    status_code, balance_coins, item_count = vending_machine.dispense_item(
        item_id=item_id)
    response = {"quantity": item_count}
    if status_code == 200:

        item_qty = str(vending_machine.get_inventory(item_id=item_id))
        headers = {"X-Coins": str(balance_coins),
                   "X-Inventory-Remaining": item_qty}

        return JSONResponse(content=response, status_code=status_code, headers=headers)

    if status_code in (403, 404):
        headers = {"X-Coins": str(balance_coins)}

        raise HTTPException(status_code=status_code, headers=headers)


# Default inventory state
DEFAULT_INVENTORY = {
    "1": {
        "name": "Cola",
        "price": 2,
        "stock": 5
    },
    "2": {
        "name": "Pepsi",
        "price": 2,
        "stock": 5
    },
    "3": {
        "name": "Sprite",
        "price": 2,
        "stock": 5
    }
}

# Basic Authentication setup
security = HTTPBasic()

# Default admin credentials
# TODO: Use environment variables or secure vaults for credentials in production
USERNAME = "admin"
PASSWORD = "password123"


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    '''
    Basic authentication for admin endpoints. Validates the provided username and password.

    Args:
        credentials (HTTPBasicCredentials): The credentials provided by the client.

    Raises:
        HTTPException: If the credentials are invalid.

    Returns:
        The credentials object if authentication is successful.
    '''
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@app.post("/inventory/reset")
def reset_inventory(credentials: HTTPBasicCredentials = Depends(authenticate)):
    '''
    Endpoint to reset the vending machine inventory to its default state.
    This is a protected admin-only route requiring basic authentication.

    Args:
        credentials (HTTPBasicCredentials): Credentials to authenticate the admin.

    Returns:
        A success message indicating the inventory has been reset.
    '''
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_INVENTORY, f)
    return {"message": "Inventory has been reset to default."}
