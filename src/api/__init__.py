import os

from fastapi import APIRouter

from src.api.routes import demo_stage

router = APIRouter(prefix="/api/v1")

# Register route modules here as they are created:
# from src.api.routes import people, projects
# router.include_router(people.router)

# The demo stage read routes (talking-points content, generated overview location) are
# read-only and carry no capability of their own, so — unlike the terminal route below — they
# are registered unconditionally, not gated by D_SYSTEM_DEMO_TERMINAL.
router.include_router(demo_stage.router, prefix="/demo/stage")

# The demo terminal route (ADR-013) is registered only when D_SYSTEM_DEMO_TERMINAL=1 — with the
# flag unset, src.api.routes.demo_terminal is never imported and the route does not exist
# (404), rather than existing and refusing. Importing the module also runs its loopback-bind
# fail-fast check, so a non-loopback launch with the flag set fails here, at app construction.
if os.environ.get("D_SYSTEM_DEMO_TERMINAL") == "1":
    from src.api.routes import demo_terminal

    router.include_router(demo_terminal.router, prefix="/demo/terminal")
