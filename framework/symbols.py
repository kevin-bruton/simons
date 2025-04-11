
class Symbol:
  def __init__(self, id, type):
    self.id = id
    self.type = type
    self.current_price = None
  
  def get_dollar_value(self):
    # This is a placeholder function. In a real implementation, this would return the dollar value of the symbol.
    return 1.0
  
class EsFutures(Symbol):
  def __init__(self):
    super().__init__('ES', 'Futures')
    self.big_point_value = 50.0
  
  def get_dollar_value(self, price, quantity=1):
    return self.big_point_value * price * quantity
  
  def get_position_value(self, entry_price, current_price, quantity=1):
    return (current_price - entry_price) * self.big_point_value * quantity