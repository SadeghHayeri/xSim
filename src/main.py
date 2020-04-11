from src.config import config
from src.services.irancell.irancell import Irancell

irancell = Irancell(config['irancell'])

# print(irancell._get_account_info())
# for active_offer in irancell.get_active_offers():
#     print(active_offer)

offers = sorted(irancell.get_offers(), key=lambda o: o.get_unit_price(count_limit_hours=True))
for offer in offers:
    print(offer, offer.volumes[0].value, offer.price, '--->', offer.get_unit_price(count_limit_hours=True))