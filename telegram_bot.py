import os
import asyncio
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from chat_session import ChatSession
from gemini_bot import get_response as gemini_respond
from ollama_bot import get_response as ollama_respond

# === Setup ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 

# === Per-user session memory ===
user_sessions = {}       # user_id -> ChatSession
user_models = {}         # user_id -> 'gemini' or 'ollama'

# === Start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = ChatSession()
    user_models[user_id] = "gemini"  # default model
    await update.message.reply_text("👋 Welcome to Indian Law Bot!\nUse /model gemini or /model ollama to choose LLM.\nAsk any legal question, e.g., 'Can I show my license digitally?'")

# === Model Selection ===
async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) == 0:
        await update.message.reply_text("Please specify a model: /model gemini or /model ollama")
        return
    choice = context.args[0].lower()
    if choice in ["gemini", "ollama"]:
        user_models[user_id] = choice
        await update.message.reply_text(f"✅ Model set to: {choice.capitalize()}")
    else:
        await update.message.reply_text("❌ Invalid model. Use /model gemini or /model ollama")

# === Reset Command ===
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = ChatSession()
    await update.message.reply_text("🧠 Memory reset. Start a new legal query.")

# === Handle User Messages ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.message.text

    # Setup session and model if missing
    session = user_sessions.setdefault(user_id, ChatSession())
    model = user_models.setdefault(user_id, "gemini")

    # Add user input to memory
    session.add_user_message(query)

    # Limit history to last 4 turns
    short_history = session.get_history()[-4:]

    # Generate response
    respond = gemini_respond if model == "gemini" else ollama_respond
    response = respond(query, short_history)

    # Add bot reply to memory
    session.add_bot_message(response)

    await update.message.reply_text(f"🤖 {response}")

# === Run Bot ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("model", model))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("🤖 Telegram bot is running...")
    app.run_polling()
