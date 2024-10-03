from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_insert_coin():
    """Test inserting a valid coin into the vending machine."""
    response = client.put("/", json={'coin': 1})
    assert response.status_code == 204
    assert response.headers['X-Coins'] == '1'
    client.delete("/")


def test_insert_coin_error():
    """Test inserting invalid coin(s) into the vending machine."""
    response = client.put("/", json={'coin': 2})
    assert response.status_code == 422


def test_remove_coins():
    """Test ejecting coins from the vending machine."""
    # Insert coin
    client.put("/", json={'coin': 1})
    # Remove coin
    response = client.delete("/")
    assert response.status_code == 204
    assert response.headers["X-Coins"] == '1'


def test_inventory():
    """Test getting the stock of all items."""
    response = client.get("/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert all(isinstance(qty, int) for qty in response.json())


def test_dispense_item_success():
    """Test successfully dispensing an item when conditions are met."""
    # Ensure there are no balance coins
    client.delete("/")
    # Insert three quarters
    client.put("/", json={'coin': 1})
    client.put("/", json={'coin': 1})
    client.put("/", json={'coin': 1})

    final_qty = client.get("/inventory/1").json() - 1
    response = client.put("/inventory/1")
    assert response.status_code == 200
    print(response.json(), response.headers)
    assert response.json()["quantity"] == 1
    assert response.headers['X-Coins'] == '1'
    assert response.headers['X-Inventory-Remaining'] == str(final_qty)


def test_dispense_item_invalid():
    """Test dispensing an item when it is invalid."""
    # Ensure there are no balance coins
    client.delete("/")
    # Insert single quarter
    client.put("/", json={'coin': 1})
    client.put("/", json={'coin': 1})

    response = client.put("/inventory/123")
    assert response.status_code == 404
    assert response.headers['X-Coins'] == '2'


def test_dispense_item_insufficient_coins():
    """Test dispensing an item when the coins are insufficient."""
    # Ensure there are no balance coins
    client.delete("/")
    # Insert single quarter
    client.put("/", json={'coin': 1})
    response = client.put("/inventory/1")
    assert response.status_code == 403
    assert response.headers['X-Coins'] == '1'
