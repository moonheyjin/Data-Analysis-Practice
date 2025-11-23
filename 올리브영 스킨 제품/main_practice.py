import pandas as pd
import streamlit as st
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import font_manager


# 데이터 로드
# @st.cache
def load_data(file_path):
    return pd.read_excel(file_path)

# 1. 많이 언급된 브랜드 Top 5 (수집 순서 고려)
def get_top_brands_with_order(df, top_n=5):
    brand_counts = df['브랜드'].value_counts().reset_index()
    brand_counts.columns = ['브랜드', '언급횟수']
    
    # 수집 순서를 고려한 브랜드 순서 유지
    df['수집순서'] = df.index  # 수집된 순서 추가
    brand_order = df[['브랜드', '수집순서']].drop_duplicates(subset=['브랜드'], keep='first')
    
    # 브랜드 순위 정렬: 언급횟수 -> 수집순서
    merged = pd.merge(brand_counts, brand_order, on='브랜드')
    merged = merged.sort_values(by=['언급횟수', '수집순서'], ascending=[False, True])
    
    return merged.head(top_n).set_index('브랜드')['언급횟수']

# 2-1. 성분 데이터에서 제외 성분 제외 후 워드클라우드
def generate_filtered_wordcloud(df, exclude_list=None, col='구성정보'):
    if exclude_list is None:
        exclude_list = {'정제수', '에탄올', '알코올', '보습제'}
    
    # 모든 성분 추출
    ingredient_data = []
    for ingredients in df[col]:
        if pd.notna(ingredients):
            for ingredient in ingredients.split(', '):
                if ingredient not in exclude_list:
                    ingredient_data.append(ingredient)
    
    # 워드클라우드 생성
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    ingredient_text = ' '.join(ingredient_data)
    wordcloud = WordCloud(
        font_path=font_path,
        width=800,
        height=400,
        background_color='white'
    ).generate(ingredient_text)
    
    # 그림 생성
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

# 2-2. 겹치지 않는 성분만 추출 및 워드클라우드 생성
def generate_low_frequency_histogram_and_top5(df, exclude_list=None, col='구성정보', threshold=39, top_n=10):
    if exclude_list is None:
        exclude_list = {'정제수', '에탄올', '알코올', '보습제'}
    
    # 모든 성분 추출
    ingredient_data = []
    for ingredients in df[col]:
        if pd.notna(ingredients):
            for ingredient in ingredients.split(', '):
                if ingredient not in exclude_list:
                    ingredient_data.append(ingredient)
    
    # 성분 카운트
    ingredient_counts = Counter(ingredient_data)
    
    # 60번 이하로 언급된 성분 필터링
    low_frequency_ingredients = {ing: count for ing, count in ingredient_counts.items() if count <= threshold}
    
    # Top N 성분 추출
    top_low_freq_ingredients = sorted(low_frequency_ingredients.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    # 데이터 프레임 생성
    hist_data = pd.DataFrame(top_low_freq_ingredients, columns=['성분', '언급횟수'])
    
    # 한글 폰트 설정
    font_path = 'C:/Windows/Fonts/malgun.ttf'  # Windows용 폰트 경로
    font_prop = font_manager.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
    
    # 히스토그램 생성
    fig, ax = plt.subplots(figsize=(10, 6))
    hist_data.sort_values(by='언급횟수').plot.barh(
        x='성분', y='언급횟수', ax=ax, color='skyblue', legend=False
    )
    ax.set_xlabel('언급 횟수', fontsize=12)
    ax.set_ylabel('성분', fontsize=12)
    ax.set_title('40번 미만 언급된 성분 Top 10', fontsize=16)
    plt.tight_layout()
    
    return fig, hist_data,




# 3. 전체 많이 언급된 성분 Top 5
def get_top_ingredients(df, top_n=5):
    ingredient_data = []
    for ingredients in df['구성정보']:
        if pd.notna(ingredients):
            for ingredient in ingredients.split(', '):
                ingredient_data.append(ingredient)
    
    # 제외 성분 리스트
    exclude_list = {'정제수', '에탄올', '알코올', '보습제'}
    filtered_data = [ing for ing in ingredient_data if ing not in exclude_list]
    
    # 상위 n개 성분 추출
    ingredient_counts = Counter(filtered_data)
    return ingredient_counts.most_common(top_n)

# 4. 피부타입별 많이 언급된 성분 Top 5
def get_top_ingredients_by_skin_type(df, skin_type_col='피부타입추천', top_n=5):
    ingredient_data = []

    for _, row in df.iterrows():
        skin_type = row[skin_type_col]
        ingredients = row['구성정보']
        if pd.notna(skin_type) and pd.notna(ingredients):
            for ingredient in ingredients.split(', '):  # 성분 분리
                ingredient_data.append((skin_type, ingredient))
    
    # 제외 성분 리스트
    exclude_list = {'정제수', '에탄올', '알코올', '보습제'}
    filtered_data = [(skin_type, ing) for skin_type, ing in ingredient_data if ing not in exclude_list]
    
    # 성분별 카운트
    skin_type_counts = {}
    for skin_type, ing in filtered_data:
        if skin_type not in skin_type_counts:
            skin_type_counts[skin_type] = Counter()
        skin_type_counts[skin_type][ing] += 1
    
    # 상위 n개 성분 추출
    result = {}
    for skin_type, counts in skin_type_counts.items():
        result[skin_type] = counts.most_common(top_n)
    
    return result


# 불용어 정의
STOPWORDS = {
    '의', '이', '가', '은', '는', '을', '를', '에', '와', '과', 
    '도', '으로', '로', '에서', '하고', '입니다', '수', '있다', 
    '있습니다', '합니다', '그리고', '하지만', '더', '그', '또', '한',
    '너무', '정말', '좋아요', '저는', '아주', '피부가', '같아요', 
    '것', '토너', '피부', '스킨', '때', '좀', '좋아서', '많이', 
    '느낌', '이거', '다른', '쓰면', '정도', '있는', '없고', 
    '항상', '같이', '구매했어요', '구매', '다시', '진짜', 'n', 
    '일단', '바로', '그냥', '좋은', '쓰고', '피부에', '동생이', '향도', '좋겠어요', 
    '추천합니다', '한 번', '엄청', '제품은', '제품이', '생각합니다', '제품입니다', 
    '좋아요', '제가', '동생은', '느낌이', '좋은거', '좋습니다', '이것만', '제품', 
    '리뷰', '조금', '엄청', 'ㅎㅎ', '좋고', '확실히', '제품을', '완전', '토너를', 
    '있어서', '없어서', '사용해도', '꾸준히', '느낌이에요', '그래서', '굉장히', 
    '쓰고', '전에', '사서', '생각보다', '샀어요', '근데', '해서', '자주', '특히', 
    '따로', 'ㅠㅠ', '때문에', '제품이라', '한번', '거의', '워낙', '이렇게', '있어서', 
    '사용', '사용하고', '사용하면', '않고', 'ㅋㅋ', '느낌이', '있어요', '구매했는데', 
    'n저는', 'n', '토너는', '같아요', '그런지', '제품이에요', '되고', '자주', '나서', 
    '엄청', '토너를', '피부에', '제품', '토너는', '조금', '그래서', '때문에', '해서', 
    '살짝', '제품입니다', '같아서', '사용하는데', '얼굴이', '구매했습니다', '추천합니다', 
    '하나', '이번에', '지금', '사용하면', '요즘', '가장', '처음', '여러번', '발라도', 
    '이렇게', '느낌이라','토너가', '좋았어요', '좋네요', '얼굴에', '토너로', '그런', 
    '없는', '맞는', '좋다고', '좋아요', '같아요','토너도','같습니다','좋을','그리고','써봤는데',
    '좋더라구요','약간','맞는','사용하기','금방','뭔가','있는데','않아서','같은','좋다고','좋았어요',
    '아니라','같은','역시','좋아요','좋네요','있는데','하는','n그리고','이런','같습니다','있어','좋다고',
    '그래도','계속','좋아요','있는데','없는', '남편이','하더라고요','않지만','있지만','있고','좋은데', '이걸로',
    '늘','이게','이건','없이','크리니크','다만','같아요','제품에'
}


# 불용어 제거 함수
def preprocess_text(text):
    # 텍스트를 단어로 나누기
    words = text.split()  # 기본적으로 공백을 기준으로 분리
    # 불용어 제거
    meaningful_words = [word for word in words if word not in STOPWORDS and len(word) > 1]
    return ' '.join(meaningful_words)

def preprocess_reviews(df, review_col='리뷰'):
    df['전처리_리뷰'] = df[review_col].dropna().apply(preprocess_text)
    return df

# 5.리뷰 워드클라우드 생성 (불용어 제외)
def generate_wordcloud(df, review_col='전처리_리뷰'):
    # 전처리된 리뷰를 사용하여 텍스트 생성
    review_text = ' '.join(df[review_col].dropna())
    
    # 워드클라우드 생성
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    wordcloud = WordCloud(
        font_path=font_path, 
        width=800, 
        height=400, 
        background_color='white', 
        stopwords=STOPWORDS  # 불용어 목록을 전달하여 워드클라우드에서 제외되도록 설정
    ).generate(review_text)
    
    # 워드클라우드 그림 생성
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

# 6. 피부타입별 리뷰 워드클라우드 생성 (불용어 제외)
def generate_wordcloud_by_skin_type(df, skin_type_col='피부타입추천', review_col='전처리_리뷰'):
    # 피부타입별 리뷰 그룹화
    skin_type_reviews = df.groupby(skin_type_col)[review_col].apply(lambda x: ' '.join(x.dropna()))
    skin_type_wordclouds = {}
    
    # 폰트 경로 설정
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    
    for skin_type, review_text in skin_type_reviews.items():
        if review_text:  # 비어 있지 않은 리뷰에 대해서만 처리
            wordcloud = WordCloud(
                font_path=font_path, 
                width=800, 
                height=400, 
                background_color='white', 
                stopwords=STOPWORDS  # 불용어 목록을 전달하여 워드클라우드에서 제외되도록 설정
            ).generate(review_text)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            skin_type_wordclouds[skin_type] = fig
    
    return skin_type_wordclouds



# Streamlit 메인 함수
def main():
    st.title("올리브영 스킨, 토너 데이터 분석")
    
    # 데이터 로드
    file_path = '올영_스킨토너_판매순_스킨타입별.xlsx'
    df = load_data(file_path)

    # 많이 언급된 브랜드 Top 5
    st.header("1️⃣ 많이 언급된 브랜드 Top 5 (수집 순서 고려)")
    top_brands = get_top_brands_with_order(df)
    st.bar_chart(top_brands)

    # 2번: 구성정보 워드클라우드 (제외 성분 제거)
    st.header("2️⃣ 제외 성분 제거 후 구성 성분 워드클라우드")
    filtered_wordcloud_fig = generate_filtered_wordcloud(df)
    st.pyplot(filtered_wordcloud_fig)

    # 2번 추가: 겹치지 않는 성분 히스토그램 및 전체 Top 5
    st.header("2️⃣-1️⃣ 60번 이하 언급된 성분 히스토그램 및 전체 Top 5")
    low_freq_hist_fig, low_freq_hist_data = generate_low_frequency_histogram_and_top5(df)

    # 히스토그램 출력
    st.pyplot(low_freq_hist_fig)
    
    # 히스토그램 데이터 출력
    st.subheader("60번 이하 언급된 성분 Top 10 데이터")
    st.table(low_freq_hist_data)

    # 전체 많이 언급된 성분 Top 5
    st.header("3️⃣ 전체 많이 언급된 성분 Top 5 (공통 성분 제외)")
    top_ingredients = get_top_ingredients(df)
    st.table(pd.DataFrame(top_ingredients, columns=['성분', '언급횟수']))

    # 피부타입별 많이 언급된 성분 Top 5
    st.header("4️⃣ 피부타입별 많이 언급된 성분 Top 5")
    skin_type_ingredients = get_top_ingredients_by_skin_type(df)
    for skin_type, top_ingredients in skin_type_ingredients.items():
        st.subheader(f"피부타입: {skin_type}")
        st.table(pd.DataFrame(top_ingredients, columns=['성분', '언급횟수']))

    # 리뷰 워드클라우드
    st.header("5️⃣ 리뷰 워드클라우드 (전체)")
    df = preprocess_reviews(df)  # 전처리 적용
    wordcloud_fig = generate_wordcloud(df, review_col='전처리_리뷰')  # 전처리된 리뷰 컬럼 사용
    st.pyplot(wordcloud_fig)

    # 피부타입별 리뷰 워드클라우드
    st.header("6️⃣ 피부타입별 리뷰 워드클라우드")
    skin_type_wordclouds = generate_wordcloud_by_skin_type(df, review_col='전처리_리뷰')  # 전처리된 리뷰 컬럼 사용
    for skin_type, wordcloud_fig in skin_type_wordclouds.items():
        st.subheader(f"피부타입: {skin_type}")
        st.pyplot(wordcloud_fig)

if __name__ == "__main__":
    main()
