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
