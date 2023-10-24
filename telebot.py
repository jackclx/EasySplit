import logging
from telegram.constants import ParseMode
from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
from telegram.ext import MessageHandler, filters
from telegram.ext import Updater
from telegram.ext import CallbackContext
token_id = '6824458601:AAGrOOx8Vr1Wenm0mKQJnhGog2HhrK6min4'



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Dictionary to store user expenses and group information
# user_expenses = {}
group_members = {}
username_dic = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='''
🎉 Welcome to EasySplitBot! 🎉

Are you having troubles to split bills after a trip?
Say no more! With EasySplitlBot, all you need to do is:

1️⃣ Create your own username by /create_username  💸
2️⃣ Create a group name by /create_group or /join_group if your friend created one. 🧑👩
3️⃣ Add your own expenses to the group by /add_expense <group_name>  <expenses in numbers> 
                                   
Let us do the math and split the bill equally at the end of the day! 🧮
Check final bills by /split_bills <group_name>

Getting started with examples: 
/create_username 
                                   
/create_group 
or /join_group (if the group has already been created)
/add_expense Japan 100
/add_expense Japan 200 
/show_summary Japan ( to view current group spending )
/split_bills Japan ( to view final bill split )

                                                              
                                  
Enjoy hassle-free payments and more fun times with friends! 🥳

For any help or additional commands, type /help.''')


async def create_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)
    print(current_state)

    if update.message.text =='/create_username':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the username you want to create:")
        context.user_data['current_state'] = 'waiting_for_username'
    elif current_state == 'waiting_for_username':
        username = update.message.text
        print(username)
        if username not in username_dic.values():  # Check username values, not keys
            username_dic[user_id] = username
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {username}, your username has been created. You can now /create_group or /join_group.")
            del context.user_data['current_state']  # Resetting the state here
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="This username has been taken. Try again.")


async def create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)
    print(current_state)

    if not username_dic.get(user_id):  # Check if user has created a username
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please create a username first with /create_username.")
        return

    if update.message.text == '/create_group':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the name of the group you want to create:")
        context.user_data['current_state'] = 'waiting_for_groupname'
    elif current_state == 'waiting_for_groupname':
        group_name = update.message.text
        print(group_name)
        if group_name not in group_members:
            group_members[group_name] = {user_id:0}
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Group '{group_name}' created. You are now a member.")
            del context.user_data['current_state']  # Resetting the state here
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="This group name has been taken. Try again.")

async def join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        group_name = context.args[0]
        user_id = update.effective_user.id
        
        if group_name in group_members:
            if user_id not in group_members[group_name]:
                group_members[group_name][user_id] = 0
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You joined group '{group_name}'.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Group '{group_name}' does not exist.")

    except (IndexError, ValueError):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Example Usage: /join_group Japan")

async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        group_name = context.args[0]
        user_id = update.effective_user.id
        group = group_members[group_name]
        total = sum(list(group.values()))
        summary = {username_dic[key]: group[key] for key in group}

        
        
        if group_name in group_members: 
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"This is {group_name} expense summary: '{summary}' with total spending: {total}.")

    except (IndexError, ValueError):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Example Usage: /show_summary Japan")


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 2 :
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Example Usage: /add_expense Japan 100")
            return

        group_name = context.args[0]
        expense = float(context.args[1])
        user_id = update.effective_user.id

        if group_name not in group_members:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Group not found. Please create the group using /create_group <group_name>")
        else:
            group = group_members[group_name]
            if user_id not in group:
                group[user_id] = 0
            else: 
                group[user_id] += expense
            print(group_members)

            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Added expense of {expense} to group '{group_name}'.")

    except (ValueError, TypeError):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Example Usage: /add_expense Japan 100")


async def split_bills(update:Update, context:ContextTypes.DEFAULT_TYPE):
    # dic1 ={'A':100,"B":1000,"C":400,"D":300,"E":700}
    group_name = context.args[0]
    user_id = update.effective_user.id
    group = group_members[group_name]

    names = list(group.keys())
    spent = list(group.values())

    # Step 1: Compute the total spent by all the friends.
    total = sum(spent)

    # Step 2: Determine the equal expense per person.
    expense_per_person = total / len(spent)

    # Step 3: Compute how much each person owes or gets owed.
    # Negative values mean they owe money, positive values mean they are owed money.
    owe = [i - expense_per_person for i in spent]

    # Step 4: Settle the debts.
    def settle_debts(names, owe):
        transactions = []
        while max(owe) != 0:  # while someone still owes something
            payer_index = owe.index(min(owe))
            payee_index = owe.index(max(owe))

            amount_to_transfer = min(-owe[payer_index], owe[payee_index])

            transactions.append((names[payer_index], names[payee_index], amount_to_transfer))
            owe[payer_index] += amount_to_transfer
            owe[payee_index] -= amount_to_transfer

        return transactions

    transactions = settle_debts(names, owe)
    # print(transactions)
    for transaction in transactions:
        payer, payee, amount = transaction
        payer = username_dic [payer]
        payee = username_dic [payee]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{payer} should transfer {amount} to {payee}.")
        # print(f"{payer} should transfer {amount} to {payee}.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(token_id).build()


    start_handler = CommandHandler('start', start)
    create_username_handler = CommandHandler('create_username',create_username)
    create_group_handler = CommandHandler('create_group', create_group)
    join_group_handler = CommandHandler('join_group', join_group)
    add_expense_handler = CommandHandler('add_expense', add_expense)
    show_summary_handler = CommandHandler('show_summary', show_summary)
    split_bills_handler = CommandHandler('split_bills', split_bills)

    username_text_handler = MessageHandler(filters.ALL, create_username)
    create_group_text_handler = MessageHandler(filters.ALL, create_group)
    join_group_text_handler = MessageHandler(filters.ALL, join_group)

    
    application.add_handler(start_handler)
    application.add_handler(create_username_handler)
    application.add_handler(create_group_handler)
    application.add_handler(join_group_handler)
    application.add_handler(add_expense_handler)
    application.add_handler(show_summary_handler)
    application.add_handler(split_bills_handler)

    application.add_handler(username_text_handler)
    application.add_handler(create_group_text_handler)
    application.add_handler(join_group_text_handler)
    
    application.run_polling()


