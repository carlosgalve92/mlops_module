from fastapi import APIRouter

from mlops.app.endpoints.predict import router as router_predict

router = APIRouter()

# Aquí registramos los endpoints de la versión v1
router.include_router(router_predict, prefix="/api", tags=["v1"])


if __name__ == "__main__":
    print("stop")
