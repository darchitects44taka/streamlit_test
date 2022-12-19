import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import nlplot
#import plotly
#from plotly.subplots import make_subplots
#from plotly.offline import iplot
import matplotlib.pyplot as plt

# scraiping
@st.cache
def get_scraipingdata(page_count):
    get_data = []

    for page in page_count:
    # getdata(loop_page)
        url = f'https://review.travel.rakuten.co.jp/hotel/voice/50253/?f_time=&f_keyword=&f_age=0&f_sex=0&f_mem1=0&f_mem2=0&f_mem3=0&f_mem4=0&f_mem5=0&f_teikei=&f_version=2&f_static=1&f_point=0&f_sort=0&f_next={page}'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        comments = soup.find_all('div', attrs={'class': 'commentBox'})

        # nodata -> break
        if comments == []:
            break

        # GetData(loop_data) ※maxdata:20
        for comment in comments:
            result = comment.find('p', attrs={'class', 'commentRate'})
            # Rate
            if result is None:
                rate = 0
            else:
                rate = float(comment.find('span').text)
            # Review
            review = comment.find('p', attrs={'class': 'commentSentence'})
            review = review.text.replace('\r\n', '').lstrip()

            info = comment.find('dl', attrs={'class': 'commentPurpose'})
            titles = info.find_all('dt')
            contents = info.find_all('dd')

            # SetData
            details = {}
            details['rate'] = rate
            details['review'] = review
            get_data.append(details)

    df = pd.DataFrame(get_data)
    return df

# WordCloud
def make_wordcloud(df,rate,top_n,min_freq):
    for i in rate:
        df_late = df[df['rate'] == i]
        npt = nlplot.NLPlot(df_late, target_col='review')
        stopwords = npt.get_stopword(top_n=top_n, min_freq=min_freq)
        st.write(f'<span style="background-color:pink;font-weight:bold"> 　Rate　:　{i} 　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　</span>',unsafe_allow_html = True)
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
        plt.imshow(fig_wc, interpolation='bilinear')
        plt.axis('off')
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

# Initiate
df = pd.DataFrame()
rate = []
page_count = range(0,5000,20)

# Sidebar
st.sidebar.text('')
st.sidebar.write('<span style="font-weight:bold"> Select Rate </span>',unsafe_allow_html = True)
if st.sidebar.checkbox(label = 'Rate:0'):
    rate.append(0)
if st.sidebar.checkbox(label = 'Rate:1'):
    rate.append(1)
if st.sidebar.checkbox(label = 'Rate:2'):
    rate.append(2)
if st.sidebar.checkbox(label = 'Rate:3'):
    rate.append(3)
if st.sidebar.checkbox(label = 'Rate:4'):
    rate.append(4)
if st.sidebar.checkbox(label = 'Rate:5'):
    rate.append(5)
st.sidebar.text('')
st.sidebar.write('<span style="font-weight:bold"> Frequent Word Setting </span>',unsafe_allow_html = True)
top_n = st.sidebar.slider('Top Frequent Words', 0, 10, 0)
st.sidebar.text('')
min_freq = st.sidebar.slider('Frequent Subordinate Words', 0, 10, 0)
st.sidebar.text('')
st.sidebar.write('<span style="font-weight:bold"> Create WordCloud </span>',unsafe_allow_html = True)
button = st.sidebar.button('start')

# Main
st.title('Review Analysis')

if rate == []:
    st.error('Rate is not set', icon=None)    
else:
    if button:
        df = get_scraipingdata(page_count)
        make_wordcloud(df, rate, top_n, min_freq)