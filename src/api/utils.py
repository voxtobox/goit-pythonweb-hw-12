from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])


# Route to check the health of the application and database connection
@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint to ensure the database is configured and accessible.

    This endpoint checks the connection to the database by executing a simple SQL query
    (SELECT 1). If the database is not accessible or misconfigured, an error is returned.

    Args:
        db (AsyncSession): The database session, injected by FastAPI's Depends function.

    Returns:
        dict: A JSON response with a message indicating the health status of the service.

    Raises:
        HTTPException:
            - If the database is not configured correctly, a 500 status code is raised with an appropriate error message.
            - If there is an error connecting to the database, a 500 status code is raised.
    """
    try:
        # Execute a simple SQL query to check the database connection
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        # If the result is None, raise an HTTP 500 error indicating misconfiguration
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )

        # If the database connection is healthy, return a success message
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        # In case of an error connecting to the database, log the exception and raise an HTTP 500 error
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
