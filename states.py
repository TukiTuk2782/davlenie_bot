from aiogram.fsm.state import StatesGroup, State

class BloodPressure(StatesGroup):
    waiting_for_systolic = State()
    waiting_for_diastolic = State()
    waiting_for_pulse = State()
    waiting_for_confirm = State()