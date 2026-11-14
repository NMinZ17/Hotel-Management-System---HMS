from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import Settings
from app.routers.rooms import router as rooms_router


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings.from_environment()
    application = FastAPI(
        title="HMS API",
        version="0.1.0",
        description="API quản lý khách sạn: kiểm tra dịch vụ và danh sách phòng.",
    )
    application.state.settings = settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @application.get("/", include_in_schema=False)
    def home() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    @application.get("/api/health", tags=["health"], summary="Kiểm tra dịch vụ API")
    def health() -> dict[str, str]:
        """Kiểm tra tiến trình API; gọi /api/rooms để kiểm tra dữ liệu PostgreSQL."""
        return {"status": "ok", "service": "hms-api"}

    application.include_router(rooms_router)
    return application


app = create_app()
