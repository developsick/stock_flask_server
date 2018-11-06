import pandas as pd
from slacker import Slacker
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'hello world'


@app.route('/stock/<name>/token/<token>')
def getStockInfo(name, token):
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    code_df.head()

    if name == "":
        name = '신라젠'
    item_name = name
    url = get_url(item_name, code_df)
    df = pd.DataFrame()
    for page in range(1, 21):
        pg_url = '{url}&page={page}'.format(url=url, page=page)

    df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)
    df = df.dropna()
    
    #token은 직접 코드에 입력할 경우 slack에서 해당 token을 deactivate시킴
    print(token)
    slack = Slacker(token)
    slack.chat.post_message('#test', item_name + '\n' + df.head().to_string())

    return item_name + '\n' + " data sent to slack"


def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    # print("요청 URL = {}".format(url)) 
    return url


if __name__ == '__main__':
    app.run(port='5001', debug='true')