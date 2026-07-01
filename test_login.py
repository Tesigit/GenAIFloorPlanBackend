import asyncio, traceback, os
from dotenv import load_dotenv
load_dotenv()
from app.db import get_db
async def t():
    try:
        db = get_db()
        print('DB returns:', type(db))
        print(await db['users'].find_one({'email': 'test'}))
    except Exception as e:
        with open('err.txt', 'w', encoding='utf-8') as f:
            traceback.print_exc(file=f)
asyncio.run(t())
