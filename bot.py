from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import io

API_TOKEN = "8514511171:AAEdwehoBo7ywvECZofJYeHiOzLw_UCXKXQ"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# States
class KreditForm(StatesGroup):
    summa = State()
    foiz = State()
    oy = State()
    turi = State()

# Kredit funksiyalari
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

# /start handler
@dp.message(Command("start"))
async def start_handler(msg: types.Message, state: FSMContext):
    await msg.answer(
        "Salom! 👋 Men sizga kredit hisoblashda yordam beraman.\n"
        "1️⃣ Qarz miqdorini kiriting (misol: 10000000)"
    )
    await state.set_state(KreditForm.summa)

# Summa handler
@dp.message(KreditForm.summa)
async def summa(msg: types.Message, state: FSMContext):
    try:
        summa = float(msg.text.replace(",",""))
        await state.update_data(summa=summa)
        await msg.answer("2️⃣ Yillik foiz stavkasini kiriting (misol: 24)")
        await state.set_state(KreditForm.foiz)
    except:
        await msg.answer("⚠ Iltimos raqam kiriting (misol: 10000000)")

# Foiz handler
@dp.message(KreditForm.foiz)
async def foiz(msg: types.Message, state: FSMContext):
    try:
        foiz = float(msg.text.replace("%",""))
        await state.update_data(foiz=foiz)
        await msg.answer("3️⃣ Muddatni oyda kiriting (misol: 12)")
        await state.set_state(KreditForm.oy)
    except:
        await msg.answer("⚠ Iltimos raqam kiriting (misol: 24)")

# Oy handler
@dp.message(KreditForm.oy)
async def oy(msg: types.Message, state: FSMContext):
    try:
        oy = int(msg.text)
        await state.update_data(oy=oy)
        await msg.answer("4️⃣ Kredit turini kiriting (annuitet yoki oddiy, misol: annuitet)")
        await state.set_state(KreditForm.turi)
    except:
        await msg.answer("⚠ Iltimos butun son kiriting (misol: 12)")

# Kredit turi handler
@dp.message(KreditForm.turi)
async def turi(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    summa = data["summa"]
    foiz = data["foiz"]
    oy = data["oy"]
    turi = msg.text.lower()
    if turi not in ["annuitet","oddiy"]:
        await msg.answer("⚠ Kredit turi faqat 'annuitet' yoki 'oddiy' bo'lishi mumkin!")
        return

    if turi == "annuitet":
        payment = annuitet(summa, foiz, oy)
    else:
        payment = oddiy(summa, foiz, oy)
    total = payment * oy
    extra = total - summa

    await msg.answer(
        f"📌 Oylik to'lov: {payment:,.2f} so‘m\n"
        f"💰 Umumiy to'lov: {total:,.2f} so‘m\n"
        f"📈 Foiz ortiqcha: {extra:,.2f} so‘m\n"
        f"🔹 Bu hisob {turi} kredit turiga asoslangan."
    )

    # Excel jadval
    df = jadval(summa, foiz, oy, turi)
    file_bytes = io.BytesIO()
    df.to_excel(file_bytes, index=False)
    file_bytes.seek(0)
    await msg.answer_document(types.InputFile(file_bytes, filename="kredit_jadval.xlsx"))

    # Grafik
    img = grafik(df)
    await msg.answer_photo(types.InputFile(img, filename="qarz_grafik.png"))
    await state.clear()

# Ishga tushurish
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
