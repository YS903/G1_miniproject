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
    
    # 새로운 4단계 메뉴 구성
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

        if "fc_index" not in st.session_state:
            st.session_state.fc_index = 0
            st.session_state.show_meaning = False

        # 무작위로 단어 샘플링 또는 순차 진행 중 선택 (여기서는 랜덤 카드 뽑기 방식 적용)
        if st.button("🔀 무직위 카드 뽑기") or "fc_word" not in st.session_state:
            row = df.sample(1).iloc[0]
            st.session_state.fc_word = str(row[word_col]).strip()
            st.session_state.fc_meaning = str(row[meaning_col]).strip()
            st.session_state.show_meaning = False

        word = st.session_state.fc_word
        meaning = st.session_state.fc_meaning

        # 카드 UI 디자인
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

        if "quiz_word" not in st.session_state or st.button("🔄 다음 문제 출제"):
            correct_row = df.sample(1).iloc[0]
            st.session_state.q_word = str(correct_row[word_col]).strip()
            st.session_state.q_correct = str(correct_row[meaning_col]).strip()
            
            wrong_rows = df[df[word_col] != st.session_state.q_word].sample(3)
            options = list(wrong_rows[meaning_col].values) + [st.session_state.q_correct]
            random.shuffle(options)
            st.session_state.q_options = options

        st.markdown(f"### Q. 다음 영단어의 뜻은 무엇일까요?\n# **{st.session_state.q_word}**")
        choice = st.radio("보기를 선택하세요:", st.session_state.q_options, key="quiz_radio")

        if st.button("정답 제출하기"):
            if choice == st.session_state.q_correct:
                st.success("🎉 정답입니다! 훌륭해요 👏")
            else:
                st.error(f"❌ 틀렸습니다. 정답은 **{st.session_state.q_correct}** 입니다.")

    elif menu == "✍️ 서술형 스펠링 테스트":
        st.header("✍️ 서술형 스펠링 테스트 (뜻 ➔ 영단어)")
        st.write("제시된 한국어 뜻을 보고 올바른 영단어 철자를 직접 입력해 보세요.")

        if "subj_word" not in st.session_state or st.button("🔄 다른 문제 풀기"):
            rand_row = df.sample(1).iloc[0]
            st.session_state.subj_word = str(rand_row[word_col]).strip()
            st.session_state.subj_meaning = str(rand_row[meaning_col]).strip()
            # 첫 글자 힌트 제공
            w = st.session_state.subj_word
            st.session_state.subj_hint = w[0] + " _ " * (len(w) - 1)

        target_word = st.session_state.subj_word
        target_meaning = st.session_state.subj_meaning

        st.markdown(f"### 뜻: **{target_meaning}**")
        
        if st.checkbox("💡 첫 글자 힌트 보기"):
            st.info(f"힌트: {st.session_state.subj_hint}")

        user_input = st.text_input("영단어 철자를 소문자로 입력하세요:", key="user_subj_input")

        if st.button("정답 확인하기"):
            if user_input.strip().lower() == target_word.lower():
                st.success(f"🎉 정답입니다! 단어: **{target_word}** ({target_meaning})")
            else:
                st.error(f"❌ 틀렸습니다. 정답은 **{target_word}** 입니다.")

    elif menu == "⏱️ 타임어택 배틀":
        st.header("⏱️ 타임어택 스피드 배틀 게임")
        st.write("제한 시간(10초) 동안 최대한 많은 객관식 문제를 맞춰 최고 기록에 도전하세요!")

        if "battle_active" not in st.session_state:
            st.session_state.battle_active = False
            st.session_state.battle_score = 0

        if not st.session_state.battle_active:
            if st.button("🚀 배틀 시작하기"):
                st.session_state.battle_active = True
                st.session_state.battle_start_time = time.time()
                st.session_state.battle_score = 0
                
                # 첫 문제 설정
                row = df.sample(1).iloc[0]
                st.session_state.b_word = str(row[word_col]).strip()
                st.session_state.b_correct = str(row[meaning_col]).strip()
                w_rows = df[df[word_col] != st.session_state.b_word].sample(3)
                opts = list(w_rows[meaning_col].values) + [st.session_state.b_correct]
                random.shuffle(opts)
                st.session_state.b_opts = opts
                st.rerun()
        else:
            elapsed = time.time() - st.session_state.battle_start_time
            remaining = max(0, 10 - int(elapsed))

            if remaining > 0:
                st.metric(label="⏳ 남은 시간", value=f"{remaining}초")
                st.markdown(f"### 현재 점수: 🏆 {st.session_state.battle_score}점")
                
                st.write(f"단어: **{st.session_state.b_word}**")
                ans = st.radio("뜻을 고르세요:", st.session_state.b_opts, key="battle_radio")

                if st.button("정답 제출"):
                    if ans == st.session_state.b_correct:
                        st.session_state.battle_score += 1
                        st.success("정답! +1점")
                    else:
                        st.error(f"오답! 정답은 '{st.session_state.b_correct}' 였습니다.")
                    
                    # 곧바로 다음 문제 생성
                    row = df.sample(1).iloc[0]
                    st.session_state.b_word = str(row[word_col]).strip()
                    st.session_state.b_correct = str(row[meaning_col]).strip()
                    w_rows = df[df[word_col] != st.session_state.b_word].sample(3)
                    opts = list(w_rows[meaning_col].values) + [st.session_state.b_correct]
                    random.shuffle(opts)
                    st.session_state.b_opts = opts
                    st.rerun()
                
                time.sleep(1)
                st.rerun()
            else:
                st.warning(f"⏰ 시간이 종료되었습니다! 최종 점수: **{st.session_state.battle_score}점**")
                if st.button("🔄 다시 도전하기"):
                    st.session_state.battle_active = False
                    st.rerun()
else:
    st.warning("데이터를 로드할 수 없습니다.")
