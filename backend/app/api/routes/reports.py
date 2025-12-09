from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.services.report_service import generate_target_report 
from backend.app.services.pdf_service import generate_pdf_report

router = APIRouter()

@router.get("/{target_id}")
def download_report(
    target_id: int, 
    format: str = Query("html", regex="^(html|pdf)$"), # Allow ?format=pdf
    db: Session = Depends(get_db)
):
    # PDF Logic
    if format == "pdf":
        pdf_file = generate_pdf_report(db, target_id)
        if not pdf_file:
            raise HTTPException(status_code=404, detail="Target not found or PDF error")
        
        # Return as a downloadable file
        return StreamingResponse(
            pdf_file, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=sentry_report_{target_id}.pdf"}
        )

    # Existing HTML Logic
    report_html = generate_target_report(db, target_id)
    if not report_html:
        raise HTTPException(status_code=404, detail="Target not found")
    return HTMLResponse(content=report_html)