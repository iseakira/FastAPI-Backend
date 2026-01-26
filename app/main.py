from fastapi import FastAPI

app = FastAPI()

shipment = {
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

