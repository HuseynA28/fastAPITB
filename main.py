from fastapi import FastAPI
from mall.model import Customer
from mall.database import create_db_and_tables


app = FastAPI()

# Creates all tables
create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/customers/{id}")
async def get_customer(id: int):
    return {"data": f"Customer id : {id}"}


@app.post("/customers")
async def create_customer(customer: Customer):
    return {"data": f"Customer {customer.CustomerID} is created."}