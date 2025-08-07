from fastapi import APIRouter
from . import notes, ai, exports, sync

router = APIRouter()

router.include_router(notes.router, prefix="/notes", tags=["notes"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
router.include_router(exports.router, prefix="/exports", tags=["exports"])
router.include_router(sync.router, prefix="/sync", tags=["sync"])