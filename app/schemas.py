from pydantic import BaseModel

class ProductOut(BaseModel):

    id : int
    name : str
    category : str
    base_price : float
    tage : str

class RecommendRequest(BaseModel):
    product_id: int
    top_n: int = 4