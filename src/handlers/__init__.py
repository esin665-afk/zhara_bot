from src.handlers.menu import register_menu_handlers
from src.handlers.calendar import register_calendar_handlers
from src.handlers.set_builder import register_set_handlers

def register_handlers(dp):
    """Регистрация всех обработчиков."""
    register_menu_handlers(dp)
    register_calendar_handlers(dp)
    register_set_handlers(dp)
