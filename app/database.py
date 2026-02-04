import sqlite3
from .schemas import ShipmentRead, ShipmentCreate, ShipmentUpdate


class Database:
  def __init__(self):
    self.conn = sqlite3.connect("sqlite.db",check_same_thread=False)
    self.cur = self.conn.cursor()

    self.create_table()

  def create_table(self):
      self.cur.execute("""
              CREATE TABLE IF NOT EXISTS shipment (
               id INTEGER PRIMARY KEY ,
               content TEXT,
               weight REAL,
               status TEXT
               )
               """)
  def create(self, shipment:ShipmentCreate)->int:
     self.cur.execute("""
        SELECT MAX(id) FROM shipment""")
     result = self.cur.fetchone()
     new_id = (result[0] or 0) + 1

     self.cur.execute("""
     INSERT INTO shipment
     VALUES (:id, :content, :weight, :status)
     """,{
     "id":new_id,
     **shipment.model_dump(),
     "status":"placed"
     })
     self.conn.commit()
     return new_id

  def get(self,id:int)->ShipmentRead|None:
    self.cur.execute("""
    SELECT * FROM shipment
    WHERE id = ?
""",(id,))
    row = self.cur.fetchone()
    if row is None:
       return None
    return {
       "id":row[0],
        "content":row[1],
        "weight":row[2],
        "status":row[3]
    }

  def update(self, id:int,shipment:ShipmentUpdate):
    self.cur.execute("""
    UPDATE shipment
    SET status = :status
    WHERE id = :id
  """,{
    "id":id,
    **shipment.model_dump()})
    self.conn.commit()
    return self.get(id)

  def delete(self,id:int):
    self.cur.execute("""
      DELETE FROM shipment
      WHERE id = ?
    """
    ,(id,))
    self.conn.commit()

  def close(self):
    self.conn.close()




