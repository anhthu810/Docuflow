import os
import shutil
import io
import csv
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from backend.database import get_db, BASE_DIR
from backend.models import Document, User
from backend.schemas import DocumentOut, DocumentUpdate
from backend.auth import get_current_user_optional
from backend.ai_service import extract_invoice_data

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DEFAULT_DEMO_DOCS = [
    {
        "file_name": "Invoice_084.pdf",
        "format": "PDF • 1 trang",
        "supplier": "Northline Studio",
        "tax_id": "0318992145",
        "invoice_no": "INV-2026-084",
        "date": "28/10/2026",
        "subtotal": 42500000.0,
        "tax": 4250000.0,
        "total": 46750000.0,
        "has_low_confidence": True,
        "audit_done": False
    },
    {
        "file_name": "Invoice_085.jpg",
        "format": "JPG • Ảnh chụp",
        "supplier": "Atlas Office Supply",
        "tax_id": "0109923841",
        "invoice_no": "INV-2026-085",
        "date": "29/10/2026",
        "subtotal": 19600000.0,
        "tax": 1960000.0,
        "total": 21560000.0,
        "has_low_confidence": False,
        "audit_done": True
    },
    {
        "file_name": "Invoice_086.pdf",
        "format": "PDF • 1 trang",
        "supplier": "Meridian Supply Co.",
        "tax_id": "0308821990",
        "invoice_no": "INV-2026-086",
        "date": "29/10/2026",
        "subtotal": 28000000.0,
        "tax": 2800000.0,
        "total": 30800000.0,
        "has_low_confidence": False,
        "audit_done": True
    },
    {
        "file_name": "Invoice_087.png",
        "format": "PNG • Ảnh scan",
        "supplier": "Harbor Logistics",
        "tax_id": "0200881920",
        "invoice_no": "INV-2026-087",
        "date": "30/10/2026",
        "subtotal": 9850000.0,
        "tax": 985000.0,
        "total": 10835000.0,
        "has_low_confidence": False,
        "audit_done": True
    }
]

def seed_default_documents(db: Session, user_id: Optional[int] = None):
    """Seed initial sample invoices if table is empty"""
    created_list = []
    for item in DEFAULT_DEMO_DOCS:
        doc = Document(
            user_id=user_id,
            file_name=item["file_name"],
            format=item["format"],
            supplier=item["supplier"],
            tax_id=item["tax_id"],
            invoice_no=item["invoice_no"],
            date=item["date"],
            subtotal=item["subtotal"],
            tax=item["tax"],
            total=item["total"],
            has_low_confidence=item["has_low_confidence"],
            audit_done=item["audit_done"]
        )
        db.add(doc)
        created_list.append(doc)
    db.commit()
    return created_list

@router.get("", response_model=List[DocumentOut])
def get_documents(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Document)
    if user:
        docs = query.filter(Document.user_id == user.id).all()
        if not docs:
            docs = seed_default_documents(db, user_id=user.id)
    else:
        docs = query.filter(Document.user_id == None).all()
        if not docs:
            docs = seed_default_documents(db, user_id=None)
    return docs

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    if not files:
        raise HTTPException(status_code=400, detail="Không có tệp nào được tải lên.")

    created_docs = []
    for file in files:
        # Save file to uploads folder
        safe_filename = f"{int(file.filename.split('.')[0] if '.' in file.filename else 'file')}_{os.urandom(4).hex()}_{file.filename}" if len(file.filename) < 10 else f"{os.urandom(4).hex()}_{file.filename}"
        saved_path = os.path.join(UPLOAD_DIR, safe_filename)
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract data with AI or fallback
        extracted = extract_invoice_data(saved_path, file.filename)

        new_doc = Document(
            user_id=user.id if user else None,
            file_name=file.filename,
            file_path=f"/uploads/{safe_filename}",
            format=extracted.get("format", "Tài liệu"),
            supplier=extracted.get("supplier", "CÔNG TY ĐỐI TÁC"),
            tax_id=extracted.get("tax_id", ""),
            invoice_no=extracted.get("invoice_no", ""),
            date=extracted.get("date", ""),
            subtotal=extracted.get("subtotal", 0.0),
            tax=extracted.get("tax", 0.0),
            total=extracted.get("total", 0.0),
            has_low_confidence=extracted.get("has_low_confidence", False),
            audit_done=extracted.get("audit_done", True),
            raw_extracted_json=str(extracted)
        )
        db.add(new_doc)
        created_docs.append(new_doc)

    # Deduct credits
    if user and user.credits > 0:
        user.credits = max(0, user.credits - len(files))

    db.commit()
    for d in created_docs:
        db.refresh(d)

    return {
        "success": True,
        "message": f"Đã bóc tách thành công {len(created_docs)} hóa đơn!",
        "documents": [DocumentOut.model_validate(d) for d in created_docs],
        "credits": user.credits if user else 20
    }

@router.put("/{doc_id}", response_model=DocumentOut)
def update_document(
    doc_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu này.")

    if payload.supplier is not None:
        doc.supplier = payload.supplier
    if payload.tax_id is not None:
        doc.tax_id = payload.tax_id
    if payload.invoice_no is not None:
        doc.invoice_no = payload.invoice_no
    if payload.date is not None:
        doc.date = payload.date
    if payload.subtotal is not None:
        doc.subtotal = payload.subtotal
    if payload.tax is not None:
        doc.tax = payload.tax
    if payload.total is not None:
        doc.total = payload.total
    elif payload.subtotal is not None or payload.tax is not None:
        doc.total = doc.subtotal + doc.tax
    if payload.audit_done is not None:
        doc.audit_done = payload.audit_done
    if payload.has_low_confidence is not None:
        doc.has_low_confidence = payload.has_low_confidence

    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu cần xóa.")
    
    db.delete(doc)
    db.commit()
    return {"success": True, "message": "Đã xóa tài liệu thành công."}

@router.post("/reset-session")
def reset_session(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """Resets documents to default initial demo dataset"""
    if user:
        db.query(Document).filter(Document.user_id == user.id).delete()
    else:
        db.query(Document).filter(Document.user_id == None).delete()
    db.commit()

    docs = seed_default_documents(db, user_id=user.id if user else None)
    return {
        "success": True,
        "message": "Đã khởi tạo lại phiên làm việc mẫu.",
        "documents": [DocumentOut.model_validate(d) for d in docs]
    }

@router.get("/export/excel")
def export_excel(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Document)
    docs = query.filter(Document.user_id == (user.id if user else None)).all()
    if not docs:
        docs = query.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách hóa đơn"

    # Styling
    header_fill = PatternFill(start_color="2F5BFF", end_color="2F5BFF", fill_type="solid")
    header_font = Font(name="Be Vietnam Pro", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Be Vietnam Pro", size=10)
    num_font = Font(name="JetBrains Mono", size=10)
    thin_border = Border(
        left=Side(style='thin', color='D0D5DD'),
        right=Side(style='thin', color='D0D5DD'),
        top=Side(style='thin', color='D0D5DD'),
        bottom=Side(style='thin', color='D0D5DD')
    )

    headers = [
        "STT", "Tên tệp", "Nhà cung cấp", "Mã số thuế", 
        "Số hóa đơn", "Ngày lập", "Tiền hàng (VND)", "Tiền thuế VAT (VND)", 
        "Tổng thanh toán (VND)", "Trạng thái rà soát"
    ]
    ws.append(headers)

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[1].height = 28

    for idx, d in enumerate(docs, 1):
        status_label = "Đã xác nhận" if d.audit_done else "Cần rà soát"
        row_data = [
            idx,
            d.file_name,
            d.supplier,
            str(d.tax_id),
            str(d.invoice_no),
            d.date,
            d.subtotal,
            d.tax,
            d.total,
            status_label
        ]
        ws.append(row_data)
        row_idx = idx + 1
        ws.row_dimensions[row_idx].height = 22

        for col_idx in range(1, len(row_data) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = thin_border
            if col_idx in [7, 8, 9]:
                cell.font = num_font
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx in [1, 4, 5, 6, 10]:
                cell.font = num_font if col_idx in [4, 5, 6] else data_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.font = data_font
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Auto-adjust column width
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=DocuFlow_Bao_Cao_Hoa_Don.xlsx"}
    )

@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Document)
    docs = query.filter(Document.user_id == (user.id if user else None)).all()
    if not docs:
        docs = query.all()

    output = io.StringIO()
    # Write UTF-8 BOM so Excel opens Vietnamese characters cleanly
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow([
        "STT", "Nhà cung cấp", "Mã số thuế", "Số hóa đơn", 
        "Ngày lập", "Tiền hàng", "Tiền thuế", "Tổng thanh toán", "Trạng thái rà soát"
    ])

    for idx, d in enumerate(docs, 1):
        status_label = "Đã rà soát" if d.audit_done else "Cần rà soát"
        writer.writerow([
            idx,
            d.supplier,
            f'="{d.tax_id}"',
            f'="{d.invoice_no}"',
            d.date,
            int(d.subtotal),
            int(d.tax),
            int(d.total),
            status_label
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=DocuFlow_Bao_Cao_Hoa_Don.csv"}
    )

