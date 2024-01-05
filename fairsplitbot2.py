import logging
from telegram.constants import ParseMode
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes, CallbackQueryHandler
from telegram.ext import MessageHandler, filters
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram import ForceReply
import re
from functions import *
from sql2 import *
import mysql.connector
from mysql.connector import Error






logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)






async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='''
🎉 Welcome to FairSplitBot! 🎉

Are you having troubles to split bills after a trip?
Say no more! With FairSplitlBot, all you need to do is:

1️⃣ Create your own username by /create_username  👾
2️⃣ Create a group name by /create_group or /join_group if your friend had already created one. 🧑👩
3️⃣ Add your own expenses to the the group by /add_expense 💸
                                   
Let us do the math and split the bill equally at end of the day! 🧮             
Enjoy hassle-free payments and more fun times with friends! 🥳
                                   
Check final bills by /split_bills   
                                   
Getting started: 
/create_username 
                                   
For any help or additional commands, type /help.''')
    user_id = update.effective_user.id
    try: 
        username = get_username(connection,user_id)
        group_id = get_user_current_group_id(connection,user_id)
        group_name = get_current_group_name(connection,user_id) 
        group_members = get_groupmates(connection,user_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {username}, your current group is {group_name}, your current groupmates are :{group_members} \nTo proceed: /add_expense /show_summary /show_my_transactions /split_bills \nIf you would like to change your current group: /update_group\nIf you would like to join new group: /join_group\nIf you would like to create new group: /create_group")
    except: 
        pass 

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)

    if update.message.text =='/help':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="""start - start using
create_username - create your username
create_group - create a new group name 
join_group - join an existing group
update_group - update your current group 
add_expense - add my expense to my group
add_expense_all - add expense for the whole group 
add_expense_one - add expense to individual of the group
delete_transaction - delete specific transaction
show_my_transactions - show my transactions 
show_summary - show summary of the group
split_bills - split the final bills of my group""")


async def command_create_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)

    if update.message.text =='/create_username':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the username you want to create:")
        context.user_data['current_state'] = 'create_username'



async def command_create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)
    username = get_username(connection,user_id)

    if update.message.text =='/create_group':
        if username == None: 
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please create a username first with /create_username.")
        else: 
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the group name you want to create:")
            context.user_data['current_state'] = 'create_group'
    
async def command_update_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)

    if update.message.text =='/update_group':
        group_names=get_users_groups(connection,user_id)
        output = '\n'.join(f"group_id: {group_id}, group_name: {group_name}" for group_id, group_name in group_names)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{output}\nEnter the numerical group id you want to change from above:\n(just the number of the group_id)")
        context.user_data['current_state'] = 'update_group'

async def join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)
    username = get_username(connection,user_id)
    
    if update.message.text =='/join_group':
        if username == None: 
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please create a username first with /create_username.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the group name you want to join:")
            context.user_data['current_state'] = 'join_group'

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)
    username = get_username(connection,user_id)

    if update.message.text =='/add_expense':
        if username == None: 
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please create a username first with /create_username.")
        else: 
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"/add_expense_all if the expense is shared by everyone \n/add_expense_one if one specific person owes you the expense")

async def add_expense_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state', None)

    if update.message.text == '/add_expense_all':
        # Ask for the amount first
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="How much did you pay? Please enter the amount (numerical value only):"
        )
        context.user_data['current_state'] = 'waiting_for_expense_amount'

async def add_expense_one (update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    groupmates = get_groupmates(connection,user_id)
    if len(groupmates) == 0: 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You do not have any group members.")



    
    
    # Create a custom keyboard with groupmate usernames
    keyboard = [[KeyboardButton(name)] for name in groupmates]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    # Send the message with the custom keyboard
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👤 Who did you pay for? Select a groupmate below",
        reply_markup=reply_markup
    )
    
    # Set the next step to handle the response
    context.user_data['current_state'] = 'waiting_for_groupmate_name'

async def show_my_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.effective_user.id
    username = get_username(connection,user_id)
    group_id = get_user_current_group_id(connection,user_id)
    group_name = get_current_group_name(connection,user_id) 
    transactions = get_all_transactions_for_user(connection, user_id, group_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"This is your {group_name} expense summary: \n\n{my_transactions(transactions,username)}\n\nYou may continue /add_expense or /delete_transaction or /show_summary  next.")

async def command_delete_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    current_state = context.user_data.get('current_state', None)
    user_id = update.effective_user.id
    username = get_username(connection,user_id)
    group_id = get_user_current_group_id(connection,user_id)
    group_name = get_current_group_name(connection,user_id)
    transactions = get_all_transactions_for_user(connection, user_id, group_id)
    if update.message.text == '/delete_transaction':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"This is your {group_name} expense summary: \n\n{my_transactions(transactions,username)}\n\nType the numerical ID of the transaction that you would like to delete:")
        context.user_data['current_state'] = 'delete_transaction'


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group_id = get_user_current_group_id(connection,user_id)
    print(group_id)
    group_name = get_current_group_name(connection,user_id)
    print(group_name)
    transactions = get_all_transactions_in_group(connection, group_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"This is {group_name} expense summary: \n\n{summary(transactions)}\n\nYou may continue /add_expense or /split_bills next.")

        

async def split_bills(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    group_id = get_user_current_group_id(connection,user_id)
    transactions = get_all_transactions_in_group(connection, group_id)
    dic = transaction_dic(transactions)
        # dic1 ={'A':100,"B":1000,"C":400,"D":300,"E":700}


    names = list(dic.keys())
    spent = list(dic.values())

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
        tolerance = 0.01
        while max(owe) > tolerance:  # while someone still owes something
            payer_index = owe.index(min(owe))
            payee_index = owe.index(max(owe))

            amount_to_transfer = min(-owe[payer_index], owe[payee_index])

            transactions.append((names[payer_index], names[payee_index], amount_to_transfer))
            owe[payer_index] += amount_to_transfer
            owe[payee_index] -= amount_to_transfer

        return transactions

    transactions = settle_debts(names, owe)
    transaction_messages = ""

    for transaction in transactions:
        payer, payee, amount = transaction
        transaction_messages += f"{payer} should transfer {round(amount, 1)} to {payee}.\n"

    # Send the combined transaction messages as a single message
    if transaction_messages:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=transaction_messages)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No transactions needed.")



async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_state = context.user_data.get('current_state', None)
    user_id = update.effective_user.id
    text = update.message.text 
    try: 

        if current_state == 'create_username':
            username = text
            try: 
                create_username(connection, user_id, username)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {username}, your username has been created. \nYou can now /create_group or /join_group.\nYou may /add_expense if you already in a group") 
                del context.user_data['current_state']  
                
            except: 
                username = get_username(connection,user_id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have already created a username: {username}.\nYou may /create_group or /join_group next.\nYou may /add_expense if you already in a group ")
                del context.user_data['current_state']



        elif current_state == 'create_group':
            groupname = text
            group_id = create_group_name(connection, groupname)
            add_user_to_group(connection, user_id, group_id)
            update_current_group(connection,user_id,group_id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Group '{groupname}' created. You are now a member. \nYou may /add_expense if you have incurred expense for the group.")
            del context.user_data['current_state'] 


        elif current_state == 'join_group':
            groupname = text
            group_id = list(get_group_id(connection, groupname)[0])[0]
            add_user_to_group(connection, user_id, group_id)
            update_current_group(connection,user_id,group_id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f" You are now a member of {groupname}. \nYou may /add_expense if you have incurred expense for the group.")
            del context.user_data['current_state']  

        elif current_state == 'update_group': 
            group_id = int(text) 
            update_current_group(connection,user_id,group_id)
            group_name = get_current_group_name(connection,user_id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f" You are now a member of {group_name}. \nYou may /add_expense if you have incurred expense for the group.")
            del context.user_data['current_state']  


        elif current_state == 'delete_transaction': 
            try:
                transaction_id = int(text)
                result = delete_transaction(connection, transaction_id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{result}\n\nYou may /add_expense or /show_my_transaction or /show_summary next.")
            except ValueError:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid transaction ID. Please enter a numerical ID.")
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {e}")
            finally:
                del context.user_data['current_state']
            

        elif current_state == 'waiting_for_groupmate_name':
            # Assuming the user has just sent the groupmate's name
            groupmate_name = text
            context.user_data['groupmate_name'] = groupmate_name  # Store the name
            context.user_data['current_state'] = 'waiting_for_expense_amount'  # Update state

            # Prompt user for the next piece of information
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Got it! You paid for {groupmate_name}. Now enter the amount you paid (numerical value only):"
            )
            

        elif current_state == 'waiting_for_expense_amount':
            # The user is now sending the expense amount
            try:
                expense_amount = float(text)  # Convert the text to a float
                context.user_data['expense_amount'] = expense_amount
                context.user_data['current_state'] = 'waiting_for_expense_description'  # Update state

                # Prompt user for the next piece of information
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="And what was the expense for? Please enter the description:"
                )
            except ValueError:
                # User didn't enter a valid number
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="That doesn't look like a number. Please enter the amount you paid as a number:"
                )


        elif current_state == 'waiting_for_expense_description': 
            text = update.message.text
            title = text 
            amount = context.user_data['expense_amount']
            user_id = update.effective_user.id
            user2 = context.user_data.get('groupmate_name', None)
            if user2 == None:
                user2_id = None 
            else: 
                user2_id = get_user_id(connection,user2)
            group_id = get_user_current_group_id(connection,user_id)
            group_name = get_current_group_name(connection,user_id)
            transaction_id = add_transaction(connection, title, amount, user_id, user2_id, group_id)
            if user2_id != None: 
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Added expense of {amount} to {user2} for {title} in group '{group_name}'. \nYou may continue /add_expense or /show_summary or /split_bills next.")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Added expense of {amount} for {title} to group '{group_name}'. \nYou may continue /add_expense or /show_summary or /split_bills next.")
            del context.user_data['current_state'] 
            del context.user_data['expense_amount']
            if user2 != None: 
                del context.user_data['groupmate_name']

    except ValueError as ve:
        # Handle incorrect number formats
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid number.")
        logger.error(f"ValueError: {ve}")

    except Exception as e:
        # Handle other exceptions
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Please try again.")
        logger.error(f"Exception: {e}")





if __name__ == '__main__':
    token_id = '6824458601:AAGrOOx8Vr1Wenm0mKQJnhGog2HhrK6min4'
    application = ApplicationBuilder().token(token_id).build()
    connection = create_connection_pool("mypool",5,"localhost", "root", '661063lt', 'EasySplit')
# connection = create_connection("mypool",5,"jackclx.mysql.pythonanywhere-services.com", "jackclx", '661063lt', 'jackclx$EasySplit') 

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler ('help',help)
    create_username_handler = CommandHandler('create_username',command_create_username)
    create_group_handler = CommandHandler('create_group', command_create_group)
    join_group_handler = CommandHandler('join_group', join_group)
    update_group_handler = CommandHandler('update_group', command_update_group)
    add_expense_handler = CommandHandler('add_expense', add_expense)
    show_my_transactions_handler = CommandHandler('show_my_transactions',show_my_transactions)
    delete_transaction_handler = CommandHandler('delete_transaction',command_delete_transaction)
    show_summary_handler = CommandHandler('show_summary', show_summary)
    split_bills_handler = CommandHandler('split_bills', split_bills)
    add_expense_all_handler = CommandHandler('add_expense_all', add_expense_all)
    add_expense_one_handler = CommandHandler('add_expense_one', add_expense_one)



    application.add_handler(start_handler)
    application.add_handler(create_username_handler)
    application.add_handler(create_group_handler)
    application.add_handler(join_group_handler)
    application.add_handler(update_group_handler)
    application.add_handler(add_expense_handler)
    application.add_handler(show_my_transactions_handler)
    application.add_handler(delete_transaction_handler)
    application.add_handler(show_summary_handler)
    application.add_handler(split_bills_handler)
    application.add_handler(add_expense_all_handler)
    application.add_handler(add_expense_one_handler)
    application.add_handler(help_handler)

    text_handler = MessageHandler(filters.TEXT, handle_text)
    application.add_handler(text_handler)
    
    application.run_polling()   