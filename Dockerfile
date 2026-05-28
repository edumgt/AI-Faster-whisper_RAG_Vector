# Reuse local image that already has sentence-transformers, torch, fastapi,
# uvicorn, pydantic, numpy, requests, python-dotenv (~9 GB of deps).
# Only chromadb and a few small packages need to be added.
FROM education-counsel-webapp:latest

LABEL maintainer="edumgt"
LABEL description="Counseling Multimodal RAG API"

WORKDIR /app

# Packages already in base: sentence-transformers, torch, fastapi, uvicorn,
#   pydantic, python-dotenv, numpy, requests
# Only install what is missing:
RUN pip install --no-cache-dir \
        "chromadb>=0.5.5" \
        "python-multipart>=0.0.9" \
        "typer>=0.12.3" \
        "rich>=13.7.1" \
        "reportlab>=4.2.0"

COPY requirements.txt .
# pip will skip already-satisfied constraints from the base image.
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY src/ ./src/
COPY samples/ ./samples/

RUN mkdir -p runtime

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
