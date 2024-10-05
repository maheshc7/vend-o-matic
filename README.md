# vend-o-matic

Service supporting beverage vending machine

# Vending Machine API

This is a simple API service for a vending machine that accepts US quarters to purchase beverages. The machine has a limited inventory, and the service handles coin insertion, item vending, inventory management, and coin refunds. This project is a simple implementation designed to be lightweight and easily testable.

## Table of Contents

1. [Installation](#installation)
2. [Running the Application](#running-the-application)
3. [API Documentation](#api-documentation)
4. [Testing](#testing)
5. [Postman Collection](#postman-collection)
6. [Future Improvements](#future-improvements)

## Installation

To install and run the application, follow the steps below:

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn (ASGI server)
- `pip` (Python package installer)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/maheshc7/vend-o-matic.git
   cd vend-o-matic
   ```

2. Set up a virtual environment (recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/MacOS
   # OR
   venv\Scripts\activate  # For Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) You can edit the `beverages.json` file to modify the initial inventory of the vending machine.
   Or use the Postman collection to reset the inventory.
   The POST /inventory/reset endpoint is protected by authentication.
   If authenticated, the inventory is reset by overwriting the beverages.json file with the default inventory.

## Running the Application

Once dependencies are installed, you can run the application with the following command:

```bash
uvicorn app:app --reload
```

This will start the FastAPI application with hot-reloading enabled, making it easy for development.

## API Documentation

The API follows REST conventions and allows you to interact with the vending machine for:

- Inserting coins.
- Checking the inventory.
- Vending an item.
- Refunding coins.

### Swagger UI for API Documentation

FastAPI automatically provides interactive API documentation with Swagger. You can access the Swagger docs at the following URL after running the application:

- [Swagger API Documentation](http://127.0.0.1:8000/docs)

You can test out all API endpoints directly via this interface.

## Testing

The project uses `pytest` to run unit tests. Make sure all tests pass before deploying or making changes.

### Steps to run tests:

1. Install `pytest`:

   ```bash
   pip install pytest
   pip install httpx
   ```

2. Run the tests:

   ```bash
   python3 -m pytest
   ```

Tests include scenarios for:

- Valid and invalid coin insertion.
- Vending items when enough coins are inserted.
- Handling out-of-stock items.
- Refunding unused coins.

## Postman Collection

You can use [Postman](https://www.postman.com/) to manually test the API. A Postman collection and environment are provided to simplify this process.

- **Postman Collection**: [Vend-O-Matic.postman_collection.json](./postman/Vend-O-Matic.postman_collection.json)
- **Postman Environment**: [vend-o-matic.postman_environment.json](./postman/vend-o-matic.postman_environment.json)

To use the Postman collection:

1. Download and import both files into your Postman workspace.
2. Use the environment to automatically set base URLs and variables.
3. Execute the requests from the collection to simulate real-world interactions with the vending machine.

## Future Improvements

### Containerization with Docker

For easier deployment and environment consistency, the entire application can be containerized using Docker. You can build a Docker image with a `Dockerfile`, and run the application inside a containerized environment.

### Database Integration

Currently, the system stores all state information (coins inserted, inventory) in memory and JSON files. For production use, a database (e.g., SQLite, PostgreSQL) can be added to handle transactions and state management reliably.

With a database:

- Inventory can be managed more efficiently.
- Transactions (coin inserts, purchases) can be atomic and durable.
- Coin balances and sales data can be stored persistently.
