from http import HTTPStatus
from pathlib import Path

import fastapi
import starlette.responses

from overhave.api.deps import get_admin_files_dir


async def favicon(files_dir: Path = fastapi.Depends(get_admin_files_dir)) -> starlette.responses.FileResponse:
    icon_path = files_dir / "favicon.ico"
    if icon_path.exists():
        return starlette.responses.FileResponse(icon_path.as_posix())
    raise fastapi.HTTPException(status_code=HTTPStatus.NOT_FOUND)


async def docs() -> starlette.responses.RedirectResponse:
    return starlette.responses.RedirectResponse(url="/docs")
