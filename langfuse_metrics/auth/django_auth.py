from fastapi import Header, HTTPException, Depends
import httpx
import os
from config import DJANGO_AUTH_URL

async def validate_django_token(
    authorization: str = Header(None)
):

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            DJANGO_AUTH_URL,
            headers={"Authorization": authorization},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    return response.json()
