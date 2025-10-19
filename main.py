from typing import Optional
from fastapi import FastAPI
import mysql.connector

app = FastAPI()

def db_connect():
    mydb = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword"
    )
    print
    return 1+2
    
@app.get("/")
async def root():
    return {"message": "CRUD is working"}

@app.get("/add")
async def add(a:int,b:int):
   return int(a+b)

@app.get("/sub")
async def sub(a:int,b:int):
    return int(a-b)

@app.get("/multiply")
async def multiply(a:int,b:int):
    return int(a*b)

@app.get("divison")
async def division(a:int,b:int):
    return a/b