from config import bot
from handlers import cart, catalog, admin, user, contacts


def register_handlers():
    cart.register_cart_handlers()
    catalog.register_catalog_handlers()
    user.register_user_handlers()
    contacts.register_contacts_handlers()
    admin.register_admin_handlers()


register_handlers()

bot.polling(none_stop=True)
