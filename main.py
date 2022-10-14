from aiogram import executor
from create_bot import dp
from bd import bd_start
from handlers.admin import reg_admin
from handlers.hello import reg_hello_handlers
from handlers.user import reg_user
from handlers.schudle import reg_schedule
from handlers.counter import reg_count
from handlers.game import reg_game

reg_admin(dp)
reg_hello_handlers(dp)
reg_user(dp)
reg_schedule(dp)
reg_game(dp)
reg_count(dp)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=bd_start())
