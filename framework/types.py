from datetime import datetime

class Order:
  id: str
  symbol_id: str
  direction: str
  quantity: float
  created_dt: datetime
  limit: float
  stop: float
  sl: float
  tp: float
  description: str

class Position:
  id: str
  symbol_id: str
  direction: str
  quantity: float
  entry_dt: datetime
  entry_price: float
  sl: float
  orig_sl: float
  tp: float
  desc: float

  
class Bar:
  dt: datetime
  open: float
  high: float
  low: float
  close: float
  volume: float

class Trade:
  id: str
  symbol_id: str
  direction: str
  quantity: float
  entry_dt: datetime
  exit_dt: datetime
  entry_price: float
  exit_price: float
  orig_sl: float
  description: str
