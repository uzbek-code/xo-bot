from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, CallbackQueryHandler, ContextTypes
from uuid import uuid4

TOKEN = "8357664064:AAErg5wtBqYNK3FnUYmf26tZXe7-Mxrb9_w"  # <-- bu joyga tokeningni yoz

games = {}

def new_board():
    return [
        ["⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜"]]

def make_markup(board):
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(InlineKeyboardButton(board[i][j], callback_data=f"{i},{j}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def check_win(board, symbol):
    for i in range(3):
        if all(board[i][j] == symbol for j in range(3)): return True
        if all(board[j][i] == symbol for j in range(3)): return True
    if all(board[i][i] == symbol for i in range(3)): return True
    if all(board[i][2-i] == symbol for i in range(3)): return True
    return False

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="🎮 X va O o‘yinini boshlash",
            input_message_content=InputTextMessageContent("X va O o‘yini boshlandi!"),
            reply_markup=make_markup(new_board())
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    message = query.message

    key = f"{message.chat_id}:{message.message_id}"
    if key not in games:
        games[key] = {
            "board": new_board(),
            "players": {},
            "turn": None
        }

    game = games[key]
    i, j = map(int, data.split(','))
    board = game["board"]

    # Belgilarni tayinlash
    if user.id not in game["players"]:
        if len(game["players"]) == 0:
            game["players"][user.id] = "❌"
            game["turn"] = user.id
        elif len(game["players"]) == 1:
            game["players"][user.id] = "⭕"

    symbol = game["players"].get(user.id, None)
    if not symbol:
        await query.answer("Bu o‘yin 2 kishilik!", show_alert=True)
        return

    if user.id != game["turn"]:
        await query.answer("Sizning navbatingiz emas!", show_alert=True)
        return

    if board[i][j] != "⬜":
        await query.answer("Bu joy band!", show_alert=True)
        return

    board[i][j] = symbol

    # Yutish holatini tekshirish
    if check_win(board, symbol):
        await query.edit_message_text(
            f"🏆 {user.first_name} yutdi!\nO‘yin tugadi.",
            reply_markup=None
        )
        del games[key]
        return

    # Durang holati
    if all(cell != "⬜" for row in board for cell in row):
        await query.edit_message_text("🤝 Durang!", reply_markup=None)
        del games[keyfrom telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, CallbackQueryHandler, ContextTypes, CommandHandler
from uuid import uuid4

TOKEN = "Bot_tokeni_yoz"  # <-- bu joyga tokeningni yoz

# O'yin holatini saqlash uchun lug'at (ChatID:MessageID)
# Har bir o'yin quyidagilarni saqlaydi: {"board": [], "players": {user_id: symbol}, "turn": user_id}
games = {}

def new_board():
    """Yangi, bo'sh o'yin maydonini qaytaradi."""
    return [
        ["⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜"]]

def make_markup(board):
    """O'yin maydonini inline tugmalar shaklida yaratadi."""
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            # Har bir tugma o'zining koordinatasini (callback_data) saqlaydi
            row.append(InlineKeyboardButton(board[i][j], callback_data=f"{i},{j}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def check_win(board, symbol):
    """Berilgan belgi (symbol) uchun g'alaba holatini tekshiradi."""
    
    # Qatorlar va ustunlarni tekshirish
    for i in range(3):
        if all(board[i][j] == symbol for j in range(3)): return True # Qator
        if all(board[j][i] == symbol for j in range(3)): return True # Ustun
    
    # Diagonallarni tekshirish
    if all(board[i][i] == symbol for i in range(3)): return True # Asosiy diagonal
    if all(board[i][2-i] == symbol for i in range(3)): return True # Qarama-qarshi diagonal
        
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start buyrug'iga javob beradi. """
    await update.message.reply_text(
        "Salom! Men X va O o'yin botiman (2 kishilik).\n"
        "O'yinni boshlash uchun chatda @BotIsmingiz ni yozing va o'yinni tanlang."
    )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline so'rovga javob berib, o'yinni boshlash tugmasini chiqaradi."""
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="🎮 X va O o‘yinini boshlash",
            input_message_content=InputTextMessageContent("X va O o‘yini boshlandi! Birinchi o'yinchi (❌) boshlasin."),
            reply_markup=make_markup(new_board())
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline tugma bosilganda ishga tushadi. 2 kishilik o'yin mantiqi."""
    query = update.callback_query
    user = query.from_user
    data = query.data
    message = query.message

    key = f"{message.chat_id}:{message.message_id}"
    
    # O'yin holatini yuklash yoki yaratish
    if key not in games:
        games[key] = {
            "board": new_board(),
            "players": {},
            "turn": None
        }

    game = games[key]
    i, j = map(int, data.split(','))
    board = game["board"]

    # --- 1. O'yinchilarni tayinlash ---
    if user.id not in game["players"]:
        if len(game["players"]) == 0:
            # 1-o'yinchi (❌)
            game["players"][user.id] = "❌"
            game["turn"] = user.id
            await query.answer(f"Siz ❌ belgisini tanladingiz. Do'stingizni (⭕) kutamiz!")
            return
        elif len(game["players"]) == 1:
            # 2-o'yinchi (⭕)
            game["players"][user.id] = "⭕"
            await query.answer("Siz ⭕ belgisini tanladingiz. O'yin boshlandi!")
        else:
            # 2 o'yinchi bor, boshqa odamlar aralashmasin
            await query.answer("Bu o‘yin allaqachon boshlangan va to'lgan!", show_alert=True)
            return

    symbol = game["players"].get(user.id, None)

    # --- 2. Navbatni tekshirish ---
    if user.id != game["turn"]:
        await query.answer("Sizning navbatingiz emas!", show_alert=True)
        return

    # --- 3. Band joyni tekshirish ---
    if board[i][j] != "⬜":
        await query.answer("Bu joy band! Boshqasini tanlang.", show_alert=True)
        return

    # --- 4. Yurishni bajarish ---
    board[i][j] = symbol

    # --- 5. G'alaba holatini tekshirish ---
    if check_win(board, symbol):
        await query.edit_message_text(
            f"🏆 {user.first_name} ({symbol}) yutdi!\nO‘yin tugadi.",
            reply_markup=None
        )
        del games[key]
        return

    # --- 6. Durang holati ---
    if all(cell == "❌" or cell == "⭕" for row in board for cell in row):
        await query.edit_message_text("🤝 Durang! O‘yin tugadi.", reply_markup=None)
        del games[key]
        return

    # --- 7. Navbatni almashtirish ---
    
    # 2-o'yinchi topilsa, navbatni unga o'tkazamiz
    if len(game["players"]) == 2:
        next_player_id = None
        for pid in game["players"]:
            if pid != user.id:
                next_player_id = pid
                break
        
        # Navbatni almashtirish
        game["turn"] = next_player_id
        
        # O'yin holatini yangilash
        await query.edit_message_reply_markup(reply_markup=make_markup(board))
        await query.answer("✅ Yurish qabul qilindi!")
    else:
        # Birinchi o'yinchi yurgan bo'lsa, ikkinchi o'yinchini kutadi
        await query.edit_message_reply_markup(reply_markup=make_markup(board))
        await query.answer("✅ Yurish qabul qilindi! Ikkinchi o'yinchi qo'shilishi kerak.")


# --- Botni ishga tushirish ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(InlineQueryHandler(inline_query))
app.add_handler(CallbackQueryHandler(button))

print("✅ Inline XO bot ishga tushdi (2 kishilik rejim)...")
app.run_polling()
