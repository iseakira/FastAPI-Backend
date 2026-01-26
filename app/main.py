from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()

shipments = {
   12076: {
        "weight":2.0,
        "content":"Books",
        "status": "in transit"
   },
    12077: {
          "weight":5.5,
          "content":"Electronics",
          "status": "delivered"
    },
    12078: {
          "weight":1.2,
          "content":"Clothes",
          "status": "pending"
    },
    12079: {
          "weight":3.0,
          "content":"Toys",
          "status": "in transit"
    }
}

@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = "Scalar_API"
    )