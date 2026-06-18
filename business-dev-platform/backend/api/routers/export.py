import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from backend.core.config import SESSIONS_DIR
from backend.services.plan_service import assemble_plan
from backend.reports.markdown_generator import render_markdown
from backend.reports.html_generator import render_html_report

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/plan/{session_id}/markdown")
async def export_plan_markdown(session_id: str):
    """
    Export business plan as Markdown file.

    Returns:
        Markdown file download (content-disposition: attachment)
    """
    try:
        # Verify session exists
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        # Assemble plan
        plan = assemble_plan(session_id)
        if not plan:
            raise HTTPException(status_code=500, detail="Failed to assemble plan")

        # Generate markdown
        markdown_content = render_markdown(plan)

        # Return as downloadable file
        business_name = plan.get("metadata", {}).get("business_name", "Geschaeftsplan")
        filename = f"{business_name.replace(' ', '_')}_plan.md"

        return FileResponse(
            content=markdown_content.encode("utf-8"),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting markdown: {str(e)}")


@router.get("/plan/{session_id}/html", response_class=HTMLResponse)
async def export_plan_html(session_id: str):
    """
    Export business plan as HTML page.

    Returns:
        HTML document suitable for viewing and printing to PDF
    """
    try:
        # Verify session exists
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        # Assemble plan
        plan = assemble_plan(session_id)
        if not plan:
            raise HTTPException(status_code=500, detail="Failed to assemble plan")

        # Generate HTML
        html_content = render_html_report(plan)

        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting HTML: {str(e)}")


@router.get("/{session_id}/summary")
async def get_export_summary(session_id: str):
    """
    Get summary of what can be exported for a session.

    Returns:
        Dict with export options and plan metadata
    """
    try:
        # Verify session exists
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        # Assemble plan
        plan = assemble_plan(session_id)
        if not plan:
            raise HTTPException(status_code=500, detail="Failed to assemble plan")

        return {
            "session_id": session_id,
            "business_name": plan.get("metadata", {}).get("business_name", ""),
            "domain": plan.get("metadata", {}).get("domain", ""),
            "city": plan.get("metadata", {}).get("city", ""),
            "legal_form": plan.get("metadata", {}).get("legal_form", ""),
            "generated_at": plan.get("generated_at", ""),
            "export_options": [
                {
                    "format": "markdown",
                    "description": "Download as Markdown (.md) file",
                    "url": f"/export/plan/{session_id}/markdown",
                },
                {
                    "format": "html",
                    "description": "View as HTML (printable to PDF)",
                    "url": f"/export/plan/{session_id}/html",
                },
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting export summary: {str(e)}")
