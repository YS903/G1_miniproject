import streamlit as st
import pandas as pd
import random
import time

# 페이지 기본 설정
st.set_page_config(
    page_title="G1 Vocabulary App",
    page_icon="📚",
    layout="centered"
)

# 데이터 로드 함수 (voca_3000.csv 파일 사용, 2열: 영단어, 4열: 뜻)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Voca_3000.csv", encoding="utf-8")
        return df
    except Exception as e:
        st.error(f"CSV 파일을 불러오는 중 오류가 발생했습니다: {e}")
        return None

df = load_data()

if df is not None:
    word_col = df.columns[1]   # 2번째 열 (영단어)
    meaning_col = df.columns[3] # 4번째 열 (뜻)
    
    st.sidebar.title("📚 G1 Vocabulary App")
    st.sidebar.markdown("중학교 1학년 필수 영단어 마스터!")
    
    menu = st.sidebar.selectbox(
        "학습 메뉴 선택",
        [
            "🏠 홈 소개",
            "🃏 플래시카드 학습",
            "❓ 객관식 퀴즈",
            "✍️ 서술형 스펠링 테스트",
            "⏱️ 타임어택 배틀"
        ]
    )

    if menu == "🏠 홈 소개":
        st.title("🌟 G1 English Vocabulary App")
        st.write("환영합니다! 중학교 1학년 수준의 3,000개 어휘를 플래시카드와 다양한 퀴즈로 마스터해보세요.")
        st.info("👈 왼쪽 사이드바에서 원하는 학습 단계를 선택하세요!")
        st.subheader("📊 데이터 현황")
        st.write(f"현재 연동된 전체 학습 단어 수: **{len(df)}개**의 교육과정 기초어휘")

    elif menu == "🃏 플래시카드 학습":
        st.header("🃏 플래시카드 단어 암기")
        st.write("카드를 넘겨가며 영단어와 뜻을 차근차근 암기해 보세요.")

        if "fc_word" not in st.session_state:
            row = df.sample(1).iloc[0]
            st.session_state.fc_word = str(row[word_col]).strip()
            st.session_state.fc_meaning = str(row[meaning_col]).strip()
            st.session_state.show_meaning = False

        word = st.session_state.fc_word
        meaning = st.session_state.fc_meaning

        st.markdown("---")
        if not st.session_state.show_meaning:
            st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>🔤 {word}</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>카드를 뒤집으려면 아래 버튼을 누르세요</p>", unsafe_allow_html=True)
            if st.button("🔄 뜻 확인하기 (카드 뒤집기)", use_container_width=True):
                st.session_state.show_meaning = True
                st.rerun()
        else:
            st.markdown(f"<h1 style='text-align: center; color: #2ca02c;'>💡 {meaning}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #1f77b4; font-weight: bold;'>영단어: {word}</p>", unsafe_allow_html=True)
            if st.button("🔄 다시 단어 보기", use_container_width=True):
                st.session_state.show_meaning = False
                st.rerun()
        
        st.markdown("---")
        if st.button("➡️ 다음 카드 넘어가기", use_container_width=True):
            row = df.sample(1).iloc[0]
            st.session_state.fc_word = str(row[word_col]).strip()
            st.session_state.fc_meaning = str(row[meaning_col]).strip()
            st.session_state.show_meaning = False
            st.rerun()

    elif menu == "❓ 객관식 퀴즈":
        st.header("❓ 객관식 퀴즈 (영단어 ➔ 뜻)")
        st.write("제시된 영단어를 보고 알맞은 뜻을 보기에서 고르세요.")

        if "q_total" not in st.session_state:
            st.session_state.q_total = 0
            st.session_state.q_correct_cnt = 0
            st.session_state.q_retry = False
            st.session_state.q_solved = False

        if "q_word" not in st.session_state:
            correct_row = df.sample(1).iloc[0]
            st.session_state.q_word = str(correct_row[word_col]).strip()
            st.session_state.q_correct = str(correct_row[meaning_col]).strip()
            wrong_rows = df[df[word_col] != st.session_state.q_word].sample(3)
            options = list(wrong_rows[meaning_col].values) + [st.session_state.q_correct]
            random.shuffle(options)
            st.session_state.q_options = options

        st.markdown(f"📊 **진행도: 맞춘 횟수 {st.session_state.q_correct_cnt}번 / 총 푼 문제 {st.session_state.q_total}문제**")
        st.markdown("---")

        st.markdown(f"### Q. 다음 영단어의 뜻은 무엇일까요?\n# **{st.session_state.q_word}**")
        choice = st.radio("보기를 선택하세요:", st.session_state.q_options, key="quiz_radio")

        if not st.session_state.q_solved:
            if st.button("정답 제출하기"):
                st.session_state.q_total += 1
                if choice == st.session_state.q_correct:
                    st.session_state.q_correct_cnt += 1
                    st.session_state.q_solved = True
                    st.success("🎉 정답입니다! 훌륭해요 👏")
                    st.rerun()
                else:
                    if not st.session_state.q_retry:
                        st.session_state.q_retry = True
                        st.warning("⚠️ 틀렸습니다! 하지만 포기하지 말고 다시 한 번 잘 생각해보세요. (기회 1번 연장)")
                    else:
                        st.session_state.q_solved = True
                        st.error(f"❌ 아쉽습니다. 정답은 **{st.session_state.q_correct}** 입니다.")
                        st.rerun()
        else:
            if st.button("➡️ 다음 문제 풀기"):
                st.session_state.q_retry = False
                st.session_state.q_solved = False
                correct_row = df.sample(1).iloc[0]
                st.session_state.q_word = str(correct_row[word_col]).strip()
                st.session_state.q_correct = str(correct_row[meaning_col]).strip()
                wrong_rows = df[df[word_col] != st.session_state.q_word].sample(3)
                options = list(wrong_rows[meaning_col].values) + [st.session_state.q_correct]
                random.shuffle(options)
                st.session_state.q_options = options
                st.rerun()

    elif menu == "✍️ 서술형 스펠링 테스트":
        st.header("✍️ 서술형 스펠링 테스트 (뜻 ➔ 영단어)")
        st.write("제시된 한국어 뜻을 보고 올바른 영단어 철자를 직접 입력해 보세요.")

        if "subj_total" not in st.session_state:
            st.session_state.subj_total = 0
            st.session_state.subj_correct_cnt = 0
            st.session_state.subj_retry = False
            st.session_state.subj_solved = False

        if "subj_word" not in st.session_state:
            rand_row = df.sample(1).iloc[0]
            st.session_state.subj_word = str(rand_row[word_col]).strip()
            st.session_state.subj_meaning = str(rand_row[meaning_col]).strip()
            w = st.session_state.subj_word
            st.session_state.subj_hint = w[0] + " _ " * (len(w) - 1)

        target_word = st.session_state.subj_word
        target_meaning = st.session_state.subj_meaning

        st.markdown(f"📊 **진행도: 맞춘 횟수 {st.session_state.subj_correct_cnt}번 / 총 푼 문제 {st.session_state.subj_total}문제**")
        st.markdown("---")

        st.markdown(f"### 뜻: **{target_meaning}**")
        
        if st.checkbox("💡 첫 글자 힌트 보기"):
            st.info(f"힌트: {st.session_state.subj_hint}")

        user_input = st.text_input("영단어 철자를 소문자로 입력하세요:", key="user_subj_input")

        if not st.session_state.subj_solved:
            if st.button("정답 확인하기"):
                st.session_state.subj_total += 1
                if user_input.strip().lower() == target_word.lower():
                    st.session_state.subj_correct_cnt += 1
                    st.session_state.subj_solved = True
                    st.success(f"🎉 정답입니다! 단어: **{target_word}** ({target_meaning})")
                    st.rerun()
                else:
                    if not st.session_state.subj_retry:
                        st.session_state.subj_retry = True
