import os, sys, requests, time, json, httpx, asyncio
import re
from typing import List, Optional
from colorama import Fore, init
from requests.exceptions import ConnectionError

host = 'http://localhost:8000'

import os
import sys

init(autoreset=True)

TOKEN_FILE = "temp_storage.json"
current_token = None

trial_creds = {
    1: {'username': 'assmeblycoder', 'password': 'CoderOfWorld2003'},
    2: {'username': 'lifeofcoding', 'password': 'Code2003BecomesPower'},
    3: {'username': 'javascriptcoder', 'password': 'CodeJStill2025'},
    4: {'username': 'pythoncoder', 'password': '2003LifeWithPython'},
    5: {'username': 'AI-Agent-coder', 'password': '2003LifeWithAI'},
    6: {'username': 'ServerSideDev', 'password': '2003LifeWithTech'},
    7: {'username': 'lifewithnetwork', 'password': '2003LifeWithTech'},
    8: {'username': 'lifewithDNS', 'password': '2003LifeWithTech'},
    9: {'username': 'lifewithOpenVPN', 'password': '2003LifeWithTech'},
}

login_tokens = {}

trials_fetched = False

def save_token(data: dict):
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary.")
    
    with open(TOKEN_FILE, "w") as file:
        json.dump(data, file)
    print(f"\nToken saved: {data.get('access_token')}")


def get_token() -> str | None:
    if not os.path.exists(TOKEN_FILE):
        return None

    with open(TOKEN_FILE, "r") as file:
        data = json.load(file)

    return data.get("access_token", None)

def clear_terminal() -> None:
    try:
        os.system("clear")
    except Exception:
        sys.stdout.write("\033c")
        sys.stdout.flush()

def register_or_login():
    print(Fore.GREEN + 'Preparing tokens to test concurrency...')
    success_rate = 0
    for key, cred in trial_creds.items():
        create_res = requests.post(
            f"{host}/create_user",
            json=cred
        )

        if not (create_res.status_code in [200, 409]):
            clear_terminal()
            print(Fore.RED+f"\nUnexpected error during registration: {create_res.status_code}, {create_res.text}")
            continue 

        login_res = requests.post(
            f"{host}/login",
            json=cred
        )
        if login_res.status_code == 200:
            token = login_res.json().get("access_token")
            login_tokens[key] = token
            success_rate += 1
        else:
            clear_terminal()
            print(Fore.RED+f"   Login failed: {login_res.status_code}, {login_res.text}")
        time.sleep(1)

    if len(trial_creds.keys()) <= success_rate:
        global trials_fetched
        trials_fetched = True

async def ConcurrentReq():
    message = input(Fore.YELLOW+'\nMessage to AI: '+Fore.WHITE)
    clear_terminal()
    if not trials_fetched:  register_or_login()
    token1 = get_token()
    token2 = login_tokens.get(1)
    token3 = login_tokens.get(2)
    token4 = login_tokens.get(3)
    token5 = login_tokens.get(4)
    token6 = login_tokens.get(5)
    token7 = login_tokens.get(6)
    token8 = login_tokens.get(7)
    token9 = login_tokens.get(8)
    token10 = login_tokens.get(9)
    clear_terminal()
    request_count = len(login_tokens.keys())
    if token1: request_count += 1
    print(Fore.GREEN + f'Fetching {request_count} responses')
    start = time.time()
    async with httpx.AsyncClient(timeout=10) as client:
        request1 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        request2 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token2}"}
        )

        request3 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token3}"}
        )

        request4 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token4}"}
        )

        request5 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token5}"}
        )

        request6 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token6}"}
        )

        request7 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token7}"}
        )
        request8 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token8}"}
        )

        request9 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token9}"}
        )
        request10 = client.post(
            f"{host}/support",
            json={'message': message},
            headers={"Authorization": f"Bearer {token10}"}
        )
        
        # Run ALL requests concurrently
        r1, r2, r3, r4, r5, r6, r7, r8, r9, r10 = await asyncio.gather(
            request1, 
            request2, 
            request3, 
            request4, 
            request5, 
            request6, 
            request7, 
            request8, 
            request9,
            request10
        )
        clear_terminal()
        print(Fore.GREEN+"\nFirst Response:", f'\n\n {r1.json().get('answer')}' if r1.status_code == 200 else Fore.YELLOW+str(r1.status_code))
        print(Fore.GREEN+"\nSecond Response:",f'\n\n {r2.json().get('answer')}' if r2.status_code == 200 else Fore.YELLOW+str(r2.status_code))
        print(Fore.GREEN+"\nThird Response:", f'\n\n {r3.json().get('answer')}' if r3.status_code == 200 else Fore.YELLOW+str(r3.status_code))
        print(Fore.GREEN+"\nFourth Response:",f'\n\n {r4.json().get('answer')}' if r4.status_code == 200 else Fore.YELLOW+str(r4.status_code))
        print(Fore.GREEN+"\nFifth Response:", f'\n\n {r5.json().get('answer')}' if r5.status_code == 200 else Fore.YELLOW+str(r5.status_code))
        print(Fore.GREEN+"\n6th Response:", f'\n\n {r6.json().get('answer')}' if r6.status_code == 200 else Fore.YELLOW+str(r6.status_code))
        print(Fore.GREEN+"\n7th Response:", f'\n\n {r7.json().get('answer')}' if r7.status_code == 200 else Fore.YELLOW+str(r7.status_code))
        print(Fore.GREEN+"\n8th Response:", f'\n\n {r8.json().get('answer')}' if r8.status_code == 200 else Fore.YELLOW+str(r8.status_code))
        print(Fore.GREEN+"\n9th Response:", f'\n\n {r9.json().get('answer')}' if r9.status_code == 200 else Fore.YELLOW+str(r9.status_code))
        print(Fore.GREEN+"\n10th Response:", f'\n\n {r10.json().get('answer')}' if r10.status_code == 200 else Fore.YELLOW+str(r10.status_code))
        
        end = time.time()
        elapsed = end - start
        print(Fore.MAGENTA +f"\nTook {elapsed:.2f} seconds for all {request_count} responses")
        await ConcurrentReq()


def checkConcurrency():
    asyncio.run(ConcurrentReq())


def testCreate(username, password):
    url = host + '/create_user'
    request = requests.post(url, json={'username': username, 'password': password})
    response = request.json()
    if request.status_code in [200, 201]:
        print('User created successfully !')
        print(f'Username: {response.get('username')}')
        print('\nPress Ctrl+C to main menu')
    else: 
        clear_terminal()
        print('User registration failed\n')
        print('Error:\n\n')
        print(response)
        print('\nPress Ctrl+C to main menu')


def testLogin(username, password):
    url = host + '/login'
    request = requests.post(url, json={'username': username, 'password': password})
    response = request.json()
    if request.status_code in [200, 201]:
        print(Fore.GREEN+'Logged in successfully !')
        print(Fore.GREEN+f'Response token:\n    ', Fore.WHITE+response.get('access_token'))
        token = response.get('access_token')
        if token:
            global current_token
            current_token = token 
            save_token(response)
        print(Fore.GREEN + '\nPress Ctrl+C to main menu')
        time.sleep(5)
        return current_token
    else: 
        clear_terminal()
        print('login failed')
        print('Error:\n\n')
        print(response)
        print('\nPress Ctrl+C to main menu')

def productListLayout(products: list):
    processed = []
    for each in products:
        id = each.get('id')
        name = each.get('name')
        price = each.get('price')
        processed.append(f'\n{name}\n\n    ID: {id}    \n    Price: {price}\n')
    return ''.join(processed)

def timesLine(x):
    lines = []
    for line in range(max(min(x, 1), 3)):  
        lines.append('\n')
    return ''.join(lines)

def productListStruct(data: list[dict]):
    structure = ''
    for times in range(len(data)):
        each_purchase = data[times]
        purchase_id = each_purchase.get('id', '')
        purchase_status = each_purchase.get('fulfillment_stage', 'Status Not Available')
        layout = f'{timesLine(times)}Info on purchase ID: {purchase_id}:\n'
        products = each_purchase.get('purchased_products', [])
        structure += layout + productListLayout(products) + f'\nOrder Status: {purchase_status}'
    return structure

def testListProduct(restart, quick=False):
    url = host + '/user_purchases'
    request = requests.get(url, headers={'Authorization': f'Bearer {current_token}'})
    response = request.json()
    if request.status_code in [401]:
        clear_terminal()
        print('\n\n    Authentication failed!')
        time.sleep(1)
        restart()
    if request.status_code in [200, 201]:
        clear_terminal()
        if response: print(productListStruct(response))
        else: print(Fore.RED  + '\n   No purchases found so far!')
        print(Fore.GREEN + '\nPress Ctrl+C to main menu')
        if not quick: time.sleep(12)
        return response
    else: 
        clear_terminal()
        print('login failed')
        print('Error:\n\n')
        print(response)
        print('\nPress Ctrl+C to main menu')

def extract_id(data: str) -> Optional[List[int]]:
    try:
        number_strings = re.findall(r'\d+', data)
        return [int(s) for s in number_strings]
    except Exception:
        return None

def testOrderCreation():
    url = host + '/products'
    request = requests.get(url)
    if request.status_code in [200, 201]:
        response = request.json()
        clear_terminal()
        if response:
            print(f'''
                \nHere are the products to choose from:\n\n{productListLayout(response)} {Fore.YELLOW + '\n\nMake sure to add commas between ids to includes more products\n\n'}
            ''')
            product_requested = None
            while not product_requested:
                product_requested = extract_id(input('Products: '))
                if product_requested: break
            
            request = requests.post(
                host + '/register_purchase', 
                json={'products': product_requested},
                headers={'Authorization': f'Bearer {current_token}'}
            )
            if request.status_code in [200, 201]:
                clear_terminal()
                print('\n   Purchase created!')
                print('\nPress Ctrl+C to main menu')
                time.sleep(5)
            else:
                print('\n   Purchase was not created!')
                time.sleep(2)

        else: 
            print(Fore.RED + '\n No Products Found in DB!\n')
            print(Fore.GREEN + '\nPress Ctrl+C to main menu')

def testStatusSet():
    order_id = input('Enter purchase ID: ')
    if order_id:
        clear_terminal()
        print('\n1: processing\n2: on the way\n3: delivered\n')
        status_requested = input('\nPick status to set the purchase to: ')
        if status_requested:
            url = host + f'/update_order_status/{order_id}'
            request = requests.post(
                url, 
                json={'status_index': status_requested},
            )
            clear_terminal()
            if request.status_code in [200, 201]:
                print('\n   Order status changed!')
                time.sleep(1)
            else: 
                time.sleep(1)
                print(Fore.RED + '\n   Order status was not changed!\n')
                print(Fore.RED + '   Likely wrong order number!')
                print(Fore.GREEN + '\nPress Ctrl+C to main menu')
        else:
            clear_terminal()
            print('failed!')

def testCreateProduct():
    name = input('\nProduct name: ')
    price = input('Product price: ')
    clear_terminal()
    try:
        price = float(price)
    except ValueError as error: 
        print('Enter valid price!')
        time.sleep(1)
        testCreateProduct()
    url = host+'/create_product'
    request = requests.post(url, json={'name': name, 'price': price})
    clear_terminal()
    if request.status_code in [200, 201]:
        print('\n\nProduct Created!\n')
        print('\nPress Ctrl+C to main menu')
        time.sleep(1)
    else: 
        print('\n\nCreation Failed!\n')
        time.sleep(1)

def testAI(message=None):
    def get_message(): return input('ask AI: ')
    msg = get_message() if not message else message
    url = host + '/support'
    try:
        request = requests.post(
            url, 
            json={'message': msg.strip()},
            headers={'Authorization': f'Bearer {current_token}'}
        )
        if request.status_code in [200, 201]:
            response = request.json()
            clear_terminal()
            print(f'\n{response.get('answer', 'No Answer')}\n')
            msg = get_message()
            testAI(msg)
        else:
            print('\nRequest failed, likely not logged in!')
            print('\nPress Ctrl+C to main menu')
            time.sleep(2)
    except Exception as error:
        print(error)
        print('\nPress Ctrl+C to main menu')
        time.sleep(3)

def testAuth(trial=False, instruct=True):
    url = host + '/myprofile'
    request = requests.get(url, headers={'Authorization': f'Bearer {current_token}'})
    response = request.json()
    if request.status_code in [200, 201]:
        username = response.get('username')
        id = response.get('id')
        print('Profile fetched in successfully !')
        print(f'Username: {username}\nId: {id}')
        if instruct: print(Fore.GREEN + '\nPress Ctrl+C to main menu')
        return username, True
    else:  
        if not trial:
            clear_terminal()
            print('Authentication failed\n')
            print('Error:\n\n')
            print(response)
            print('\nPress Ctrl+C to main menu')
            return None, False
    return None, False

def runTest():
    cancelled = 0
    global current_token
    current_token = get_token()
    while True:
        clear_terminal()
        username, loggedin = testAuth(True, False)
        try:
            if loggedin:
                print(f'Currently Logged in as: {username}')
            action = input(f'''
                \nActions to perform:\n{Fore.RED + "Not Logged In!" if not loggedin else '\n'}   
                1: Create User Account\n   
                2: Login with credentials\n   
                3: Check authentication status\n
                4: Create products in DB\n  
                5: Check purchased products\n
                6: Place order\n  
                7: Change order status\n       
                8: Chat AI-support\n 
                9: Check AI concurrency\n                            \n\n\nYour choice: ''')


            action_indecies = {
                1: testCreate,
                2: testLogin,
                3: testAuth,
                4: testCreateProduct,
                5: testListProduct,
                6: testOrderCreation,
                7: testStatusSet,
                8: testAI,
                9: checkConcurrency
            }

            action_id = int(action)
            perform = action_indecies[action_id]
            cancelled = 0
            if action_id in [1, 2]:
                username = input('Enter your username: ')
                password = input('Enter your password: ')
                username = username.strip()
                password = password.strip()
                perform(username, password)
                time.sleep(5)

            elif action_id in [5]:
                perform(runTest)
                time.sleep(3)
            else:
                perform()
                time.sleep(5)
        except:
            cancelled += 1
            print(f'test stopped, terminating...')
            if cancelled > 3: break

if __name__ == '__main__':
    try:
        runTest()
    except ConnectionError as error:
        clear_terminal()
        print(Fore.RED+'\nServer did not respond!')
        print(Fore.YELLOW+'\nRun the server first!')
        print(Fore.YELLOW+'\nHow ?\n\n     uvicorn project.main:app --workers 2')
        print(Fore.RED+'\nTerminating....\n')