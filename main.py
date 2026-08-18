from fastapi import FastAPI

import mlops
from mlops.app.router import router

app = FastAPI(title=rf"{mlops.__name__}", version=rf"{mlops.__version__}")

app.include_router(router)
