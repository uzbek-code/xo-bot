from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8357664064:AAErg5wtBqYNK3FnUYmf26tZXe7-Mxrb9_w"

games = {}

def new_board():
    return [["⬜", "⬜", "⬜"],
            ["⬜", "⬜", "⬜"],
            ["⬜", "⬜", "⬜"]]

def board_markup(board):
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(InlineKeyboardButton(board[i][j], callback_data=f"{i},{j}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    games[user.id] = new_board()
    await update.message.reply_text(
        "X va O o'yiniga xush kelibsiz!\nSiz X bilan o'ynaysiz.",
        reply_markup=board_markup(games[user.id])
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data.split(',')
    i, j = int(data[0]), int(data[1])

    board = games.get(user.id, new_board())
    if board[i][j] != "⬜":
        await query.edit_message_text("Bu joy band! Boshqasini tanlang.")
        return

    board[i][j] = "❌"

    from random import choice
    empty = [(x, y) for x in range(3) for y in range(3) if board[x][y] == "⬜"]
    if empty:
        x, y = choice(empty)
        board[x][y] = "⭕"

    games[user.id] = board
    await query.edit_message_reply_markup(reply_markup=board_markup(board))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("✅ Bot ishlamoqda...")
app.run_polling()
