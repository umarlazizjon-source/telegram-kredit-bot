import io
import pandas as pd
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

API_TOKEN = "8514511171:AAEdwehoBo7ywvECZofJYeHiOzLw_UCXKXQ"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class KreditForm(StatesGroup):
    summa = State()
    foiz = State()
    oy = State()
    turi = State()

def annuitet(summa, foiz, oy):
    r = foiz / 12 / 100
    if r == 0:
        return summa / oy
    return summa * (r * (1 + r)**oy) / ((1 + r)**oy - 1)

def oddiy(summa, foiz, oy):
    total_foiz = summa * foiz / 100 * (oy / 12)
    return (summa + total_foiz) / oy

def jadval(summa, foiz, oy, turi):
    rows = []
    if turi == "annuitet":
        payment = annuitet(summa, foiz, oy)
        r = foiz / 12 / 100
        qolgan = summa
        for i in range(1, oy+1):
            interest = qolgan * r
            main = payment - interest
            qolgan -= main
            rows.append([i, round(payment,2), round(main,2), round(interest,2), round(qolgan,2)])
    else:
        total_foiz = summa * foiz / 100 * (oy/12)
        payment = (summa + total_foiz)/oy
        main_payment = summa/oy
        interest_payment = total_foiz/oy
        for i in range(1, oy+1):
            remaining = summa - main_payment*i
            rows.append([i, round(payment,2), round(main_payment,2), round(interest_payment,2), round(remaining,2)])
    return pd.DataFrame(rows, columns=["Oy","To'lov","Asosiy","Foiz","Qoldiq"])

def grafik(df):
    fig, ax = plt.subplots()
    ax.plot(df["Oy"], df["Qoldiq"], marker="o")
    ax.set_xlabel("Oy")
    ax.set_ylabel("Qoldiq")
    ax.set_title("Qarz kamayishi grafigi")
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)
    return img

# Start
@dp.message(Command("start"))
async def start_handler(msg: types.Message, state: FSMContext):
    await msg.answer("Salom! 👋 Men sizga kredit hisoblashda yordam beraman.\n1️⃣ Qarz miqdorini kiriting (misol: 10000000)")
    await state.set_state(KreditForm.summa)

# ... (shu kabi qolgan xabarlar va hisoblash funksiyalari)
# Bot ishga tushurish
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
