import streamlit as st
import random
import requests
import pandas as pd
from config import config
import os
from db import get_connection
from dotenv import load_dotenv 
load_dotenv()
from PIL import Image
import json
import time
img = Image.open('api/logo.png')

st.set_page_config(page_title='group3 chatbot', page_icon=img)

user_dict = {
    'Biden' : 1,
    'Putin' : 2,
    'Sachin' : 3
}

backend_ip = os.getenv("backend_ip")
backend_port = os.getenv("backend_port")
#use_sql = config.app_config.use_sql
use_sql = os.getenv("use_sql")
use_sql = use_sql == "True"

if ('session_id' not in st.session_state):
    st.session_state['session_id'] = random.randint(0, 10e5)

if use_sql:
    engine = get_connection()
    conn = engine.connect()

if "messages" not in st.session_state.keys():
        st.session_state.messages = []
        
def get_user_id():
    if ('user_id' not in st.session_state):
        st.session_state['user_id'] = None
        
    if st.session_state['user_id'] == None:
        user = st.selectbox(
        "Please select a user",
        (None, "Biden", "Putin", "Sachin"))
        
        if user != None:
            
            st.session_state['user_id'] = user_dict[user]
            st.session_state.messages.append({"role": "assistant", "content": f'You have selected {user}. Now please provide me order id or describe the product that you want help with.'})
            
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
               
                    
get_user_id()
        
def runllm_through_args(*args):
    runllms(args[0])
    
def call_before_llm2(msg, user_selected_product):
    
    st.session_state["user_selected_product"] = user_selected_product
    st.session_state.messages.append({"role": "user", "content": msg})
    st.session_state.messages.append({"role": "assistant", "content": 'Tell me how I can help you with this product'})
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
def call_before_session_end(*args):
    selection = args[0]
    if selection == 'different_product':
        st.session_state["user_selected_product"] = None
        st.session_state.messages.append({"role": "user", "content": 'I need help with some other product'})
        st.session_state.messages.append({"role": "assistant", "content": 'Please describe the product you want help with'})           
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
    elif selection == 'same_product':
        st.session_state.messages.append({"role": "user", "content": 'I need more support on same product'})
        st.session_state.messages.append({"role": "assistant", "content": 'Please tell me how I can help with this order'})           
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
    elif selection == 'session_end':
        st.session_state["user_selected_product"] = None
        st.session_state.messages.append({"role": "user", "content": 'My queries are solved'})
        st.session_state.messages.append({"role": "assistant", "content": 'Thank you for talking to me, Have a great day!'})           
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
    elif selection == 'need_human_help':
        st.session_state.messages.append({"role": "user", "content": 'I am not happy, I want to connect with a human agent'})
        st.session_state.messages.append({"role": "assistant", "content": 'One of our attendent will join the chat soon, please wait'})           
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"]) 
                
def function_call_confirmation(function_to_call, confirmation):
    
    t = time.time()
    try:
        response = requests.get(f'{backend_ip}:{backend_port}/backend_call', params={'USER_ID': st.session_state.get('user_id'),
                                                                'text' : 'None',
                                                                'user_selected_product' : st.session_state.get("user_selected_product"),
                                                                'user_confirmation' : confirmation,
                                                                'func_to_call' : function_to_call
                                                                })
    
        response = response.json()
    except:
        response = {'error': 'api did not respond'}
    
    response['session_id'] = st.session_state['session_id']
    response['time_taken'] = time.time() - t
    with open('api_responses.json', 'a') as outfile:
        json.dump(response, outfile)
        outfile.write('\n')
    
    msg = response.get('message', 'I am sorry I could not understand')
    resp_type = response.get('resp_type', None)
    if resp_type == 'tool_msg':
        st.session_state.messages.append({"role": "assistant", "content": msg})
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        st.button(f'I need more support on same product', on_click=call_before_session_end, args=(['same_product']))
        st.button(f'I need help with some other product', on_click=call_before_session_end, args=(['different_product']))
        st.button(f'My queries are solved', on_click=call_before_session_end, args=(['session_end']))
        st.button(f'I am not happy, I want to connect with a human agent', on_click=call_before_session_end, args=(['need_human_help']))
    else:
        st.session_state.messages.append({"role": "assistant", "content": msg})
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
            
                
def runllms(chat):
    USER_ID = st.session_state['user_id']
    st.session_state.messages.append({"role": "user", "content": chat})
    t = time.time()
    try:
        response = requests.get(f'{backend_ip}:{backend_port}/backend_call', params={'USER_ID': USER_ID,
                                                                    'text' : chat,
                                                                    'user_selected_product' : st.session_state.get("user_selected_product"),
                                                                    'user_confirmation' : st.session_state.get("user_confirmation"),
                                                                    'func_to_call' : st.session_state.get("user_confirmation")
                                                                    })
        response = response.json()
    except:
        response = {'error': 'api did not respond'}
    
    response['session_id'] = st.session_state['session_id']
    response['time_taken'] = time.time() - t
    with open('api_responses.json', 'a') as outfile:
        json.dump(response, outfile)
        outfile.write('\n')
        
    msg = response.get('message', 'I am sorry I could not understand')
    order_ids = response.get('orders', [])
    resp_type = response.get('resp_type', '')
    function_to_call = response.get('function_to_call', '')
    
    
    if len(order_ids) > 0:
        if config.app_config.use_sql:
            user_products = pd.read_sql(f"SELECT * FROM user_products WHERE user_id = {USER_ID} AND order_id IN {tuple(order_ids + order_ids)}", conn)
        else:
            user_products = pd.read_csv('../user_products.csv')
        
        user_products = user_products[(user_products.user_id == int(USER_ID)) & (user_products.order_id.isin(order_ids))]

        st.session_state.messages.append({"role": "assistant", "content": msg})
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        
        for u in range(len(user_products)):
            order_id = user_products['order_id'].iloc[u]
            description = user_products['description'].iloc[u]
            purchased_at = str(user_products['purchased_at'].iloc[u])
            st.button(f'{description} purchased on {str(purchased_at)}', on_click=call_before_llm2, args=([f'Selected {description} purchased on {str(purchased_at)}', order_id]))
    
    elif resp_type == 'tool_msg':
        
        st.session_state.messages.append({"role": "assistant", "content": msg})
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        st.button(f'I need more support on same product', on_click=call_before_session_end, args=(['same_product']))
        st.button(f'I need help with some other product', on_click=call_before_session_end, args=(['different_product']))
        st.button(f'My queries are solved', on_click=call_before_session_end, args=(['session_end']))
        st.button(f'I am not happy, I want to connect with a human agent', on_click=call_before_session_end, args=(['need_human_help']))
                  
    elif (resp_type == 'get_cofirmation') & (function_to_call in ['CancelOrder', 'ReturnOrder', 'ReplaceOrder']):
            if function_to_call == 'CancelOrder':
                msg = 'Please confirm if you want to cancel this order.'
                st.session_state.messages.append({"role": "assistant", "content": msg})
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                        
                st.button(f'Yes I want to cancel product {st.session_state.get("user_selected_product")}', on_click=function_call_confirmation, args=([function_to_call, 'true']))
                st.button(f'No I dont want to cancel it', on_click=function_call_confirmation, args=([function_to_call, 'false']))
                
            
            if function_to_call == 'ReturnOrder':
                msg = 'Please confirm if you want to return this order'
                st.session_state.messages.append({"role": "assistant", "content": msg})
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                        
                st.button(f'Yes I want to return product {st.session_state.get("user_selected_product")}', on_click=function_call_confirmation, args=([function_to_call, 'true']))
                st.button(f'No I dont want to return it', on_click=function_call_confirmation, args=([function_to_call, 'false']))
                
        
            if function_to_call == 'ReplaceOrder':
                msg = 'Please confirm if you want to replace this order'
                st.session_state.messages.append({"role": "assistant", "content": msg})
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                        
                st.button(f'Yes I want to return product {st.session_state.get("user_selected_product")}', on_click=function_call_confirmation, args=([function_to_call, 'true']))
                st.button(f'No I dont want to return it', on_click=function_call_confirmation, args=([function_to_call, 'false']))
    else:
        st.session_state.messages.append({"role": "assistant", "content": msg})
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])    
            


if prompt := st.chat_input():
    runllms(prompt)
        
    


