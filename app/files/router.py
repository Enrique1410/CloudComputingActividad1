from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Body
from pypdf import PdfMerger
from pydantic import BaseModel
import uuid
import aiohttp
import requests

router = APIRouter()

files = {}


class CarlemanyFile(BaseModel):
    filename: str
    author: str
    amount_of_pages: int
    path: str


authentication_url = "0.0.0.0"


async def introspect(auth: str):
    headers = {"accept": "application/json", "auth": auth}
    url = "http://" + authentication_url + ":80/introspect"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, ssl=False) as response:
            status_code = response.status
            if status_code != 200:
                return None
            body = await response.text()
            return body


@router.get("/list_files")
async def list_files(auth: str = Header()) -> dict[str, list[CarlemanyFile] | str]:

    response = await introspect(auth=auth)
    if response is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    import json

    user_info = json.loads(response)
    username = user_info["username"]

    user_files = [
        file_data for file_data in files.values() if file_data.author == username
    ]

    return {"status": "ok", "files": user_files}


class FileCreateInput(BaseModel):
    filename: str
    amount_of_pages: int


@router.post("/create_file")
async def create_file(
    auth: str = Header(), file_info: FileCreateInput = Body()
) -> dict[str, str]:

    response = await introspect(auth=auth)
    if response is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    import json

    user_info = json.loads(response)
    username = user_info["username"]

    file_id = str(uuid.uuid4())
    prefix = "files/"
    filename = (
        file_info.filename
        if file_info.filename.endswith(".pdf")
        else file_info.filename + ".pdf"
    )
    filepath = prefix + filename

    file_data = CarlemanyFile(
        filename=filename,
        author=username,
        amount_of_pages=file_info.amount_of_pages,
        path=filepath,
    )
    files[file_id] = file_data

    return {"status": "ok", "file_id": file_id}


@router.get("/get_file/{id}")
async def get_file(
    id: str, auth: str = Header()
) -> dict[str, CarlemanyFile | str | bytes]:

    response = await introspect(auth=auth)
    if response is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    if id not in files:
        raise HTTPException(status_code=404, detail="File not found")

    import json

    user_info = json.loads(response)
    username = user_info["username"]

    if files[id].author != username:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this file"
        )

    file_data = files[id]

    content = None
    import os

    if os.path.exists(file_data.path):
        with open(file_data.path, "rb") as f:
            content = f.read()

    response = {
        "status": "ok",
        "file_info": file_data,
    }
    if content is not None:
        response["content"] = content.hex()

    return response


@router.post("/update_file/{id}")
async def update_file(
    id: str, auth: str = Header(), input_file: UploadFile = File()
) -> dict[str, str]:

    response = await introspect(auth=auth)
    if response is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    if id not in files:
        raise HTTPException(status_code=404, detail="File not found")

    import json

    user_info = json.loads(response)
    username = user_info["username"]

    if files[id].author != username:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this file"
        )

    filepath = files[id].path
    with open(filepath, "wb") as buffer:
        while chunk := await input_file.read(8192):
            buffer.write(chunk)

    from pypdf import PdfReader

    pdf = PdfReader(filepath)
    actual_pages = len(pdf.pages)
    if actual_pages != files[id].amount_of_pages:
        import os

        os.remove(filepath)
        raise HTTPException(
            status_code=400,
            detail=f"Page count mismatch: expected {files[id].amount_of_pages}, got {actual_pages}",
        )

    return {"status": "ok"}


@router.delete("/delete_file/{id}")
async def delete_file(id: str, auth: str = Header()) -> dict[str, str]:

    response = await introspect(auth=auth)
    if response is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    if id not in files:
        raise HTTPException(status_code=404, detail="File not found")

    import json

    user_info = json.loads(response)
    username = user_info["username"]

    if files[id].author != username:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this file"
        )

    import os

    file_path = files[id].path
    if os.path.exists(file_path):
        os.remove(file_path)

    del files[id]

    return {"status": "ok"}


class MergeInput(BaseModel):
    file_id1: str
    file_id2: str


@router.post("/merge_files")
async def merge_files(
    file_id1: str = Header(), file_id2: str = Header(), auth: str = Header()
) -> dict[str, str]:
    response = await introspect(auth=auth)
    if response is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    import json

    user_info = json.loads(response)
    username = user_info["username"]

    if file_id1 not in files:
        raise HTTPException(status_code=404, detail=f"File {file_id1} not found")
    if file_id2 not in files:
        raise HTTPException(status_code=404, detail=f"File {file_id2} not found")

    if files[file_id1].author != username:
        raise HTTPException(status_code=403, detail="Not authorized to merge file 1")
    if files[file_id2].author != username:
        raise HTTPException(status_code=403, detail="Not authorized to merge file 2")

    import os

    file1_path = files[file_id1].path
    file2_path = files[file_id2].path
    if not os.path.exists(file1_path):
        raise HTTPException(status_code=400, detail=f"File {file_id1} has no content")
    if not os.path.exists(file2_path):
        raise HTTPException(status_code=400, detail=f"File {file_id2} has no content")

    file_id = str(uuid.uuid4())
    prefix = "files/"
    merged_filename = f"merged_{file_id}.pdf"
    merged_path = prefix + merged_filename

    merger = PdfMerger()
    merger.append(file1_path)
    merger.append(file2_path)
    merger.write(merged_path)
    merger.close()

    from pypdf import PdfReader

    pdf = PdfReader(merged_path)
    page_count = len(pdf.pages)

    merged_file = CarlemanyFile(
        filename=merged_filename,
        author=username,
        amount_of_pages=page_count,
        path=merged_path,
    )
    files[file_id] = merged_file

    return {"status": "ok", "file_id": file_id}
