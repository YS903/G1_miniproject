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

# 데이터 로드 함수 (voca_3000.csv 파일 사용)
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
    # 2열(인덱스 1)을 영단어, 4열(인덱스 3)을 뜻으로 정확히 지정
    word_col = df.columns[1]   # 2번째 열 (영단어)
    meaning_col = df.columns[3] # 4번째 열 (뜻)
    
    st.sidebar.title("📚 G1 Vocabulary App")
    st.sidebar.markdown("중학교 1학년 필수 영단어 마스터!")
    
    menu = st.sidebar.selectbox(
        "학습 메뉴 선택",
        [
            "🏠 홈 소개",
            "✍️ 단어 스펠링 연습 (Typing)",
            "📖 예문 학습 (Example Sentences)",
            "❓ 객관식 퀴즈 (Multiple-Choice)",
            "⏱️ 타임어택 배틀 (Timed Battle)"
        ]
    )

    if menu == "🏠 홈 소개":
        st.title("🌟 G1 English Vocabulary App")
        st.write("환영합니다! 중학교 1학년 수준의 어휘를 재미있게 익히고 테스트할 수 있는 공간입니다.")
        st.info("👈 왼쪽 사이드바에서 원하는 학습 메뉴를 선택하여 시작하세요!")
        st.subheader("📊 데이터 현황")
        st.write(f"현재 연동된 전체 학습 단어 수: **{len(df)}개**의 교육과정 기초어휘")

    elif menu == "✍️ 단어 스펠링 연습 (Typing)":
        st.header("✍️ 단어 스펠링 타이핑 연습")
        st.write("뜻을 보고 알맞은 영단어 철자를 직접 입력해 보세요!")
        
        if "typing_word" not in st.session_state or st.button("🔄 다른 단어 뽑기"):
            rand_row = df.sample(1).iloc[0]
            st.session_state.typing_word = str(rand_row[word_col]).strip()
            st.session_state.typing_meaning = str(rand_row[meaning_col]).strip()
            st.session_state.typing_hint = st.session_state.typing_word[0] + " _ " * (len(st.session_state.typing_word) - 1)

        target_word = st.session_state.typing_word
        target_meaning = st.session_state.typing_meaning

        st.markdown(f"### 뜻: **{target_meaning}**")
        
        if st.checkbox("💡 첫 글자 힌트 보기"):
            st.info(f"힌트: {st.session_state.typing_hint}")

        user_input = st.text_input("영단어 철자를 입력하세요 (소문자 입력):", key="user_typing")

        if st.button("정답 확인"):
            if user_input.strip().lower() == target_word.lower():
                st.success(f"🎉 정답입니다! 단어: **{target_word}** ({target_meaning})")
            else:
                st.error(f"❌ 틀렸습니다. 정답은 **{target_word}** 입니다.")

    elif menu == "📖 예문 학습 (Example Sentences)":
        st.header("📖 문맥 속 단어 학습")
        st.write("단어와 뜻을 활용해 자동으로 생성된 예문입니다.")

        # 버튼을 누르거나 처음 들어왔을 때 새로운 단어 선택
        if "ex_word" not in st.session_state or st.button("🔄 다른 예문 보기"):
            sample_row = df.sample(1).iloc[0]
            st.session_state.ex_word = str(sample_row[word_col]).strip()
            st.session_state.ex_meaning = str(sample_row[meaning_col]).strip()

        word = st.session_state.ex_word
        meaning = st.session_state.ex_meaning

        st.markdown(f"### 🎯 단어: **{word}** ({meaning})")
        
        # 파일에 예문이 없으므로 단어를 포함한 문장을 자동 생성하여 표시
        auto_example = f"This is an example sentence using the word **{word}** ({meaning})."
        st.markdown(f"> **자동 생성 예문:** {auto_example}")

    elif menu == "❓ 객관식 퀴즈 (Multiple-Choice)":
        st.header("❓ 어휘 객관식 퀴즈")
        if "quiz_word" not in st.session_state or st.button("🔄 다음 문제 출제"):
            correct_row = df.sample(1).iloc[0]
            st.session_state.q_word = str(correct_row[word_col])
            st.session_state.q_correct = str(correct_row[meaning_col])
            wrong_rows = df[df[word_col] != st.session_state.q_word].sample(3)
            options = list(wrong_rows[meaning_col].values) + [st.session_state.q_correct]
            random.shuffle(options)
            st.session_state.q_options = options

        st.markdown(f"### Q. 다음 단어의 뜻은 무엇일까요?\n# **{st.session_state.q_word}**")
        choice = st.radio("보기를 선택하세요:", st.session_state.q_options)

        if st.button("제출하기"):
            if choice == st.session_state.q_correct:
                st.success("🎉 정답입니다! 짝짝짝 👏")
            else:
                st.error(f"❌ 틀렸습니다. 정답은 **{st.session_state.q_correct}** 입니다.")

    elif menu == "⏱️ 타임어택 배틀 (Timed Battle)":
        st.header("⏱️ 타임어택 스피드 배틀")
        st.write("제한 시간(10초) 동안 최대한 많은 문제를 맞춰보세요!")

        # 세션 상태 초기화
        if "battle_active" not in st.session_state:
            st.session_state.battle_active = False
            st.session_state.battle_score = 0

        # 게임 시작 버튼
        if not st.session_state.battle_active:
            if st.button("🚀 배틀 시작!"):
                st.session_state.battle_active = True
                st.session_state.battle_start_time = time.time()
                st.session_state.battle_score = 0
                # 첫 문제 세팅
                row = df.sample(1).iloc[0]
                st.session_state.b_word = str(row[word_col])
                st.session_state.b_correct = str(row[meaning_col])
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
                    
                    # 바로 다음 문제 출제
                    row = df.sample(1).iloc[0]
                    st.session_state.b_word = str(row[word_col])
                    st.session_state.b_correct = str(row[meaning_col])
                    w_rows = df[df[word_col] != st.session_state.b_word].sample(3)
                    opts = list(w_rows[meaning_col].values) + [st.session_state.b_correct]
                    random.shuffle(opts)
                    st.session_state.b_opts = opts
                    st.rerun()
                
                # 실시간으로 화면이 갱신되도록 1초 대기 후 리프레시
                time.sleep(1)
                st.rerun()
            else:
                st.warning(f"⏰ 시간이 종료되었습니다! 최종 점수: **{st.session_state.battle_score}점**")
                if st.button("🔄 다시 도전하기"):
                    st.session_state.battle_active = False
                    st.rerun()
else:
    st.warning("데이터를 로드할 수 없습니다.")
