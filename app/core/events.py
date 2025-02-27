from typing import Callable
from fastapi import FastAPI

def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        # Add any startup events here
        pass

    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        # Add any cleanup events here
        pass

    return stop_app