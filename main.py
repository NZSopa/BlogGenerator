from openai import OpenAI
import streamlit as st
import os
from datetime import datetime, timedelta


# 사이드바 설정
with st.sidebar:
    st.title("SoPa Blog Generator")
    st.write("This is a simple blog generator powered by OpenAI and Streamlit.")

    # API 키 입력 필드
    # openai_api_key = st.text_input("OpenAI API Key", type="password")
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    google_api_key = st.text_input("Google API Key", type="password")
    google_cse_id = st.text_input("Google Custom Search Engine ID")
    
# 사용자 입력 필드
city = st.text_input("Enter the city")
category = st.text_input("Enter the category")

# 프롬프트 생성 함수
def prompt_generator(topic):
    prompt = f'''
        Write blog posts in markdown format.
        Write the theme of your blog as "{topic}".
        Highlight, bold, or italicize important words or sentences.
        Please include the restaurant's address, menu recommendations and other helpful information(opening and closing hours) as a list style.
        Please make the entire blog less than 10 minutes long.
        The audience of this article is 40-60 years old.
        Create several hashtags and add them only at the end of the line.
        Add a summary of the entire article at the beginning of the blog post.
        Write in Korean.
    '''
    return prompt

# OpenAI 클라이언트 초기화
client = OpenAI(api_key= openai_api_key)

# 블로그 생성 함수
def generate_blog(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 또는 사용 가능한 최신 모델
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes blog posts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"블로그 생성 중 오류 발생: {str(e)}")
        return None

# 해시태그 생성 함수
def generate_hash_tags(blog):
    import re
    hashtags = [w[1:] for w in re.findall(r'(#+[a-zA-Z0-9(_)])', blog)]
    tag_string = ""
    for w in hashtags:
        if len(w) > 3:
            tag_string += f"{w}, "
    tag_string = re.sub(r'[^a-zA-Z, ]', '', tag_string)
    hashtags = tag_string.strip()[:-1]
    return hashtags

# 블로그 헤더 생성 함수
def generate_head(topic, category, hashtags):
    page_head = f'''---
    layout: single
    title: "{topic}"
    categories: {category}
    tag : [{hashtags}]
    toc: false
    author_profile: false
    sidebar:
        nav: "counts
    ---
    '''
    return page_head

# 블로그 출력 함수
def output_blog(topic, category, output):
    try:
        yesterday = datetime.now() - timedelta(days=1)
        timestring = yesterday.strftime("%Y-%m-%d")
        filename = f"{timestring}-{'-'.join(topic.lower().split())}-{category.lower()}.md"
        filepath = os.path.join("posts", filename)
        
        # posts 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(output)
        st.success(f"블로그가 성공적으로 저장되었습니다: {filepath}")
    except IOError as e:
        st.error(f"파일 저장 중 오류 발생: {str(e)}")
    except Exception as e:
        st.error(f"블로그 출력 중 오류 발생: {str(e)}")

# 생성 버튼 클릭 시 실행
if st.button("Generate"):
    if not city or not category:
        st.error("도시와 카테고리를 모두 입력해주세요.")
    else:
        try:
            topic = f"Top 10 Cafes you must visit in {city}"
            prompt = prompt_generator(topic)
            blog = generate_blog(prompt)
            if blog:
                hashtags = generate_hash_tags(blog)
                head = generate_head(topic, category, hashtags)
                output = head + blog
                output_blog(topic, category, output)
                st.write(output)
        except Exception as e:
            st.error(f"블로그 생성 과정에서 오류 발생: {str(e)}")
