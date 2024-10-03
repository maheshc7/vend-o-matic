import os
import json
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from vending_machine import VendingMachine


class Coin(BaseModel):
    coin: Annotated[int, Field(strict=True, ge=1, le=1)]


app = FastAPI()

data_file = os.path.join(os.path.dirname(__file__), 'data', 'beverages.json')
vending_machine = VendingMachine(data_file)


@app.put("/", status_code=status.HTTP_204_NO_CONTENT)
def insert_coin(coin_input: Coin, response: Response):
    vending_machine.insert_coin(coin_input.coin)
    response.headers["X-Coins"] = str(vending_machine.coins)
    return {}


@ app.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def remove_coin(response: Response):
    balance_coins = vending_machine.eject_coins()
    response.headers["X-Coins"] = str(balance_coins)
    return {}


@ app.get("/inventory")
def get_inventory():
    return vending_machine.get_inventory()


@ app.get("/inventory/{item_id}")
def get_item(item_id: int):
    item_qty = vending_machine.get_inventory(item_id=item_id)
    if item_qty is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_qty


@ app.put("/inventory/{item_id}")
def purchase_item(item_id: int):
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
# TODO use .env to store credentials instead
USERNAME = "admin"
PASSWORD = "password123"


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@app.post("/inventory/reset")
def reset_inventory(credentials: HTTPBasicCredentials = Depends(authenticate)):
    # Reset the inventory to default
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_INVENTORY, f)
    return {"message": "Inventory has been reset to default."}
