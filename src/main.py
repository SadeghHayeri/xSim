from src.config import config
from src.services.irancell.irancell import Irancell

irancell = Irancell(config['irancell'])

# print(irancell._get_account_info())
for active_offer in irancell.get_active_offers():
    print(active_offer)

irancell.get_offers()