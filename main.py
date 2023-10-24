from fastapi import FastAPI, Request, status
from pydantic import BaseModel
import challonge
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Union

class ApiData(BaseModel):
    name: str
    key: str

class PlayerIDs(BaseModel):
    p1: Union[int, None]
    p2: Union[int, None]
    np1: Union[int, None]
    np2: Union[int, None]
    pp1: Union[int, None]
    pp2: Union[int, None]

class PushData(BaseModel):
    id: int
    winner: int
    p1score: int
    p2score: int

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/{id}/matches")
async def getmatch(id):
    matches = challonge.matches.index(id)
    return matches

@app.post("/setapi")
async def setapi(apidata: ApiData):
    username = apidata.name
    apikey = apidata.key
    challonge.set_credentials(username, apikey)
    return {"message": "Done!"}

@app.post("/{id}/getplayers")
async def getplayers(ids: PlayerIDs, id):
    p1 = None
    p2 = None
    np1 = None
    np2 = None
    pp1 = None
    pp2 = None
    if ids.p1:
        p1 = challonge.participants.show(id, ids.p1)
    if ids.p2:
        p2 = challonge.participants.show(id, ids.p2)
    if ids.np1:
        np1 = challonge.participants.show(id, ids.np1)
    if ids.np2:
        np2 = challonge.participants.show(id, ids.np2)
    if ids.pp1:
        pp1 = challonge.participants.show(id, ids.pp1)
    if ids.pp2:
        pp2 = challonge.participants.show(id, ids.pp2)

    value = jsonable_encoder({"p1":p1,"p2":p2,"np1":np1,"np2":np2,"pp1":pp1,"pp2":pp2})
    return JSONResponse(content=value)

@app.post("/{id}/match/update")
async def UpdateMatch(data: PushData, id):
    s = str(data.p1score) + "-" + str(data.p2score)
    challonge.matches.update(
        id, data.id, scores_csv=s,winner_id=data.winner
    )

