from fastapi import FastAPI, Form
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pydantic import BaseModel 

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount('/static', StaticFiles(directory='static'), name='static')


# @app.post("/user/")
# async def files(
#                     request:           Request,
#                     username: str    = Form(...),
#                     password: str    = Form(...),
#                 ):
#     print('username', username)
#     print('password', password)
#     return templates.TemplateResponse(
#         'index.html', 
#         {
#             'request':  request,
#             'username': username,
#         }
#                                         )

@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse('init.html',{'request': request})


@app.get("/search",name='search_page')
async def main(request: Request):
    return templates.TemplateResponse('index.html',{'request': request})



@app.post("/main_page")
async def main_page(request:Request,speech_info: str = Form(...)):
    print('speech_info',speech_info)
    information = speech_info
    
    process_speech(information)
    
    # TODO .. another tasks...
    return templates.TemplateResponse('main_page.html',{'request': request,'information':information})

# process the speaker's speech
def process_speech(information):
    info = information.lower()
    if  "knowledge graph" in information.lower():
        return templates.TemplateResponse('kg.html',{'request': request,'information':information})
    # TODO ...获取说话者说的信息





# class Data(BaseModel):
#     sybmol: str

# @app.post("/result") 
# def get_res(input: Data):
#     print(input)
#     return input



@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse('init.html',{'request': request})


@app.get("/test")
async def main(request: Request):

    data = [
        {'url':'http://www.baidu.com', 'name':'northern cafe','rating':4.5,'price':'$$',
        'food':'boiled fish','location':'Lorenzo','related_tokens':'burger'
        ,},
         {'url':'http://fakeurl.com', 'name':'northern cafe','rating':3,'price':'$$',
        'food':'boiled fish','location':'Lorenzo','related_tokens':'burger'
        ,}
    ]
    
    
    return templates.TemplateResponse('result.html',{'request': request,'data':data})





if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)