import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

ADMIN_ID = 8105450151  # Twój ID admina
GROUP_ID = -1002665519611  # ID Twojej grupy

TOKEN = os.environ.get("BOT_TOKEN")

calkowity_zysk = 0
saldo_do_wyplaty = 0
user_balances = {}
user_ltc_addresses = {}
user_usernames = {}
user_codes = {}

status = "Offline"

def save_status(status):
    with open('status.json', 'w') as file:
        json.dump({"status": status}, file)

def load_status():
    try:
        with open('status.json', 'r') as file:
            data = json.load(file)
            return data.get("status", "offline")  # Domyślny status to 'offline'
    except FileNotFoundError:
        return "offline"

def load_users():
    try:
        with open('users.json', 'r') as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(list(users), file)

def load_user_usernames():
    try:
        with open('user_usernames.json', 'r') as file:
            data = json.load(file)
            print(f"Załadowano użytkowników: {data}")  # Debugowanie
            return data
    except FileNotFoundError:
        return {}

def save_user_usernames():
    with open('user_usernames.json', 'w') as file:
        json.dump(user_usernames, file, ensure_ascii=False, indent=4)
        print(f"Zapisano użytkowników: {user_usernames}")  # Debugowanie

def load_user_usernames():
    try:
        with open('user_usernames.json', 'r') as file:
            data = json.load(file)
            print(f"Załadowano użytkowników: {data}")  # Debugowanie
            return data
    except FileNotFoundError:
        return {}

def save_user_usernames():
    with open('user_usernames.json', 'w') as file:
        json.dump(user_usernames, file)

all_users = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    username = user.username or "Użytkownik bez nazwy"

    # Zapisujemy username w słowniku
    user_usernames[str(user_id)] = username
    save_user_usernames()

    all_users.add(user_id)
    save_users(all_users)

    message = (
        f"✦ 👤 @{username} ✦ 💬 Status: {status} ✦\n\n"
        f"📊 Podział:\n"
        f"🔽 <1000 — 30/70\n"
        f"🔼 >1000 — 25/70\n\n"
        f"💰 Dzisiejsze Zarobki: {user_balances.get(user_id, 0)} PLN\n"  
        f"💸 Dzisiejsze Zarobki Wszystkich: {calkowity_zysk} PLN\n\n"
        f"👇 Przed każdą sesją dodaj swój adres ltc do portfela 👇\n"
    )

    keyboard = [
        [InlineKeyboardButton("🥳 Wrzuć Blika➔", callback_data='blik')],
        [InlineKeyboardButton("🏦 Portfel➔", callback_data='portfel')],
        [InlineKeyboardButton("🎟 Vouche➔", callback_data='vouche')]  # Dodany przycisk Vouche
    ]

    with open("logo.jpg", "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Usuń tę linię, bo już wysyłasz wiadomość z obrazkiem
    
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Tylko administrator ma dostęp do tej komendy.")
        return
    await update.message.reply_text("✍️ Wprowadź wiadomość, którą chcesz wysłać do użytkowników:")
    context.user_data['message_to_send'] = True

async def online(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Sprawdzenie, czy tylko admin może wywołać komendę
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Tylko administrator ma dostęp do tej komendy.")
        return
    
    # Ustawienie statusu "online"
    global status
    status = "online"
    save_status(status)  # Funkcja, która zapisuje status do pliku
    await update.message.reply_text("✅ Bot jest teraz aktywny ✅")

    # Wysłanie wiadomości do wszystkich użytkowników
    for user_id in all_users:
        try:
            username = user_usernames.get(str(user_id), "Użytkownik bez nazwy")
            await context.bot.send_message(user_id, f"✅ Bot jest teraz aktywny ✅")
        except:
            continue

async def offline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Sprawdzenie, czy tylko admin może wywołać komendę
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Tylko administrator ma dostęp do tej komendy.")
        return
    
    # Ustawienie statusu "offline"
    global status
    status = "offline"
    save_status(status)  # Funkcja, która zapisuje status do pliku
    await update.message.reply_text("🚫 Bot jest teraz nieaktywny 🚫")

    # Wysłanie wiadomości do wszystkich użytkowników
    for user_id in all_users:
        try:
            username = user_usernames.get(str(user_id), "Użytkownik bez nazwy")
            await context.bot.send_message(user_id, f"🚫 Bot jest teraz nieaktywny 🚫")
        except:
            continue

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip()

    # Jeśli nie mamy przypisanego username, przypisujemy "Użytkownik bez nazwy"
    if str(user_id) not in user_usernames:
        if user.username:  # Sprawdzamy, czy użytkownik ma nazwę użytkownika
            user_usernames[str(user_id)] = user.username
        else:
            user_usernames[str(user_id)] = "Użytkownik bez nazwy"

        # Zapisujemy użytkowników z ich username do pliku
        save_user_usernames()

    # Teraz możemy kontynuować resztę logiki (np. wysyłanie wiadomości do wszystkich)
    if context.user_data.get('message_to_send'):
        wyslano_do = []
        for uid in all_users:
            try:
                # Używamy user_usernames, by sprawdzić, czy mamy przypisane username
                username = user_usernames.get(str(uid), "Użytkownik bez nazwy")
                await context.bot.send_message(uid, f"🔔 Ogłoszenie\n\n{text}")  # <-- ta linia
                wyslano_do.append(f"• {uid} - @{username}")
            except:
                continue

        ilosc = len(wyslano_do)
        lista_odbiorcow = "\n".join(wyslano_do) if wyslano_do else "Brak odbiorców."

        await update.message.reply_text(
            f"👷 Status {ilosc} workerów:\n\n✅ Widoczna nazwa użytkownika= Online\n🚫 Brak nazwy użytkownika= Offline\n\n{lista_odbiorcow}"
        )
        context.user_data.clear()
        return


    # Obsługa podawania kwoty
    if context.user_data.get('expecting_amount'):
        try:
            amount = float(text)
            if amount <= 100:
                await update.message.reply_text("Kwota musi być większa niż 100 PLN.")
                return
        except:
            await update.message.reply_text("Podaj poprawną liczbę.")
            return

        if user_id not in user_ltc_addresses:
            await update.message.reply_text("❗️ Najpierw dodaj adres LTC w sekcji Portfel.")
            return

        context.user_data['amount'] = amount
        context.user_data['expecting_amount'] = False
        await update.message.reply_text("🔐 Podaj kod Blik\n---✮ ✮ ✮ ✮ ✮ ✮---")
        return

# Obsługa podawania adresu LTC
    if context.user_data.get('expecting_ltc_address'):
        user_ltc_addresses[user_id] = text
        context.user_data['expecting_ltc_address'] = False
        keyboard = [[InlineKeyboardButton("↩️ Powrót", callback_data='back_to_main')]]
        await update.message.reply_text(f"🏦 Twój Adres LTC:\n{text}", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Obsługa kodu blik
    if len(text) == 6 and text.isdigit():
        amount = context.user_data.get('amount')
        if amount is None:
            await update.message.reply_text("Najpierw podaj kwotę.")
            return

        code = text
        user_usernames[user_id] = user.username
        user_codes[user_id] = code

        keyboard = [
            [InlineKeyboardButton("Akceptuj ✅", callback_data=f'accept_{user_id}_{amount}_{code}')],
            [InlineKeyboardButton("Odrzuć ❌", callback_data=f'reject_{user_id}_{amount}_{code}')],
        ]

        await context.bot.send_message(
            GROUP_ID,
            f"💳 Nowy kod blik:\n\n"
            f"💸 Kwota: {amount} PLN \n"
            f"🔐 Kod Blik: {code} \n"
            f"👷 Worker: @{user.username}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await update.message.reply_text(
            f"✪ 🕵️ Oczekuję na Cashoutera... ✪\n\n"
            f"💸 Kwota: {amount} PLN\n"
            f"🔐 Kod Blik: {code}\n\n"
            f"→ <i>Poczekaj na dalsze informacje!</i>",
            parse_mode="HTML"
        )
        context.user_data.clear()
        return

    # Domyślna odpowiedź jeśli nic nie pasuje
    await update.message.reply_text("❗️ Kod Blik musi zawierać 6 cyfr.")

async def main_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

async def main_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'blik':
        if user_id not in user_ltc_addresses:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="       ❗️ Brak Adresu LTC = Brak Wypłaty ❗️\n👇 Wklej Swój PRAWIDŁOWY Adres LTC Poniżej👇"
            )
            context.user_data['expecting_ltc_address'] = True
            return
        
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="💸 Podaj kwotę\n------------$-----------"
        )
        context.user_data['expecting_amount'] = True

    elif query.data == 'portfel':
        keyboard = [
            [InlineKeyboardButton("🏦 Zmień adres LTC➔", callback_data='change_ltc')],
            [InlineKeyboardButton("📊 Zobacz swój adres LTC➔", callback_data='show_ltc')],
            [InlineKeyboardButton("↩️ Powrót", callback_data='back_to_main')],
        ]
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📈 Twój portfel",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'vouche':
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        keyboard = [
            [InlineKeyboardButton("📢  Kanał z vouch'ami", url="https://t.me/katujemyvouche")],
            [InlineKeyboardButton("↩️ Powrót", callback_data='back_to_main')]
        ]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🎟 Sprawdź nasz kanał z vouchami, aby zobaczyć opinie innych użytkowników!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'back_to_main':
        user = query.from_user
        username = user.username or "Użytkownik bez nazwy"
        
        # Zmienna `status` i `calkowity_zysk` muszą być wcześniej zdefiniowane
        message = (
            f"✦ 👤 @{username} ✦ 💬 Status: {status} ✦\n\n"
            f"📊 Podział: 30/70\n"
            f"🔽 <1000 — 30/70\n"
            f"🔼 >1000 — 25/70\n\n"
            f"💰 Dzisiejsze Zarobki: {calkowity_zysk} PLN\n"
            f"💸 Dzisiejsze Zarobki Wszystkich: {calkowity_zysk} PLN\n\n"
            f"👇 Przed każdą sesją dodaj swój adres do portfela 👇\n"
        )
        keyboard = [
            [InlineKeyboardButton("🥳 Wrzuć Blika→", callback_data='blik')],
            [InlineKeyboardButton("🏦 Portfel→", callback_data='portfel')],
            [InlineKeyboardButton("🎟 Vouche→", callback_data='vouche')]
        ]
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        with open("logo.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo,
                caption=message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif query.data == 'change_ltc':
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✏️ Podaj nowy adres LTC:"
        )
        context.user_data['expecting_ltc_address'] = True

    elif query.data == 'show_ltc':
        address = user_ltc_addresses.get(user_id)
        msg = f"Twój adres LTC to:\n{address}" if address else "Nie masz jeszcze ustawionego adresu LTC."
        keyboard = [[InlineKeyboardButton("↩️ Powrót", callback_data='back_to_main')]]
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def process_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    global calkowity_zysk, saldo_do_wyplaty

    data = query.data

    if data.startswith(('accept_', 'reject_')):  # Akceptacja lub odrzucenie kodu Blik
        action, uid, amt, code = data.split('_')
        user_id = int(uid)
        amount = float(amt)
        username = user_usernames.get(user_id, f"ID:{user_id}")

        if action == 'accept':
            keyboard = [
                [InlineKeyboardButton("🖕 DIP", callback_data=f'next_DIP_{user_id}_{amount}_{code}')],
                [InlineKeyboardButton("❌ ODRZUT", callback_data=f'next_ODRZUT_{user_id}_{amount}_{code}')],
                [InlineKeyboardButton("⚠️ LIMIT", callback_data=f'next_LIMIT_{user_id}_{amount}_{code}')],
            ]
            await query.edit_message_text(
                f"💳 Zaakceptowano kod blik:\n\n"
                f"💸 Kwota: {amount} PLN \n"
                f"🔐 Kod Blik: {code} \n"
                f"👷 Worker: @{username}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            try:
                await context.bot.send_message(
                    user_id,
                    f"✪ 🏃 Cashouter zajmuje się twoim kodem! ✪\n\n"
                    f"💸 Kwota: {amount} PLN \n"
                    f"🔐 Kod Blik: {code} \n\n"
                    f"→ <i>Poczekaj na dalsze informacje!</i>",
                    parse_mode="HTML"
                )
            except:
                pass

        elif action == 'reject':
            await query.edit_message_text("💔 Cashouter nie zdążył wypłacić kodu")
            try:
                await context.bot.send_message(user_id, "💔 Cashouter nie zdążył wypłacić kodu")
            except:
                pass

    elif data.startswith('next_'):  # Obsługa przycisków "next_DIP", "next_ODRZUT", "next_LIMIT"
        _, step, uid, amt, code = data.split('_')
        user_id = int(uid)
        amount = float(amt)
        username = user_usernames.get(user_id, f"ID:{user_id}")
        ltc = user_ltc_addresses.get(user_id, "Brak adresu LTC")

        if step == 'DIP':
            user_balances[user_id] = user_balances.get(user_id, 0) + amount
            calkowity_zysk += amount

            await query.edit_message_text(
                f"✮🖕 DIP zatwierdzony ✮\n\n"
                f"💸 Kwota: {amount} PLN \n"
                f"🔐 Kod Blik: {code} \n"
                f"👷 Worker: @{username} \n"
                f"🏦 Adres LTC: {ltc}",
                reply_markup=None
            )
            try:
                await context.bot.send_message(
                    user_id,
                    f"✮🖕 DIP - Twój kod blik został wypłacony ✮\n\n"
                    f"💸 Kwota: {amount} PLN \n"
                    f"🔐 Kod Blik: {code} \n\n"
                    f"→ <i>💸 Do twojego salda zostało dodane: {user_balances[user_id]} PLN</i>",
                    parse_mode="HTML"
                )
            except:
                pass

        elif step == 'ODRZUT':
            await query.edit_message_text(
                f"✮❌ ODRZUT zatwierdzony ✮\n\n"
                f"💸 Kwota: {amount} PLN \n"
                f"🔐 Kod Blik: {code}",
                reply_markup=None
            )
            try:
                await context.bot.send_message(
                    user_id,
                    f"✮❌ Odrzucono - Twój kod blik został odrzucony ✮\n\n"
                    f"💸 Kwota: {amount} PLN \n"
                    f"🔐 Kod Blik: {code} \n\n"
                    f"→ <i>Prosimy spróbuj ponownie!</i>",
                    parse_mode="HTML"
                )
            except:
                pass

        elif step == 'LIMIT':
            saldo_do_wyplaty += amount

            await query.edit_message_text(
                f"✮⚠️ LIMIT zatwierdzony ✮\n\n"
                f"💸 Kwota: {amount} PLN \n"
                f"👷 Worker: @{username}",
                reply_markup=None
            )
            try:
                await context.bot.send_message(
                    user_id,
                    f"✮⚠️ LIMIT - Twój kod blik posiada limit ✮\n\n"
                    f"💸 Kwota: {amount} PLN \n"
                    f"🔐 Kod Blik: {code} \n\n"
                    f"→ <i>Prosimy spróbuj ponownie!</i>",
                    parse_mode="HTML"
                )
            except:
                pass

def main():

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("Online", online))
    application.add_handler(CommandHandler("Offline", offline))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(main_button_handler, pattern='^(blik|portfel|vouche|change_ltc|show_ltc|back_to_main)$'))
    application.add_handler(CallbackQueryHandler(process_transaction, pattern='^(accept|reject|next)_'))

    application.run_polling()

if __name__ == '__main__':
    main()
