from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_insert_coin():
    response = client.put("/", json={'coin': 1})
    assert response.status_code == 204
    assert response.headers['X-Coins'] == '1'
    client.delete("/")


def test_insert_coin_error():
    response = client.put("/", json={'coin': 2})
    assert response.status_code == 422


def test_remove_coins():
    # Insert coin
    client.put("/", json={'coin': 1})
    # Remove coin
    response = client.delete("/")
    assert response.status_code == 204
    assert response.headers["X-Coins"] == '1'


def test_inventory():
    response = client.get("/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert all(isinstance(qty, int) for qty in response.json())


def test_dispense_item_success():
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


def test_dispense_item_out_of_stock():
    # Ensure there are no balance coins
    client.delete("/")
    # Insert single quarter
    client.put("/", json={'coin': 1})
    client.put("/", json={'coin': 1})

    response = client.put("/inventory/123")
    assert response.status_code == 404
    assert response.headers['X-Coins'] == '2'


def test_dispense_item_insufficient_coins():
    # Ensure there are no balance coins
    client.delete("/")
    # Insert single quarter
    client.put("/", json={'coin': 1})
    response = client.put("/inventory/1")
    assert response.status_code == 403
    assert response.headers['X-Coins'] == '1'
