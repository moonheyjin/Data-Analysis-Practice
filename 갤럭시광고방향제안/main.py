import streamlit as st
import pandas as pd
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

st.markdown('# 갤럭시23 시리즈 데이터 분석을 통한 갤럭시(스마트폰) 광고 방향성 제안')
st.caption('타겟 대상: 삼성전자 / 상품기획, 제품전략팀(Product Planning& Management)')
st.caption('사용 방법: 데이터 수집은(2023.11.19)일 기준이며, 수집 데이터 변경을 원한다면 같이 첨부된 파일을 통해 다시 데이터를 csv 파일로 저장 받아 실행하면 된다.')
st.caption('---')    


###유튜브 후기 --> 워드클라우드 분석 내용
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from nltk.tokenize import word_tokenize
from collections import Counter
from matplotlib import font_manager, rc
import nltk

nltk.download('punkt')

st.markdown('## 유튜브 댓글 활용 워드클라우드와 빈도수 분석  |  갤럭시23, 아이폰15')
st.caption('데이터 분석 과정: 1. 동일 기기(갤럭시, 아이폰) 모두 잇섭 채널에서 소개된 영상들의 댓글을 수집하였다. 2.댓글 크롤링을 한 후 df형식으로 저장 3.최종적으로 df을 .csv파일로 저장해 활용하였다. 4. .csv파일에 있는 데이터를 가지고 워드클라우드와 빈도수 분석 진행')
columns = st.columns(2)
#갤럭시23
with columns[0]:
    st.markdown('##### 갤럭시23')
    # 데이터 불러오기
    raw = pd.read_csv('./갤럭시23시리즈 유튜브 후기.csv')
    reviews = raw['reply'].dropna()
    text = ' '.join(reviews)

    # NLTK를 사용하여 토큰화
    tokens = word_tokenize(text)

    # 불용어리스트 지정
    stop_words = set(['가','게','고','과','네','는','다','도','들','듯','를','에','와','으로',
    '은','을','의','이','인','임','자','잘','좀','지','하다','한','너무','많이','진짜','이번에',
    '잇섭','님','잇섭님','때문에','더','확실히','하지만', '그리고','역시','상당히','같은데','감사합니다','그','하고','딱','안','아직','이게'
    '것이','정말','보면','저는','물론','같습니다','것','합니다','ㅎㅎ','ㅋㅋ','보고','이번에', '.', ',', '?', '!', '(', ')','...','..'
    ,'이번','수','같은','그냥','같','있'])

    # 불용어 제거
    tokens = [word for word in tokens if word.lower() not in stop_words]

    # '성능이'와 '성능'을 합쳐서 카운트
    for i, word in enumerate(tokens):
        if word.lower() == '성능이':
            tokens[i] = '성능'

    # 워드클라우드 생성 및 한글 폰트 설정
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(' '.join(tokens))
   
    st.caption('워드클라우드')
    st.image(wordcloud.to_array())
    
    # 단어 빈도수 분석
    word_counter = Counter(tokens)
    most_common_words = word_counter.most_common(10)

    font_path = 'C:/Windows/Fonts/malgun.ttf'
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)

    df_word_count = pd.DataFrame(most_common_words, columns=['word', 'count'])
    st.caption('빈도수 분석')
    st.bar_chart(df_word_count.set_index('word'))
    st.dataframe(df_word_count)

#아이폰15
with columns[1]:
    st.markdown('##### 아이폰15')
    # 데이터 불러오기
    raw2 = pd.read_csv('./아이폰15시리즈 유튜브 후기.csv')
    reviews2 = raw2['reply'].dropna()
    text = ' '.join(reviews2)

    # NLTK를 사용하여 토큰화
    tokens = word_tokenize(text)

    # 불용어리스트 지정
    stop_words = set(['가','게','고','과','네','는','다','도','들','듯','를','에','와','으로',
    '은','을','의','이','인','임','자','잘','좀','지','하다','한','너무','많이','진짜','이번에',
    '잇섭','님','잇섭님','때문에','더','확실히','하지만', '그리고','역시','상당히','같은데','감사합니다','그','하고','딱','안','아직','이게'
    '것이','정말','보면','저는','물론','같습니다','것','합니다','ㅎㅎ','ㅋㅋ','보고','이번에', '.', ',', '?', '!', '(', ')','...','..'
    ,'이번','수','같은','그냥','같','있'])

    # 불용어 제거
    tokens = [word for word in tokens if word.lower() not in stop_words]

    # '성능이'와 '성능'을 합쳐서 카운트
    for i, word in enumerate(tokens):
        if word.lower() == '성능이':
            tokens[i] = '성능'

    # 워드클라우드 생성 및 한글 폰트 설정
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(' '.join(tokens))
   
    st.caption('워드클라우드')
    st.image(wordcloud.to_array())
    
    # 단어 빈도수 분석
    word_counter = Counter(tokens)
    most_common_words = word_counter.most_common(10)

    font_path = 'C:/Windows/Fonts/malgun.ttf'
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)

    df_word_count = pd.DataFrame(most_common_words, columns=['word', 'count'])
    st.caption('빈도수 분석')
    st.bar_chart(df_word_count.set_index('word'))
    st.dataframe(df_word_count)
    
    
    

###리뷰
rs = pd.read_csv('./갤럭시23리뷰수집.csv')
# 'content' 열에서 '성능'이 들어간 부분을 5개만 수집
selected_reviews = rs[rs['content'].str.contains('성능', na=False)].head(5)['content']
for i, review in enumerate(selected_reviews, 1):
    print(f"Review {i}:\n{review}\n")
    
##디자인(색상)
st.markdown('---')
st.markdown('## 갤럭시23 시리즈 색상별 판매량')
st.caption('데이터 분석 과정: 1.네이버 쇼핑몰에서 갤럭시23에 대한 구매자들의 후기 수집 2. 데이터를 울트라, 플러스, 기본으로 따로 나눠 각각의 csv파일로 저장 3. 각 csv파일을 이용해 색상을 count 후 어떤 색상이 판매량이 높았는지 파악')

columns = st.columns(3)
with columns[0]:
    gu = pd.read_csv('./갤럭시23울트라.csv')

    cond1 = gu['info'].str.contains('팬텀블랙')
    cond2 = gu['info'].str.contains('크림')
    cond3 = gu['info'].str.contains('라벤더')    
    cond4 = gu['info'].str.contains('그린')

    count_df = pd.DataFrame(index=['크림', '그린', '팬텀블랙', '라벤더'], columns=['개수'])

    # 각 조건에 따른 갯수 계산 및 count_df에 저장
    count_df.at['팬텀블랙', '개수'] = cond1.sum()
    count_df.at['크림', '개수'] = cond2.sum()
    count_df.at['라벤더', '개수'] = cond3.sum()
    count_df.at['그린', '개수'] = cond4.sum()
    st.markdown('##### 갤럭시23 울트라')
    st.dataframe(count_df, use_container_width  = True)
    
with columns[1]:
    gp = pd.read_csv('./갤럭시23플러스.csv')

    cond1 = gp['info'].str.contains('팬텀블랙')
    cond2 = gp['info'].str.contains('크림')
    cond3 = gp['info'].str.contains('라벤더') 
    
    count_df2 = pd.DataFrame(index=['크림', '그린', '팬텀블랙', '라벤더'], columns=['개수'])
    
    # 각 조건에 따른 갯수 계산 및 count_df에 저장
    count_df2.at['팬텀블랙', '개수'] = cond1.sum()
    count_df2.at['크림', '개수'] = cond2.sum()
    count_df2.at['라벤더', '개수'] = cond3.sum()
    count_df2.at['그린', '개수'] = cond4.sum()
    st.markdown('##### 갤럭시23 플러스')
    st.dataframe(count_df2,use_container_width  = True)
        
        
with columns[2]:
    go = pd.read_csv('./갤럭시23.csv')

    cond1 = go['info'].str.contains('팬텀블랙')
    cond2 = go['info'].str.contains('크림')
    cond3 = go['info'].str.contains('라벤더')    
    cond4 = go['info'].str.contains('그린')

    count_df3 = pd.DataFrame(index=['크림', '그린', '팬텀블랙', '라벤더'], columns=['개수'])

    # 각 조건에 따른 갯수 계산 및 count_df에 저장
    count_df3.at['팬텀블랙', '개수'] = cond1.sum()
    count_df3.at['크림', '개수'] = cond2.sum()
    count_df3.at['라벤더', '개수'] = cond3.sum()
    count_df3.at['그린', '개수'] = cond4.sum()
    st.markdown('##### 갤럭시23')
    st.dataframe(count_df3,use_container_width  = True)


###광고 느낌
st.markdown('## 삼성의 광고')
st.caption('데이터 분석 과정: 1. 공식 홈페이지 채널에 들어가 정보(제목, 날짜 등) 수집 2. 정보 중 제목을 워드클라우드를 통해 각 회사의 광고 방향성 추측')
st.markdown('---')  
import re
st.markdown('##### 삼성')
columns = st.columns(1)

with columns[0]:
    s_title = pd.read_csv('./삼성전자 갤럭시 광고 정보들.csv')
    s_title['title'] = s_title['title'].str.extract(r'\](.*?)\|')
    reviews = s_title['title'].dropna()
    reviews = s_title['title'].dropna()
    text = ' '.join(reviews)
    
    # NLTK를 사용하여 토큰화
    tokens = word_tokenize(text)

    # 불용어리스트 지정
    stop_words = set(['가','게','고','과','네','는','다','도','들','듯','를','에','와','으로',
    '은','을','의','이','인','임','자','잘','좀','지','하다','한', '.', ',', '?', '!', '(', ')','...','..'
    ,'이번','수','같은','그냥','같','있','-','–','편'])

    # 불용어 제거
    tokens = [word for word in tokens if word.lower() not in stop_words]

    # 워드클라우드 생성 및 한글 폰트 설정
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(' '.join(tokens))
   
    st.caption('워드클라우드')
    st.image(wordcloud.to_array())
    
    # 단어 빈도수 분석
    word_counter = Counter(tokens)
    most_common_words = word_counter.most_common(10)

    font_path = 'C:/Windows/Fonts/malgun.ttf'
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)

    df_word_count = pd.DataFrame(most_common_words, columns=['word', 'count'])
    st.caption('빈도수 분석')
    st.bar_chart(df_word_count.set_index('word'))
    st.dataframe(df_word_count)