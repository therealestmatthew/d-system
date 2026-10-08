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
#
# The workbench read routes (ADR-015) share the same one gate, one binding: mounted only under
# this same flag, and src.api.routes.workbench re-runs the same loopback-bind check on import.
if os.environ.get("D_SYSTEM_DEMO_TERMINAL") == "1":
    from src.api.routes import demo_terminal

    router.include_router(demo_terminal.router, prefix="/demo/terminal")

    # The terminal interaction API (ADR-030) needs a second flag on top of the first. With
    # D_SYSTEM_TERMINAL_API unset, src.api.routes.demo_terminal_api is never imported: its three
    # routes do not exist (404), no bearer token is generated or written, and the websocket route
    # keeps no output record. Importing it writes the token file and turns output capture on in
    # demo_terminal, and a failure to write the token stops the application from starting.
    if os.environ.get("D_SYSTEM_TERMINAL_API") == "1":
        from src.api.routes import demo_terminal_api

        router.include_router(demo_terminal_api.router, prefix="/demo/terminal")

    from src.api.routes import workbench

    router.include_router(workbench.router, prefix="/workbench")

    # The bookmark-category routes (ADR-029) are the workbench's first write routes, mounted under
    # the same flag and loopback binding. Registered after `workbench` so its routes win any
    # overlapping path; `/bookmarks` does not overlap any of them.
    from src.api.routes import workbench_bookmarks

    router.include_router(workbench_bookmarks.router, prefix="/workbench/bookmarks")
