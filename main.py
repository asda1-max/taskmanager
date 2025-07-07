import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,ConversationHandler,MessageHandler,filters
usrdat = {}
active_sessions = {}
usrtask ={}

# Open User file
if os.path.exists("userfile.json"):
    with open("userfile.json", "r") as file:
        usrdat = json.load(file)
else:
    usrdat = {}

# Open task file
def load_task_data():
    global usrtask
    if os.path.exists("taskdata.json"):
        with open("taskdata.json", "r") as taskfile:
            usrtask = json.load(taskfile)
    else:
        usrtask = {}

load_task_data()

def savefile():
    with open("userfile.json", "w") as file:
        json.dump(usrdat, file, indent=4)

def saveTaskData():
    with open("taskdata.json", "w") as taskfile:
        json.dump(usrtask, taskfile, indent=4)  

TASK_NAME, TASK_DEADLINE, TASK_PRIORITY = range(3)



async def start(update : Update, context :ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("sup mantab jiwa")


async def sign_up(update : Update, context :ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    raw = message[4:].strip()
    
    if '-' not in raw:
        await update.message.reply_text("salah format")
    else :
        parts = raw.split('-',1)
        usn = parts[0].strip()
        pw = parts[1].strip()
        
        if usn in usrdat:
            await update.message.reply_text (f"Username '{usn}' sudah terdaftar.")
        else :
            usrdat[usn] = pw
            await update.message.reply_text(f"Berhasil daftar : '{usn}'")
            savefile()
       

async def sign_in(update : Update, context :ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    raw = message[4:].strip()
    
    if '-' not in raw:
        await update.message.reply_text("salah format")
    else :
        parts = raw.split('-',1)
        usn = parts[0].strip()
        pw = parts[1].strip()

        if usn in usrdat:
            if usrdat[usn] == pw:
                uid = update.effective_user.id
                await update.message.reply_text(f"login berhasil sebagai : {usn}")
                active_sessions[uid] = {
                    "username": usn,
                    "login_time": pw
                }
            else :
                await update.message.reply_text("gagal login pw atau usn salah")

async def sign_out(update : Update, context :ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in active_sessions:
        del active_sessions[uid]
        await update.message.reply_text("Kamu telah logout")
    else:
        await update.message.reply_text("Belum login")

async def cancel(update : Update, context :ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("memasukan task digagalkan oleh user")
    return ConversationHandler.END

async def saveTask(update : Update, context :ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    load_task_data()
    tn = update.message.text.strip()
    task = {
        "TASK_NAME" : context.user_data["TASK_NAME"],
        "TASK_DEADLINE" : context.user_data["TASK_DEADLINE"],
        "TASK_PRIORITY" : tn
    }

    # Get the username from the active session
    session = active_sessions.get(uid)
    if not session:
        await update.message.reply_text("Kamu belum login.")
        return ConversationHandler.END

    username = session["username"]

    usrtask.setdefault(username, []).append(task)
    
    saveTaskData()
    await update.message.reply_text(f"Task '{task['TASK_NAME']}' telah disimpan 💼")
    return ConversationHandler.END

async def add_taskName(update : Update, context : ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in active_sessions: 
        await update.message.reply_text("Masukan Nama Task : ")
        return TASK_NAME
    else :
        await update.message.reply_text("Kamu belum login. Gunakan /si dulu ya~")
        return ConversationHandler.END
    
async def add_taskDeadline(update : Update, context : ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in active_sessions:
        context.user_data["TASK_NAME"] = update.message.text.strip() 
        await update.message.reply_text("Masukan Deadline Task : ")
        return TASK_DEADLINE
    else :
        await update.message.reply_text("Kamu belum login. Gunakan /si dulu ya~")
        return ConversationHandler.END
    
async def add_taskPriority(update : Update, context : ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in active_sessions: 
        context.user_data["TASK_DEADLINE"] = update.message.text.strip() 
        await update.message.reply_text("Masukan Priority Task : ")
        return TASK_PRIORITY
    else :
        await update.message.reply_text("Kamu belum login. Gunakan /si dulu ya~")
        return ConversationHandler.END

async def view_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    uid = update.effective_user.id
    username = active_sessions.get(uid)["username"]

    if uid not in active_sessions:
        await update.message.reply_text("Kamu belum login.")
        return

    load_task_data()
    tasks = usrtask.get(username, [])

    if not tasks:
        await update.message.reply_text("Belum ada task tersimpan... 😴")
        return

    msg = "📋 Daftar Task:\n"
    for i, task in enumerate(tasks, 1):
        msg += f"{i}. {task}\n"

    await update.message.reply_text(msg)
        
conv = ConversationHandler(
    entry_points=[CommandHandler("addtask", add_taskName)],
    states={
        TASK_NAME : [MessageHandler(filters.TEXT & ~filters.COMMAND, add_taskDeadline)],
        TASK_DEADLINE : [MessageHandler(filters.TEXT & ~filters.COMMAND, add_taskPriority)],
        TASK_PRIORITY : [MessageHandler(filters.TEXT & ~filters.COMMAND, saveTask)]
    },
    fallbacks=[CommandHandler("cancel", cancel )]
    )     
        
app = ApplicationBuilder().token("7758310262:AAFZfDolpGpyVVauy6poLvELnlMMkbIzKHo").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("su", sign_up))
app.add_handler(CommandHandler("si", sign_in))
app.add_handler(CommandHandler("so", sign_out))
app.add_handler(CommandHandler("viewtask", view_task))
app.add_handler(conv)
app.run_polling()