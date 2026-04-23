import re
import PyPDF2

def load_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def clean_text(text):
    text = re.sub(r'Table of Contents.*?Chapter 1: Introduction', 'Chapter 1: Introduction', text, flags=re.DOTALL)
    text = re.sub(r'CALTECH LASER SAFETY MANUAL.?2026 Page \d+ of \d+', ' ', text)
    text = re.sub(r'\[THIS PAGE INTENTIONALLY LEFT BLANK\]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_text(text):
    text = clean_text(text)

    # Split by chapter headings
    parts = re.split(r'(Chapter\s+\d+:\s+[A-Za-z ,\-&]+)', text, flags=re.IGNORECASE)

    chunks = []
    current_heading = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if re.match(r'Chapter\s+\d+:\s+[A-Za-z ,\-&]+', part, flags=re.IGNORECASE):
            current_heading = part
        else:
            chunk = f"{current_heading} {part}".strip()
            if chunk:
                chunks.append(chunk)

    return chunks

def get_top_chunks(chunks, query, top_k=3):
    query_lower = query.lower()
    query_words = query_lower.split()
    scored_chunks = []

    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = 0

        # exact phrase bonus
        if query_lower in chunk_lower:
            score += 20

        # word match bonus
        for word in query_words:
            if word in chunk_lower:
                score += 3

        # special meaning boosts
        if "hazard" in query_lower:
            if "hazard" in chunk_lower or "hazards" in chunk_lower:
                score += 12
        if "eye" in query_lower:
            if "eye" in chunk_lower or "retina" in chunk_lower or "cornea" in chunk_lower:
                score += 12
        if "skin" in query_lower:
            if "skin" in chunk_lower or "burn" in chunk_lower:
                score += 10
        if "fire" in query_lower and "fire" in chunk_lower:
            score += 10
        if "electrical" in query_lower and "electrical" in chunk_lower:
            score += 10

        # chapter boosts
        if "laser hazards" in query_lower or "laser hazard" in query_lower:
            if "chapter 4: laser radiation hazards" in chunk_lower:
                score += 30
            if "chapter 6: non-beam hazards" in chunk_lower:
                score += 15

        if "eye damage" in query_lower or "eye injury" in query_lower:
            if "the eye" in chunk_lower or "retina" in chunk_lower:
                score += 30

        # penalties
        if "roles and responsibilities" in chunk_lower:
            score -= 20
        if "principal investigator" in chunk_lower:
            score -= 20
        if "laboratory laser safety officer" in chunk_lower:
            score -= 20
        if "table of contents" in chunk_lower:
            score -= 50

        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]