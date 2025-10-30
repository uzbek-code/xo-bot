from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, CallbackQueryHandler, ContextTypes, CommandHandler
from uuid import uuid4
from random import choice

TOKEN = "8357664064:AAErg5wtBqYNK3FnUYmf26tZXe7-Mxrb9_w"  # <-- bu joyga tokeningni yoz

# O'yin holatini saqlash uchun lug'at (ChatID:MessageID)
# Har bir o'yin quyidagilarni saqlaydi: {"board": [], "players": {user_id: {"symbol": str, "name": str}}, "turn": ID}
games = {}

def new_board():
    """Yangi, bo'sh o'yin maydonini qaytaradi."""
    return [
        ["⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜"]]

def board_text(board):
    """O'yin taxtasini matn ko'rinishida qaytaradi."""
    text = ""
    for row in board:
        text += " ".join(row) + "\n"
    return text.strip()

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
        # Qatorni tekshirish
        if all(board[i][j] == symbol for j in range(3)): 
            return True
        # Ustunni tekshirish
        if all(board[j][i] == symbol for j in range(3)): 
            return True
    
    # Asosiy diagonalni tekshirish (0,0), (1,1), (2,2)
    if all(board[i][i] == symbol for i in range(3)): 
        return True
    
    # Qarama-qarshi diagonalni tekshirish (0,2), (1,1), (2,0)
    if all(board[i][2-i] == symbol for i in range(3)): 
        return True
        
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start buyrug'iga javob beradi. """
    await update.message.reply_text(
        "Salom! Men X va O o'yin botiman.\n"
        "O'yinni boshlash uchun chatda @BotIsmingiz ni yozing va o'yinni tanlang."
    )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline so'rovga javob berib, o'yinni boshlash tugmasini chiqaradi."""
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="🎮 X va O o‘yinini boshlash",
            input_message_content=InputTextMessageContent("X va O o‘yini boshlandi! O'yin maydonini to'ldirishni boshlang."),
            reply_markup=make_markup(new_board())
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline tugma bosilganda ishga tushadi. Yangi mantiq bilan toʻldirildi."""
    query = update.callback_query
    user = query.from_user
    data = query.data
    message = query.message
    
    # Inline o'yin xabarini uning identifikatori orqali olish
    key = f"{message.chat_id}:{message.message_id}"
    
    # O'yin mavjud emasmi? Agar bo'lmasa, uni yaratish
    if key not in games:
        games[key] = {
            "board": new_board(),
            "players": {}, # {user_id: {"symbol": str, "name": str}}
            "turn": None
        }

    game = games[key]
    i, j = map(int, data.split(','))
    board = game["board"]
    
    # --- 1. O'yinchilarni aniqlash va navbatni sozlash ---
    if user.id not in game["players"]:
        if len(game["players"]) == 0:
            # 1-o'yinchi (X)
            game["players"][user.id] = {"symbol": "❌", "name": user.first_name}
            game["turn"] = user.id
        elif len(game["players"]) == 1:
            # 2-o'yinchi (O)
            game["players"][user.id] = {"symbol": "⭕", "name": user.first_name}
        else:
            # Agar 2 ta o'yinchi bo'lsa, qo'shilishga ruxsat yo'q
            await query.answer("Bu o‘yin allaqachon boshlangan va to'lgan!", show_alert=True)
            return

    player_info = game["players"].get(user.id)
    if not player_info:
        # 3-o'yinchi qo'shilishga uringanda, lekin yuqoridagi 'else' dan keyin keladi
        await query.answer("Bu o‘yin 2 kishilik!", show_alert=True)
        return

    if user.id != game["turn"]:
        await query.answer("Sizning navbatingiz emas!", show_alert=True)
        return

    # --- 2. Band katakni tekshirish ---
    if board[i][j] != "⬜":
        await query.answer("Bu joy band! Boshqasini tanlang.", show_alert=True)
        return

    # --- 3. Yurishni bajarish ---
    symbol = player_info["symbol"]
    board[i][j] = symbol

    # --- 4. G'alaba tekshiruvi ---
    if check_win(board, symbol):
        await query.edit_message_text(
            f"{board_text(board)}\n\n🏆 {user.first_name} yutdi!\nO‘yin tugadi.",
            reply_markup=None
        )
        del games[key]
        return

    # --- 5. Durang tekshiruvi ---
    if all(cell != "⬜" for row in board for cell in row):
        await query.edit_message_text(f"{board_text(board)}\n\n🤝 Durang!", reply_markup=None)
        del games[key]
        return

    # --- 6. Navbatni almashtirish ---
    other_ids = [pid for pid in game["players"] if pid != user.id]
    
    # Faqat 2 o'yinchi bo'lsa navbatni almashtiramiz
    if other_ids:
        game["turn"] = other_ids[0]
    # Agar faqat 1 o'yinchi bo'lsa (yoki 2-o'yinchi hali qo'shilmagan bo'lsa), navbat shu o'yinchida qoladi
    # va u boshqa o'yinchining qo'shilishini kutadi.

    # --- 7. Status xabarini yangilash ---
    turn_info = game["players"].get(game["turn"])
    if turn_info:
        status = f"Navbat: {turn_info['name']} ({turn_info['symbol']})"
    else:
        status = "Navbat: Ikkinchi o'yinchi qo'shilishini kutamiz..."

    await query.edit_message_text(board_text(board) + "\n\n" + status, reply_markup=make_markup(board))
    await query.answer("✅ Yurish qabul qilindi!")


# --- Botni ishga tushirish ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(InlineQueryHandler(inline_query))
app.add_handler(CallbackQueryHandler(button))

print("✅ Inline XO bot ishga tushdi...")
app.run_polling()
