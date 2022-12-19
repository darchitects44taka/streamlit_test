import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import nlplot
import plotly
from plotly.subplots import make_subplots
from plotly.offline import iplot
import matplotlib.pyplot as plt

st.title('Review Analysis')

#準備作業
get_data = []
page_count = range(0,5000,20)

#scraiping
for page in page_count:

  # 1ページデータ取得
  url = f'https://review.travel.rakuten.co.jp/hotel/voice/50253/?f_time=&f_keyword=&f_age=0&f_sex=0&f_mem1=0&f_mem2=0&f_mem3=0&f_mem4=0&f_mem5=0&f_teikei=&f_version=2&f_static=1&f_point=0&f_sort=0&f_next={page}'
  res = requests.get(url)
  soup = BeautifulSoup(res.text, 'html.parser')
  comments = soup.find_all('div', attrs={'class': 'commentBox'})

  # データなしで終了する
  if comments == []:
    break

  # １件づつデータ取得
  for comment in comments:

    result = comment.find('p', attrs={'class', 'commentRate'})
    # レート
    if result is None:
      # データが無い場合はZeroを格納する
      rate = 0
    else:
      rate = float(comment.find('span').text)
    # 口コミ
    review = comment.find('p', attrs={'class': 'commentSentence'})
    review = review.text.replace('\r\n', '').lstrip()

    info = comment.find('dl', attrs={'class': 'commentPurpose'})
    titles = info.find_all('dt')
    contents = info.find_all('dd')

    # データ格納
    details = {}
    details['rate'] = rate
    details['review'] = review
    get_data.append(details)

df = pd.DataFrame(get_data)

#WordCloud作成
for i in range(0,6):
    df_late = df[df['rate'] == i]
    npt = nlplot.NLPlot(df_late, target_col='review')
    stopwords = npt.get_stopword(top_n=0, min_freq=0)
    st.write(f'総合レート{i}')
    fig_wc = npt.wordcloud(
        width=1000,
        height=600,
        max_words=100,
        max_font_size=100,
        colormap='tab20_r',
        stopwords=stopwords,
        mask_file=None,
        save=False
    )
    plt.figure(figsize=(15, 25))
    plt.imshow(fig_wc, interpolation="bilinear")
    plt.axis("off")
    st.pyplot()
