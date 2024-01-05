import re

def extract_amount(text):
    match = re.match(r'(\d+):', text)
    if match:
        return int(match.group(1))
    return None

def extract_title(text):
    # Extract title, assuming it's always before the last colon
    match = re.search(r':\s*(.*?)(?::\s*[\w\s]+)?$', text)
    if match:
        return match.group(1).strip()
    return None

def extract_name(text):
    # Check if there's a second colon, if yes, extract the name
    if text.count(':') > 1:
        match = re.search(r':\s*[\w\s]*:\s*(\w+)$', text)
        if match:
            return match.group(1).strip()
    return None

def my_transactions(transactions,user_name): 
    formatted_list = f"This is {user_name}'s transactions:\n"
    for transaction in transactions:
        id, item, amount, payer, payee = transaction
        if payer.lower() == user_name.lower():
            if payee:
                formatted_list += f"{id}. Paid {amount} for {item} for {payee}\n"
            else:
                formatted_list += f"{id}. {amount} for {item}\n"
        elif payee and payee.lower() == user_name.lower():
            formatted_list += f"{id}. Owe {payer} {amount} for {item}\n"
    return formatted_list

 

def summary(transactions): 
    total_expense = 0
    user_summary = {}

    for transaction in transactions:
        amount = transaction[2]  # Transaction amount
        item = transaction[1]    # Item description
        username1 = transaction[-2]  # created_by user
        username2 = transaction[-1]  # created_to user

        if username1 not in user_summary:
            user_summary[username1] = {'paid_for': [], 'owes': []}
        
        if username2:  # If created_to user exists
            if username2 not in user_summary:
                user_summary[username2] = {'paid_for': [], 'owes': []}
            user_summary[username1]['paid_for'].append(f"{amount} for {item} for {username2}")
            user_summary[username2]['owes'].append(f"{amount} for {item} to {username1}")
        else:
            user_summary[username1]['paid_for'].append(f"{amount} for {item}")

    # Update the processing to include total spent and owed per user
    output_lines = []
    for username, details in user_summary.items():
        total_paid = sum(float(amount.split(" for ")[0]) for amount in details['paid_for'])
        total_owed = sum(float(amount.split(" for ")[0]) for amount in details['owes'])
        total_expense += total_paid
        total_expense -= total_owed

        paid_items = ', '.join(details['paid_for'])
        owes_items = ', '.join(details['owes'])
        total_spent = total_paid - total_owed

        output_lines.append(f"{username} paid {paid_items}, owes {owes_items}, total spent {total_spent}")

    # Add the total expense incurred
    output_lines.append(f"Total expense incurred: {total_expense}")

    # Format the final output as a single string
    formatted_output = "\n\n".join(output_lines)
    return formatted_output

def transaction_dic(transactions):
    expense_dict = {}

    for _, _, amount, _, _,_, _, created_by_username, created_to_username in transactions:
        # Handling the user who created the transaction
        if created_by_username in expense_dict:
            expense_dict[created_by_username] += amount
        else:
            expense_dict[created_by_username] = amount

        # If there is a user to whom the transaction was created
        if created_to_username:
            # Reduce the receiver's total by the amount
            if created_to_username in expense_dict:
                expense_dict[created_to_username] -= amount
            else:
                # In case the receiver is not yet in the dictionary, we initialize with a negative value
                expense_dict[created_to_username] = -amount

    # No need to reformat the dictionary, just return it
    return expense_dict
    