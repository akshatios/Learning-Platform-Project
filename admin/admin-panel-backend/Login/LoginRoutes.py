from fastapi import APIRouter
from Login.views.login import login

router = APIRouter(prefix="/auth", tags=["Authentication"])

router.add_api_route("/login", login, methods=["POST"])