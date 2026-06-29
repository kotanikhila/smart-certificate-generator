# Add this to app/main.py
from .routers import analytics

app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
