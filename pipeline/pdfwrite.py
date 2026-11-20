"""Minimal PDF writer (text only) — notes PDFs per unit."""
from pathlib import Path


def _esc(s):
    return (s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
             .replace("\n", " ").replace("\r", ""))


def write_notes_pdf(path: Path, title: str, lines):
    stream_lines = [f"BT /F1 9 Tf 50 750 Td 12 TL ({_esc(title)}) Tj T*"]
    for ln in lines:
        stream_lines.append(f"({_esc(ln)}) Tj T*")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines)
    objs = [
        (1, "<< /Type /Catalog /Pages 2 0 R >>"),
        (2, "<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        (3, "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"),
        (4, f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream"),
        (5, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"),
    ]
    chunks, offsets = [b"%PDF-1.4\n"], {}
    for num, body in objs:
        offsets[num] = sum(len(c) for c in chunks)
        chunks.append(f"{num} 0 obj\n{body}\nendobj\n".encode("latin-1"))
    xref_pos = sum(len(c) for c in chunks)
    n = len(objs) + 1
    xref = f"xref\n0 {n}\n0000000000 65535 f \n" + "".join(
        f"{offsets[num]:010d} 00000 n \n" for num, _ in objs)
    trailer = f"trailer\n<< /Size {n} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(chunks) + xref.encode() + trailer.encode())
