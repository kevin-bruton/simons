from datetime import datetime
from typing import Dict, List
from framework.types import Bar, Trade, Position, Order
from framework.symbols import Symbol

class Trader:
  def __init__(self, init_balance):
    self.init_balance = init_balance
    self.__cash = init_balance
    self.__positions = []
    self.__orders = []
    self.__trades: List[Trade] = []
    self.__last_order_id = 0
    self.__symbols: Dict[str, Symbol] = {}
  
  @staticmethod
  def _hit_limit(direction, limit_level, bar: Bar):
    if direction.upper() == 'LONG' and limit_level and bar['low'] <= limit_level:
      return True
    elif direction.upper() == 'SHORT' and limit_level and bar['high'] >= limit_level:
      return True
    return False
  
  @staticmethod
  def _hit_stop(direction, stop_level, bar: Bar):
    if direction.upper() == 'LONG' and stop_level and bar['high'] >= stop_level:
      return True
    elif direction.upper() == 'SHORT' and stop_level and bar['low'] <= stop_level:
      return True
    return False

  @staticmethod
  def _hit_stop_loss(direction, stop_loss, bar: Bar):
    if direction.upper() == 'LONG' and stop_loss and bar['low'] <= stop_loss:
      return True
    elif direction.upper() == 'SHORT' and stop_loss and bar['high'] >= stop_loss:
      return True
    return False

  @staticmethod
  def _hit_take_profit(direction, take_profit, bar: Bar):
    if direction.upper() == 'LONG' and take_profit and bar['high'] >= take_profit:
      return True
    elif direction.upper() == 'SHORT' and take_profit and bar['low'] <= take_profit:
      return True
    return False

  def create_order(self, symbol, direction, quantity, created_dt, limit=None, stop=None, sl=None, tp=None):
    self.__last_order_id += 1
    order = Order(
      id=self.__last_order_id,
      symbol=symbol,
      direction=direction.upper(),
      quantity=quantity,
      created_dt=created_dt,
      limit=limit,
      stop=stop,
      sl=sl,
      tp=tp
    )
    self.__orders.append(order)
    #print(f'Created {direction} order for {symbol}. limit: {limit}; stop: {stop}')
    return self.__last_order_id

  def cancel_order(self, order_id) -> bool:
    order = self.get_order(order_id)
    try:
      self.__orders.remove(order)
      return True
    except:
      return False
  
  def cancel_all_orders(self):
    self.__orders = []

  def get_orders(self):
    return self.__orders

  def get_trades(self):
    return self.__trades

  def __open_position(self, id, symbol, direction, quantity, entry_dt, entry_price, description=None, sl=None, tp=None):
    position = Position(id=id, symbol=symbol, direction=direction, quantity=quantity, entry_dt=entry_dt, entry_price=entry_price, description=description, sl=sl, tp=tp)
    self.__positions.append(position)
    self.__cash -= quantity * entry_price
    print(f'Opened position. {entry_dt} Bought {quantity:.2f} {symbol} @ {entry_price} SL: {sl} TP: {tp}')
  
  def close_position(self, pos_id, close_date, close_price, description=None):
    position = self.get_position(pos_id)
    if position and position.opened_dt != close_date:
      position.current_price = close_price
      base_profit = (close_price - position.entry) if position.direction == 'LONG' else (position.entry - close_price)
      trade = Trade(
        symbol=position.symbol,
        direction=position.direction,
        quantity=position.quantity,
        entry_dt=position.opened_dt,
        exit_dt=close_date,
        entry_price=position.entry,
        exit_price=close_price,
        orig_sl=position.orig_sl,
        description=description,
        profit=base_profit * position.quantity,
        #  'achieved_r': base_profit / (position.entry - position.orig_sl) if position.entry and position.orig_sl else None
      )
      self.__trades.append(trade)
      self.__cash += (close_price * position.quantity)
      print(f'Closed position. {close_date} Sold {position.quantity:.2f} {position.symbol} @ {close_price} Profit: {trade["profit"]:.2f} {description}')
      self.__positions.remove(position)
      return True
    else:
      return False

  def __check_orders(self, orders_to_check: list[Order], bar: Bar):
    is_market_order = lambda limit, stop: (limit == None and stop == None)
    order_ids_to_remove = []
    for order in orders_to_check:
      if Trader._hit_stop(order.direction, order.stop, bar) \
        or Trader._hit_limit(order.direction, order.limit, bar) \
        or is_market_order(order.limit, order.stop):
          cost = order.quantity * bar['close']
          if self.__cash >= cost:
            self.__open_position(order.getId(), order.symbol, order.direction, order.quantity, entry_dt=bar.dt, entry_price=bar.close, sl=order.sl, tp=order.tp)
            order_ids_to_remove.append(order.getId())
    for id in order_ids_to_remove:
      self.cancel_order(id)

  def __check_positions(self, positions_to_check, bar: Bar):
    for position in positions_to_check:
      if Trader._hit_stop_loss(position.direction, position.sl, bar):
        self.close_position(position.id, bar.dt, position.sl, description='Hit SL')
      elif Trader._hit_take_profit(position.direction, position.tp, bar):
        self.close_positon(position.id, bar.dt, position.tp, description='Hit TP')

  def check_orders_and_positions(self, symbol: str, bar: Bar):
    # get orders with said symbol and update them
    orders = self.get_orders_with_symbol(symbol)
    self.__check_orders(orders, bar)
    positions = self.get_positions_with_symbol(symbol)
    self.__check_positions(positions, bar)

  def get_account_value(self) -> float:
    return self.__cash + self.get_postions_value()

  def get_cash_balance(self) -> float:
    return self.__cash
    
  def get_position(self, pos_id):
    try:
      return next(pos for pos in self.__positions if pos.id == pos_id)
    except:
      return None
  
  def get_positions(self):
    return self.__positions

  def get_num_positions(self):
    return len(self.__positions)

  def get_positions_value(self):
    for pos in self.__positions:
      symbol = pos.symbol_name

    return sum([pos.getValue() for pos in self.__positions])

  def get_order(self, order_id):
    try:
      return next(order for order in self.__orders if order.getId() == order_id)
    except:
      return None

  def get_num_orders(self):
    return len(self.__orders)

  def get_orders_with_symbol(self, symbol):
    return [order for order in self.__orders if order.symbol == symbol]

  def get_positions_with_symbol(self, symbol):
    return [pos for pos in self.__positions if pos.symbol == symbol]
  