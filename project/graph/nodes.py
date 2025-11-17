import httpx
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, ToolMessage
from langchain_core.messages.base import messages_to_dict
from langchain_core.messages.utils import messages_from_dict
from langgraph.graph import END
from typing import Any, Optional
from dotenv import load_dotenv
from .state import SupportState
from openai import OpenAIError
from colorama import Fore, init

init(autoreset=True)


host = 'http://127.0.0.1:8000'
load_dotenv()

policies = {
    'return_&_refund': '''
        \n Return & Refund Policy \n
        Customers may return any laptop within 30 days of purchase for a full refund, provided it is in original condition with all packaging and accessories.
        Items with physical damage or missing components are not eligible for return unless reported within 7 days of delivery.
        Sale or clearance items are non-refundable.\n
    ''',
    
    'warranty_&_repairs': '''
        \n Warranty & Repairs Policy \n
        All laptops come with a 1-year limited hardware warranty covering manufacturing defects.
        Issues caused by accidental damage, liquid spills, or unauthorized repairs are not covered.
        Customers can request a warranty service or paid repair through our support portal.\n
    ''',

    'shipping_&_delivery': '''
        \n Shipping & Delivery Policy \n
        Orders are processed within 1–3 business days after payment confirmation.
        Standard shipping takes 3–5 business days within the country.
        Customers receive a tracking link via email once the item is shipped.
        Delays caused by courier services, weather, or incorrect addresses are beyond our control.
    ''',
}

def outputKeyError(invalid=False):
    if not invalid: print(Fore.RED  + '\nOPENAI_API_KEY variable was not found!')
    else: print(Fore.RED  + '\nOPENAI_API_KEY provided is invalid!')
    print(Fore.RED  + 'Place valid LLM key as OPENAI_API_KEY = "_key_" in .env file inside /graph folder!\n')
    print(Fore.YELLOW+'\nif using anthropic: ANTHROPIC_API_KEY = "_key_"')
    print(Fore.YELLOW+'or\nif using gemini: GOOGLE_API_KEY = "_key_"')

def productListLayout(products: list):
    processed = []
    for index in range(len(products)):
        each = products[index]
        name = each.get('name')
        price = each.get('price')
        processed.append(f'\n{index+1}: {name}\n\n    \n    Price: {price}\n')
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
        layout = f'{timesLine(times)}Info on purchase ID: {purchase_id}\n'
        products = each_purchase.get('purchased_products', [])
        structure += layout + productListLayout(products) + f'\n\nOrder Status: {purchase_status}'
    return structure

async def makeRequest(endpoint: str, req_type: str, data: Optional[Any] = None):
    its_post = req_type.upper() == 'POST'
    url = f"{host}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if its_post:
                post_data = data or {}
                response = await client.post(url, json=post_data)
            else:
                response = await client.get(url, params=data if data else None)

            success = response.status_code in [200, 201]
            result = response.json()
            return success, result

    except Exception as error:
        print(f"[makeRequest] Error: {error}")
        return False, None

def prepare_all(policies: dict) -> str:
    return " \n".join(p.strip() for p in policies.values())

@tool
async def getOrderStatus(order_id: int):
    ''' A tool that accepts order id based on which returns the status of the order '''
    success, response = await makeRequest(f'/purchase/{order_id}', 'GET')
    if success:
        return productListStruct([response])
    return f'Order with ID {order_id} was not found.'

@tool
async def getAllProducts(*args, **kwargs):
    ''' A tool that provides user with all available products '''
    success, response = await makeRequest(f'/products', 'GET')
    if success:
        return productListLayout(response)
    else: 
        return f'Currently this information unavailable\nSorry.'

@tool
async def getPolicy(topic: str) -> str:
    """Fetch policy details based on topic: 'return', 'warranty', or 'shipping'."""
    topic = topic.lower()
    category = ''
    if "return" in topic or "refund" in topic: category  = 'return_&_refund'

    elif "warranty" in topic or "repair" in topic: category  = 'warranty_&_repairs'

    elif "shipping" in topic or "delivery" in topic: category  = 'shipping_&_delivery'
    
    return policies.get(category, prepare_all(policies))


all_tools = [getOrderStatus, getAllProducts, getPolicy]
llm = {}
try:
    llm = init_chat_model("openai:gpt-4o-mini",  temperature=0.5)
    llm = llm.bind_tools(all_tools)
except OpenAIError as error:
    outputKeyError()


async def connect_node(state: SupportState) -> SupportState:
    sys_msg = [
        SystemMessage(content=(
            "You are a professional customer support agent that speaks english, uzbek and russian. you can: check order statuses, suggest products or list all products etc.."
            "ONLY respond to questions that are relevant. "
            "If the user asks anything irrelevant, respond politely that you cannot answer it."
            "your default language is english."
        ))
    ]
    msgs_so_far = state.get('messages', [])
    calls_so_far = state.get('calls', 0) + 1
    processed_context = messages_from_dict(msgs_so_far)
    ai_request = sys_msg + processed_context
    response = await llm.ainvoke(ai_request)
    final_state = messages_to_dict([response])
    return {'messages': final_state, 'calls': calls_so_far}


# tool node that determines if tool was requested, if so, renders all requested tools and returns as an updated state
async def tool_node(state: SupportState) -> SupportState:
    last_msg = getLastMessage(state)
    res_type = last_msg.get('type', None) if last_msg else False
    ai_message = res_type == 'ai'
    tools = toolsCalled(last_msg)
    calls_so_far = state.get('calls', 0)
    outputs = []
    if ai_message and tools:
        tool_options = getTools()
        for each_tool in tools:
            tool_name = each_tool.get('name')
            arguments = each_tool.get('args', {})
            call_id = each_tool.get('id')
            requested_tool = tool_options.get(tool_name, None)
            try:
                if requested_tool:
                    tool_output = await requested_tool.ainvoke(arguments)
                    tool_message = ToolMessage(content=tool_output, tool_call_id=call_id)
                    outputs.append(tool_message)
            except Exception as error: 
                print(error)
                continue
    return {'messages': messages_to_dict(outputs), 'calls': calls_so_far}

def getLastMessage(state: SupportState) -> dict:
    message = state.get('messages', [None])[-1]
    return message

def getTools() -> dict:
    return {t.name: t for t in all_tools}

def toolsCalled(message: dict) -> list:
    response_data = message.get('data', {})
    tools = response_data.get('tool_calls', [])
    return tools

def determine_next(state: SupportState):
    last = getLastMessage(state)
    if last:
        toolsRequested = toolsCalled(last)
        if toolsRequested:
            return 'tool_node'
    return END