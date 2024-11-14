from fastapi import APIRouter
from app.routers.routers_config import RoutesEnum
from app.global_state import GLOBAL_STATE


time_simulation_router = APIRouter(prefix=RoutesEnum.TIME_SIMULATION)


@time_simulation_router.get('/')
async def get_current_time():
    pass
