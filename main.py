import os
import json
import asyncio
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,ConversationHandler,MessageHandler,filters
from datetime import datetime
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


TASK_NAME, TASK_DESC , TASK_DEADLINE, TASK_PRIORITY = range(4)



async def start(update : Update, context :ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo, Bot Ini dibuat untuk membantu anda dalam mengatur tugas yang anda kerjakan\n\nBot ini Memiliki Fitur :\n1.Input Task beserta Detail\n2.Mengingatkan pengguna apabila task mendekati deadline\n\n ketik /help untuk mencari tahu command")

async def help_s(update : Update, context :ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("List /Command : \n1./su : sign up (daftar akun)\n2./si : sign in (masuk)\n3./so : sign out (keluar)\n\n apabila sudah sign in bisa :\n1./addtask - tambahkan tugas\n2./viewtask : list task yang ada")

async def sign_up(update : Update, context :ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    raw = message[4:].strip()
    
    if '-' not in raw:
        await update.message.reply_text("salah format, Format Yang Benar : /su <username> - <password>\ncontoh : /su user1234 - password123")
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
        await update.message.reply_text("salah format, Format Yang Benar : /si <username> - <password>\ncontoh : /si user1234 - password123")
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
    try:
        priority = int(tn)
        if priority not in [1, 2, 3]:
            await update.message.reply_text("Prioritas harus 1, 2, atau 3.")
            return TASK_PRIORITY
    except ValueError:
        await update.message.reply_text("Prioritas harus berupa angka (1/2/3).")
        return TASK_PRIORITY
    
    TASK_PRIORITY = "belum di set"
    
    if tn == "1" :
        TASK_PRIORITY = "Sangat Penting"
    elif tn == "2" :
        TASK_PRIORITY = "Penting"
    elif tn == "3" :
        TASK_PRIORITY = "Kurang Penting"

    task = {
        "TASK_NAME": context.user_data["TASK_NAME"],
        "TASK_DESC": context.user_data["TASK_DESC"],
        "TASK_DEADLINE": context.user_data["TASK_DEADLINE"],
        "TASK_PRIORITY": TASK_PRIORITY
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

async def add_taskDesc(update : Update, context : ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in active_sessions: 
        context.user_data["TASK_NAME"] = update.message.text.strip() 
        await update.message.reply_text("Masukan Deskripsi dari Task : ")
        return TASK_DESC
    else :
        await update.message.reply_text("Kamu belum login. Gunakan /si dulu ya~")
        return ConversationHandler.END

async def add_taskDeadline(update : Update, context : ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in active_sessions:
        context.user_data["TASK_DESC"] = update.message.text.strip() 
        
        await update.message.reply_text("Masukan Deadline Task (Disclaimer : Format DD-MM-YY)\nContoh : 01-08-2025")
        return TASK_DEADLINE
    else :
        await update.message.reply_text("Kamu belum login. Gunakan /si dulu ya~")
        return ConversationHandler.END
    
    
async def add_taskPriority(update : Update, context : ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in active_sessions: 
        context.user_data["TASK_DEADLINE"] = update.message.text.strip() 

        # Validasi format DD-MM-YYYY dan tidak boleh tanggal sebelum hari ini
        user_input = update.message.text.strip()
        try:
            deadline = datetime.strptime(user_input, "%d-%m-%Y")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if deadline < today:
                await update.message.reply_text("⚠️ Deadline tidak boleh sebelum hari ini. Masukkan tanggal yang valid.")
                return TASK_DEADLINE
            else:
                await update.message.reply_text("Pilih Skala Prioritas : \n1.Paling Penting \n2.Penting\n3.KurangPenting\n\n anda bisa memilih berdasar angka (1/2/3)")
                return TASK_PRIORITY
        except ValueError:
            await update.message.reply_text("⚠️ Format salah. Gunakan DD-MM-YYYY, contoh: 01-08-2025")
            return TASK_DEADLINE
       
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
        await update.message.reply_text("Belum ada task tersimpan... ")
        return

    msg = "📋 Daftar Task:\n"
    for i, task in enumerate(tasks, 1):

        msg += f"\n{i}. {task['TASK_NAME']}\n"
        msg += f"-----------------------------------\n"
        msg += f"\t|->  Description : {task['TASK_DESC']}\n"
        msg += f"\t|->  Deadline : {task['TASK_DEADLINE']}\n"
        msg += f"\t|->  Priority : {task['TASK_PRIORITY']}\n"


    await update.message.reply_text(msg)

DELETE_TASK = range(100, 101)  # Unique state for delete task

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in active_sessions:
        await update.message.reply_text("Kamu belum login.")
        return ConversationHandler.END

    username = active_sessions[uid]["username"]
    load_task_data()
    tasks = usrtask.get(username, [])

    if not tasks:
        await update.message.reply_text("Belum ada task tersimpan... ")
        return ConversationHandler.END

    msg = "Masukkan nomor task yang ingin dihapus:\n"
    for i, task in enumerate(tasks, 1):
        msg += f"{i}. {task['TASK_NAME']}\n"

    await update.message.reply_text(msg)
    context.user_data["delete_tasks"] = tasks  # Simpan list tasks untuk referensi
    return DELETE_TASK

async def handle_delete_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in active_sessions:
        await update.message.reply_text("Kamu belum login.")
        return ConversationHandler.END

    username = active_sessions[uid]["username"]
    tasks = context.user_data.get("delete_tasks", [])

    try:
        idx = int(update.message.text.strip()) - 1
        if 0 <= idx < len(tasks):
            deleted_task = tasks.pop(idx)
            usrtask[username] = tasks
            saveTaskData()
            await update.message.reply_text(f"Task '{deleted_task['TASK_NAME']}' berhasil dihapus.")
        else:
            await update.message.reply_text("Nomor task tidak valid.")
    except ValueError:
        await update.message.reply_text("Masukkan nomor task yang valid.")

    context.user_data.pop("delete_tasks", None)
    return ConversationHandler.END

async def reminder_job(app):
    while True:
        now = datetime.now()
        if now.hour in [7, 19] and now.minute == 3:
            load_task_data()
            for uid, session in active_sessions.items():
                username = session["username"]
                tasks = usrtask.get(username, [])
                reminders = []

                for task in tasks:
                        deadline = datetime.strptime(task["TASK_DEADLINE"], "%d-%m-%Y")
                        diff = (deadline - now).days
                        print(diff)
                        if diff < -2:
                            # Auto-delete overdue task
                            tasks.remove(task)
                            usrtask[username] = tasks
                            saveTaskData()
                        if -1 <= diff <= 3:
                            reminders.append(
                                f"⚠️ Task: *{task['TASK_NAME']}*\nDeadline: *{task['TASK_DEADLINE']}*\nPriority: *{task['TASK_PRIORITY']}*"
                            )
                if reminders:
                    message = "⏰ *Reminder Task Mendekati Deadline:*\n\n" + "\n\n".join(reminders)
                    try:
                        await app.bot.send_message(chat_id=uid, text=message, parse_mode='Markdown')
                    except Exception as e:
                        print("Gagal mengirim pesan ke user:", e)

        await asyncio.sleep(60)  # cek setiap 1 menit

# Tambahkan ConversationHandler untuk delete_task
delete_conv = ConversationHandler(
    entry_points=[CommandHandler("deletetask", delete_task)],
    states={
        DELETE_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_response)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

        
conv = ConversationHandler(
    entry_points=[CommandHandler("addtask", add_taskName)],
    states={
        TASK_NAME : [MessageHandler(filters.TEXT & ~filters.COMMAND, add_taskDesc)],
        TASK_DESC : [MessageHandler(filters.TEXT & ~filters.COMMAND, add_taskDeadline)],
        TASK_DEADLINE : [MessageHandler(filters.TEXT & ~filters.COMMAND, add_taskPriority)],
        TASK_PRIORITY : [MessageHandler(filters.TEXT & ~filters.COMMAND, saveTask)]
    },
    fallbacks=[CommandHandler("cancel", cancel )]
    )     
        
app = ApplicationBuilder().token("7758310262:AAFZfDolpGpyVVauy6poLvELnlMMkbIzKHo").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_s))
app.add_handler(CommandHandler("su", sign_up))
app.add_handler(CommandHandler("si", sign_in))
app.add_handler(CommandHandler("so", sign_out))
app.add_handler(CommandHandler("viewtask", view_task))
app.add_handler(conv)
app.add_handler(delete_conv)

def run_reminder_loop():
    asyncio.run(reminder_job(app))
threading.Thread(target=run_reminder_loop, daemon=True).start()

app.run_polling()