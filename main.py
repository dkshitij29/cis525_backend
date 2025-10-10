from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

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