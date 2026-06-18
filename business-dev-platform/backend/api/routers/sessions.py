import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.core.config import SESSIONS_DIR
from backend.models.session import BusinessPlanSession, BusinessProfile, WizardStep

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("")
async def create_session() -> dict:
    """
    Create a new business plan session.

    Returns:
        Dict with session_id and initial session data
    """
    try:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        session = BusinessPlanSession(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            current_step=WizardStep.DOMAIN_SELECTION,
            completed_steps=[],
            profile=BusinessProfile(),
        )

        # Save to file
        session_file = SESSIONS_DIR / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session.model_dump(mode='json'), f, default=str)

        return {
            "session_id": session_id,
            "created_at": now.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/{session_id}")
async def get_session(session_id: str) -> dict:
    """
    Retrieve a business plan session.

    Args:
        session_id: Session UUID

    Returns:
        Full BusinessPlanSession data
    """
    try:
        session_file = SESSIONS_DIR / f"{session_id}.json"

        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        with open(session_file, 'r') as f:
            data = json.load(f)

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")


@router.patch("/{session_id}")
async def update_session(session_id: str, updates: dict) -> dict:
    """
    Update a session's data.

    Args:
        session_id: Session UUID
        updates: Dict with fields to update (profile, current_step, etc.)

    Returns:
        Updated session data
    """
    try:
        session_file = SESSIONS_DIR / f"{session_id}.json"

        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        with open(session_file, 'r') as f:
            session_data = json.load(f)

        # Update allowed fields
        if "profile" in updates:
            session_data["profile"].update(updates["profile"])

        if "current_step" in updates:
            session_data["current_step"] = updates["current_step"]
            if updates["current_step"] not in session_data.get("completed_steps", []):
                completed = session_data.get("completed_steps", [])
                # Add previous step to completed if not already there
                if session_data.get("current_step"):
                    completed.append(session_data.get("current_step"))
                session_data["completed_steps"] = list(set(completed))

        if "market_analysis" in updates:
            session_data["market_analysis"] = updates["market_analysis"]

        if "financial_projection" in updates:
            session_data["financial_projection"] = updates["financial_projection"]

        if "risk_matrix" in updates:
            session_data["risk_matrix"] = updates["risk_matrix"]

        session_data["updated_at"] = datetime.utcnow().isoformat()

        with open(session_file, 'w') as f:
            json.dump(session_data, f, default=str)

        return session_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> dict:
    """
    Delete a session.

    Args:
        session_id: Session UUID

    Returns:
        Confirmation message
    """
    try:
        session_file = SESSIONS_DIR / f"{session_id}.json"

        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        session_file.unlink()

        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
