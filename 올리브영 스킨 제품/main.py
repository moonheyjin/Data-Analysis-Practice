import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import font_manager

def get_multiple_page(save_path='올영_스킨토너_판매순.xlsx'):
    browser = webdriver.Chrome()
    results = []
    try:
        for page_idx in range(1, 6):
            url = f'https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010013&fltDispCatNo=&prdSort=03&pageIdx={page_idx}'
            browser.get(url)
            time.sleep(2)

            product_elements = browser.find_elements(By.CSS_SELECTOR, 'div.prd_info > a')
            num_products = len(product_elements)

            for product_idx in range(num_products):
                # 제품 요소 재탐색
                product_elements = browser.find_elements(By.CSS_SELECTOR, 'div.prd_info > a')
                product_elements[product_idx].click()
                time.sleep(2)

                soup = BeautifulSoup(browser.page_source, 'html.parser')
                brand = soup.select_one('p.prd_brand').text.strip() if soup.select_one('p.prd_brand') else None
                product_name = soup.select_one('.prd_name').text.strip() if soup.select_one('.prd_name') else None
                price = soup.select_one('div.price > .price-2 > strong').text.strip() if soup.select_one('div.price > .price-2 > strong') else None

                go_composition = browser.find_elements(By.CSS_SELECTOR, 'li#buyInfo > a')
                composition_data = None
                if go_composition:
                    go_composition[0].click()
                    time.sleep(2)
                    soup = BeautifulSoup(browser.page_source, 'html.parser')
                    composition_elements = soup.select('div#artcInfo > dl.detail_info_list > dd')
                    if composition_elements and len(composition_elements) > 6:
                        composition_data = composition_elements[6].text.strip()

                reviews = []
                go_review = browser.find_elements(By.CSS_SELECTOR, 'li#reviewInfo')
                if go_review:
                    go_review[0].click()
                    time.sleep(2)
                    for review_page in range(1, 11):
                        # 리뷰 요소 재탐색
                        review_elements = browser.find_elements(By.CSS_SELECTOR, 'div.txt_inner')
                        for review_element in review_elements:
                            reviews.append(review_element.text.strip())
                        try:
                            next_page_btn = browser.find_element(By.XPATH, f"//a[@data-page-no='{review_page + 1}']")
                            browser.execute_script("arguments[0].click();", next_page_btn)
                            time.sleep(2)
                        except:
                            break

                results.append({
                    "브랜드": brand,
                    "상품명": product_name,
                    "가격": price,
                    "구성정보": composition_data,
                    "리뷰": reviews
                })
                browser.back()
                time.sleep(2)
    finally:
        browser.quit()

    final_df = pd.DataFrame(results)
    final_df.to_excel('./data/올영_스킨토너_판매순_스킨타입별.xlsx', index=False)
    return final_df


# @st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# 1. 많이 언급된 브랜드 Top 5 (수집 순서 고려)
def get_top_brands_with_order(df, top_n=5):
    brand_counts = df['브랜드'].value_counts().reset_index()
    brand_counts.columns = ['브랜드', '언급횟수']
    
    # 수집 순서를 고려한 브랜드 순서 유지
    df['수집순서'] = df.index  
    brand_order = df[['브랜드', '수집순서']].drop_duplicates(subset=['브랜드'], keep='first')

    merged = pd.merge(brand_counts, brand_order, on='브랜드')
    merged = merged.sort_values(by=['언급횟수', '수집순서'], ascending=[False, True])
    
    result = merged.head(top_n).reset_index(drop=True)  
    result.index += 1 

    return result.set_index('브랜드')['언급횟수']

# 2-1. 성분 데이터에서 제외 성분 제외 후 워드클라우드
def generate_filtered_wordcloud(df, exclude_list=None, col='구성정보'):
    if exclude_list is None:
        exclude_list = {'정제수', '에탄올', '알코올', '보습제'}
    
    ingredient_data = []
    for ingredients in df[col]:
        if pd.notna(ingredients):
            for ingredient in ingredients.split(', '):
                if ingredient not in exclude_list:
                    ingredient_data.append(ingredient)

    font_path = 'C:/Windows/Fonts/malgun.ttf'
    ingredient_text = ' '.join(ingredient_data)
    wordcloud = WordCloud(
        font_path=font_path,
        width=800,
        height=400,
        background_color='white'
    ).generate(ingredient_text)
   
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

# 2-2. 겹치지 않는 성분만 추출 및 워드클라우드 생성
def generate_low_frequency_histogram_and_top5(df, exclude_list=None, col='구성정보', threshold=39, top_n=10):
    if exclude_list is None:
        exclude_list = {'정제수', '에탄올', '알코올', '보습제'}
    
    ingredient_data = []
    for ingredients in df[col]:
        if pd.notna(ingredients):
            for ingredient in ingredients.split(', '):
                if ingredient not in exclude_list:
                    ingredient_data.append(ingredient)
    
    ingredient_counts = Counter(ingredient_data)
    
    low_frequency_ingredients = {ing: count for ing, count in ingredient_counts.items() if count <= threshold}
    
    top_low_freq_ingredients = sorted(low_frequency_ingredients.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    hist_data = pd.DataFrame(top_low_freq_ingredients, columns=['성분', '언급횟수'])
    hist_data.index += 1
    
    font_path = 'C:/Windows/Fonts/malgun.ttf'  # Windows용 폰트 경로
    font_prop = font_manager.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
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
    
    exclude_list = {'정제수', '에탄올', '알코올', '보습제'}
    filtered_data = [ing for ing in ingredient_data if ing not in exclude_list]
    
    ingredient_counts = Counter(filtered_data)
    top_ingredients = ingredient_counts.most_common(top_n)
    
    result = pd.DataFrame(top_ingredients, columns=['성분', '언급횟수']).reset_index(drop=True)
    result.index += 1  
    return result

# 4. 피부타입별 많이 언급된 성분 Top 5
def get_top_ingredients_by_skin_type(df, skin_type_col='피부타입추천', top_n=5):
    ingredient_data = []

    for _, row in df.iterrows():
        skin_type = row[skin_type_col]
        ingredients = row['구성정보']
        if pd.notna(skin_type) and pd.notna(ingredients):
            for ingredient in ingredients.split(', '): 
                ingredient_data.append((skin_type, ingredient))
    
    exclude_list = {'정제수', '에탄올', '알코올', '보습제'}
    filtered_data = [(skin_type, ing) for skin_type, ing in ingredient_data if ing not in exclude_list]
    
    skin_type_counts = {}
    for skin_type, ing in filtered_data:
        if skin_type not in skin_type_counts:
            skin_type_counts[skin_type] = Counter()
        skin_type_counts[skin_type][ing] += 1
    
    result = {}
    for skin_type, counts in skin_type_counts.items():
        top_counts = counts.most_common(top_n)
        result[skin_type] = (
            pd.DataFrame(top_counts, columns=['성분', '언급횟수'])
            .reset_index(drop=True)
            .assign(순위=lambda x: x.index + 1) 
        )
    
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

# 불용어 제거
def preprocess_text(text):
    words = text.split() 
    meaningful_words = [word for word in words if word not in STOPWORDS and len(word) > 1]
    return ' '.join(meaningful_words)

def preprocess_reviews(df, review_col='리뷰'):
    df['전처리_리뷰'] = df[review_col].dropna().apply(preprocess_text)
    return df

# 5.리뷰 워드클라우드 생성 (불용어 제외)
def generate_wordcloud(df, review_col='전처리_리뷰'):
    review_text = ' '.join(df[review_col].dropna())
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    wordcloud = WordCloud(
        font_path=font_path, 
        width=800, 
        height=400, 
        background_color='white', 
        stopwords=STOPWORDS 
    ).generate(review_text)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

# 6. 피부타입별 리뷰 워드클라우드 생성 (불용어 제외)
def generate_wordcloud_by_skin_type(df, skin_type_col='피부타입추천', review_col='전처리_리뷰'):
    skin_type_reviews = df.groupby(skin_type_col)[review_col].apply(lambda x: ' '.join(x.dropna()))
    skin_type_wordclouds = {}
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    
    for skin_type, review_text in skin_type_reviews.items():
        if review_text: 
            wordcloud = WordCloud(
                font_path=font_path, 
                width=800, 
                height=400, 
                background_color='white', 
                stopwords=STOPWORDS 
            ).generate(review_text)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            skin_type_wordclouds[skin_type] = fig
    
    return skin_type_wordclouds

def main():
    st.markdown('## 🫒올리브영 [스킨/토너] 판매순 크롤링&분석')

    if st.button("수집하기"):
        with st.spinner("데이터 수집 중... 잠시만 기다려주세요!"):
            new_data = get_multiple_page()
            new_data['피부타입추천'] = new_data.apply(recommend_skin_type, axis=1)
            new_data.to_excel('./올영_스킨토너_판매순_스킨타입별.xlsx', index=False, encoding='utf-8-sig')
            st.success("데이터 수집 및 저장 완료!")

    if os.path.exists('./data/올영_스킨토너_판매순_스킨타입별.xlsx'):
        df = pd.read_excel('./data/올영_스킨토너_판매순_스킨타입별.xlsx')
    
    category = st.selectbox("카테고리 선택", ["소개","데이터 활용 및 소개", "브랜드", "성분", "리뷰", "피부 타입별 리뷰 및 성분"])
    
    if category == "소개":
        st.subheader("🏢 회사 소개 : 올리브영")
        st.write(" 올리브영은 기초부터 메이크업, 스킨케어까지 다양한 뷰티 제품을 아우르는 종합 뷰티 스토어입니다. \n 나아가 뷰티뿐만 아니라 헬스, 라이프스타일 제품을 제공하는 대한민국의 대표적인 헬스앤뷰티 스토어입니다. ")
        st.subheader("🔍 직무 소개 : MD")
        st.markdown("##### 트렌드 분석 기반 카테고리 전략 수립 ")
        st.write("   - 변화하는 시장 트렌드 캐칭 및 카테고리 분석 통한 전략 수립 \n  - 전략 기반 내/외부 자원 투입 리딩 ")
        st.markdown("#####  카테고리 전략 기반 브랜드/상품 기획, 도입 및 육성  ")
        st.write("   -  신규 브랜드 소싱 및 상품 개발 및 협의 \n - 브랜드사 협업 통한 마케팅 방향성 기획 및 운영  ")

    elif category == "데이터 활용 및 소개":
        st.subheader("✅ 활용도 및 활용 방안 ")
        st.markdown("##### 1. 브랜드 카테고리 활용 ")
        st.write("   - 매장 진열 전략 \n  - 브랜드 육성 계획 ")
        st.markdown("#####  2. 성분 카테고리 활용  ")
        st.write(" - 트렌드 성분 파악")
        st.markdown("#####  3.피부 타입별 성분 & 리뷰 분석")
        st.write(" - 피부타입별 전략 : 타겟 고객층별 상품 구성")
        st.write(" - 고객 맞춤형 마케팅 : \n 피부타입별 주요 키워드를 활용한 마케팅 메시지 개발, 타겟 고객층별 차별화된 프로모션 설계, 시즌별 피부타입 맞춤 기획전 구성")
     
        st.subheader("💻 데이터 소개")
        st.write("이 데이터는 올리브영에서 판매순으로 정렬 된 스킨 및 토너 데이터를 수집한 것입니다.")
        st.write("상품명, 브랜드, 가격, 성분, 리뷰 등의 정보를 포함하고 있습니다.")
        st.dataframe(df.head())
        st.write("데이터 분석 및 시각화 진행 가능!")
    
    elif category == "브랜드":
        st.markdown("## 1️⃣ 많이 언급된 브랜드 Top 5")
        top_brands = get_top_brands_with_order(df)
        st.bar_chart(top_brands)
    
    elif category == "성분":
        st.markdown("## 1️⃣ 구성 성분 워드클라우드(기본 성분 제외)")
        filtered_wordcloud_fig = generate_filtered_wordcloud(df)
        st.pyplot(filtered_wordcloud_fig)

        st.markdown("## 2️⃣ 많이 언급된 성분 Top 5(기본 성분 제외)")
        top_ingredients = get_top_ingredients(df)
        st.table(pd.DataFrame(top_ingredients, columns=['성분', '언급횟수']))

        st.markdown("## 3️⃣ 40번 미만 언급된 성분 히스토그램")
        low_freq_hist_fig, low_freq_hist_data = generate_low_frequency_histogram_and_top5(df)
        st.pyplot(low_freq_hist_fig)
        
        st.subheader("40번 미만 언급된 성분 Top 10 데이터")
        st.table(low_freq_hist_data)

        st.markdown("## 4️⃣ 피부타입별 많이 언급된 성분 Top 5")
        skin_type_ingredients = get_top_ingredients_by_skin_type(df)
        for skin_type, top_ingredients in skin_type_ingredients.items():
            st.subheader(f"피부타입: {skin_type}")
            st.table(pd.DataFrame(top_ingredients, columns=['성분', '언급횟수']))
        
    elif category == "리뷰":
        st.markdown("## 1️⃣ 리뷰 워드클라우드 (전체)")
        df = preprocess_reviews(df)  # 전처리 적용
        wordcloud_fig = generate_wordcloud(df, review_col='전처리_리뷰')  # 전처리된 리뷰 컬럼 사용
        st.pyplot(wordcloud_fig)

        st.markdown("## 2️⃣ 피부타입별 리뷰 워드클라우드")
        skin_type_wordclouds = generate_wordcloud_by_skin_type(df, review_col='전처리_리뷰')  # 전처리된 리뷰 컬럼 사용
        for skin_type, wordcloud_fig in skin_type_wordclouds.items():
            st.subheader(f"피부타입: {skin_type}")
            st.pyplot(wordcloud_fig)

    elif category == "피부 타입별 리뷰 및 성분":
        st.markdown("## 1️⃣ 피부타입별 리뷰 및 성분 분석")
        
        skin_type_ingredients = get_top_ingredients_by_skin_type(df)
        df = preprocess_reviews(df)
        skin_type_wordclouds = generate_wordcloud_by_skin_type(df, review_col='전처리_리뷰')

        for skin_type in skin_type_ingredients.keys():
            st.subheader(f"피부타입: {skin_type}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**많이 언급된 성분 Top 5**")
                top_ingredients = skin_type_ingredients[skin_type]
                st.table(pd.DataFrame(top_ingredients, columns=['성분', '언급횟수']))
        
            with col2:
                st.markdown("**리뷰 워드클라우드**")
                st.pyplot(skin_type_wordclouds[skin_type])
        

if __name__ == "__main__":
    main()
