from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, CallbackQueryHandler, CommandHandler, ContextTypes
from uuid import uuid4
import os
import sys

# Agar bu Webhook muhiti bo'lsa (Render.com ga mos keladi), Polling ishlamasligi mumkin.
# Agar polling usulida qolishni istasangiz, quyidagi kodni ishlating.

TOKEN = "8357664064:AAErg5wtBqYNK3FnUYmf26tZXe7-Mxrb9_w"  # <-- Bu joyga tokeningizni yozing

games = {}

def new_board():
    """Yangi, bo'sh o'yin maydonini qaytaradi."""
    return [
        ["⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜"]]

def board_text(board):
    """O'yin taxtasini matn ko'rinishida formatlash"""
    return "\n".join(" ".join(row) for row in board)

def make_markup(board):
    """O'yin taxtasi uchun inline klaviaturani yaratadi."""
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(InlineKeyboardButton(board[i][j], callback_data=f"{i},{j}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def check_win(board, symbol):
    """G'alaba holatini tekshiradi"""
    # Qator va ustunlarni tekshirish
    for i in range(3):
        if all(board[i][j] == symbol for j in range(3)): return True
        if all(board[j][i] == symbol for j in range(3)): return True
    # Diagonallarni tekshirish
    if all(board[i][i] == symbol for i in range(3)): return True
    if all(board[i][2-i] == symbol for i in range(3)): return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start buyrug'iga javob beradi"""
    await update.message.reply_text("X va O o‘yinini boshlash uchun inline rejimida yozing (masalan, @bot_usernamingiz)", reply_markup=None)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline so'rovni boshqaradi"""
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="🎮 X va O o‘yinini boshlash",
            input_message_content=InputTextMessageContent("X va O o‘yini boshlandi!"),
            reply_markup=make_markup(new_board()),
            description="O‘yinni do‘stingizga yuboring."
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline tugmachalardagi bosishlarni boshqaradi"""
    query = update.callback_query
    await query.answer() # Tez javob berish
    user = query.from_user
    data = query.data
    message = query.message

    key = f"{message.chat_id}:{message.message_id}"
    
    # O'yinni topish yoki yaratish
    if key not in games:
        games[key] = {"board": new_board(), "players": {}, "turn": None}

    game = games[key]
    # Agar data bo'sh bo'lsa (bo'sh tugma yuborilgan bo'lsa), xato bermaslik uchun tekshiruv
    if not data or data == 'None':
        await query.answer("Noto'g'ri yurish ma'lumoti.", show_alert=True)
        return

    try:
        i, j = map(int, data.split(','))
    except ValueError:
        # Agar split xato bersa
        await query.answer("Noto'g'ri tugma ma'lumoti.", show_alert=True)
        return

    board = game["board"]

    # O'yinchilarni tayinlash (symbol va name ni saqlash)
    if user.id not in game["players"]:
        if len(game["players"]) == 0:
            # 1-o'yinchi
            game["players"][user.id] = {"symbol": "❌", "name": user.first_name}
            game["turn"] = user.id
        elif len(game["players"]) == 1:
            # 2-o'yinchi
            game["players"][user.id] = {"symbol": "⭕", "name": user.first_name}

    player_info = game["players"].get(user.id)
    
    # Tekshiruvlar
    if not player_info:
        await query.answer("Bu o‘yin 2 kishilik! Iltimos, boshqa o'yinchi qo'shilishini kuting.", show_alert=True)
        return

    if user.id != game["turn"]:
        await query.answer("Sizning navbatingiz emas!", show_alert=True)
        return

    if board[i][j] != "⬜":
        await query.answer("Bu joy band!", show_alert=True)
        return

    # Yurishni bajarish
    symbol = player_info["symbol"]
    board[i][j] = symbol

    # G'alaba holatini tekshirish
    if check_win(board, symbol):
        await query.edit_message_text(
            f"{board_text(board)}\n\n🏆 {user.first_name} yutdi! O‘yin tugadi.",
            reply_markup=None
        )
        if key in games:
            del games[key]
        return

    # Durang holatini tekshirish
    if all(cell != "⬜" for row in board for cell in row):
        await query.edit_message_text(f"{board_text(board)}\n\n🤝 Durang!", reply_markup=None)
        if key in games:
            del games[key]
        return

    # Navbatni almashtirish
    other_ids = [pid for pid in game["players"] if pid != user.id]
    if other_ids:
        game["turn"] = other_ids[0]

    # Status xabarini yangilash
    turn_info = game["players"].get(game["turn"])
    if turn_info:
        status = f"Navbat: {turn_info['name']} ({turn_info['symbol']})"
    else:
        status = "Navbat: Ikkinchi o'yinchi qo'shilishi kutilyapti..."

    await query.edit_message_text(board_text(board) + "\n\n" + status, reply_markup=make_markup(board))

# --- BOTNI ISHGA TUSHIRISH ---
# Polling usuli Render Web Services uchun mos kelmasligi mumkin, lekin sizning talabingiz bo'yicha.
try:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(button))

    print("✅ X va O bot ishga tushdi...")
    # sys.exit() orqali ilova to'xtatilishining oldini olish uchun run_polling ishlatiladi.
    app.run_polling(poll_interval=1)

except Exception as e:
    print(f"❌ Xato yuz berdi: {e}")
    # Render muhitida ApplicationBuilder ishlashi uchun barcha kerakli qismlar import qilingan.


