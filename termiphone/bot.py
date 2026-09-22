import os
import html
from shell import Shell
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from auth import Auth
from dotenv import load_dotenv

load_dotenv()

auth = Auth(allowed_id=int(os.environ["TG_ALLOWED_ID"]))
shell = Shell()

def allowed(update):
    return update.effective_user and auth.is_allowed(update.effective_user.id)

async def login(update, context ):
    if not allowed(update):
        return
    code = "".join(context.args)
    ok = auth.login(code)
    await update.message.delete()
    text = "Session opened (15 mins)" if ok else "Code is wrong or you are blocked."
    await context.bot.send_message(update.effective_chat.id, text)

async def logout(update, context):
    if not allowed(update):
        return
    auth.logout()
    await update.message.reply_text("Session closed.")

async def on_text(update, context):
    if not allowed(update):
        return
    if not auth.is_active():
        await update.message.reply_text("Please login first.")
        return
    auth.touch()
    shell.send(update.message.text)
    output = shell.read()
    if output:
        safe = html.escape(output)
        await update.message.reply_text(f"<pre>{safe}</pre>", parse_mode="HTML")

async def ctrl(update, context):
    if not allowed(update):
        return
    if not auth.is_active():
        return
    letter = context.args[0] if context.args else ""
    shell.send_key(letter)
    output = shell.read()
    if output:
        safe = html.escape(output)
        await update.message.reply_text(f"<pre>{safe}</pre>", parse_mode="HTML")

app = Application.builder().token(os.environ["TG_TOKEN"]).build()

app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("logout", logout))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
app.add_handler(CommandHandler("ctrl", ctrl))
app.run_polling()