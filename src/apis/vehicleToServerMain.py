import sys

sys.path.append('src')
from apis import userToServerAPIs, vehicleToServerAPIs
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(userToServerAPIs.router)
app.include_router(vehicleToServerAPIs.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "*" ],
    allow_credentials=True,
    allow_methods=[ "*" ],
    allow_headers=[ "*" ],
)
