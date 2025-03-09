from fastapi import HTTPException, status

class ItemNotFound(HTTPException):
    def __init__(self, item_id: int):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found")