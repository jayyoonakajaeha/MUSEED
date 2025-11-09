from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["status"]
)

@router.get("/status")
def get_status():
    """
    A simple endpoint to check if the backend is running.
    """
    return {"status": "ok"}
