import streamlit as st
import pandas as pd
import plotly.express as px
import time

from datetime import datetime

# ChatGPT: https://chat.openai.com/share/5d3a8f51-4edd-411a-9c62-e153c7f2d673


st.set_page_config(
    page_title="長目: BCPチェッカー", page_icon="img/chomoku-favicon.png"
)

df = pd.read_csv("./data/bcp_test.csv")

if "current_num" not in st.session_state:
    st.session_state["current_num"] = 0

if "answers" not in st.session_state:
    st.session_state["answers"] = {}


def increment_session(answer=None):
    if answer is None and st.session_state["current_num"] == 0:
        st.session_state["current_num"] = 1
    else:
        st.session_state["answers"][st.session_state["current_num"]] = answer
        if st.session_state["current_num"] <= len(df):
            st.session_state["current_num"] += 1


def modoru_func():
    if st.session_state["current_num"] > 1:
        st.session_state["current_num"] -= 1


def susumu_func():
    if st.session_state["current_num"] > 0 or st.session_state["current_num"] < len(df):
        st.session_state["current_num"] += 1


def reset_func():
    st.session_state["current_num"] = 0
    st.session_state["answers"] = {}


def agg_answers():
    ans = list(st.session_state["answers"].values())
    nums = list(st.session_state["answers"].keys())
    df = pd.DataFrame()
    df["ans"] = ans
    df["nums"] = nums
    df["cat"] = pd.NA
    df.loc[0, "cat"] = "人的資源"
    df.loc[4, "cat"] = "物的資源"
    df.loc[8, "cat"] = "資金資源"
    df.loc[12, "cat"] = "情報資源"
    df.loc[16, "cat"] = "体制など"
    df = df.ffill()
    score = df["ans"].sum()
    dfg = df.groupby("cat", as_index=False).sum()
    dfg["ans_str"] = dfg["ans"].map(lambda x: f"{x} / 4")
    return df, score, dfg


def situation_check(score):
    if score < 6:
        return st.write(
            """緊急事態に遭遇すると、あなたの会社の事業は長期間停止し、
    廃業に追い込まれる恐れがあります。１からBCPの策定・運用に
    取り組んでください。まずは、中小企業庁の基本コースを読んでみましょう。
    https://www.chusho.meti.go.jp/bcp/contents/level_a/bcpgl_01.html
    """
        )
    elif score < 16:
        return st.write(
            """緊急事態に備える意識は高いですが、まだまだ改善点があります。
    実践的なBCPを策定し、平常時から運用を進めましょう。
    中小企業庁のBCP中級編を読んでみましょう。
    https://www.chusho.meti.go.jp/bcp/contents/level_b/bcpgl_01.html
    """
        )
    else:
        return st.write(
            """BCPの考え方に則った取り組みが進んでいるようです。
            中小企業庁のBCP中級編、上級編をチェックしてみましょう。
            https://www.chusho.meti.go.jp/bcp/contents/level_b/bcpgl_01.html
        """
        )


def show_chart(df):
    fig = px.line_polar(df, r="ans", theta="cat", line_close=True)
    fig.update_traces(fill="toself")
    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 4], "color": "black"}},
        autosize=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def display_results():
    st.header("BCPチェッカー", divider="rainbow")

    st.write("## 全ての質問に回答しました")
    st.write("### 回答結果")
    df, score, dfg = agg_answers()
    today_date = datetime.now().date()
    st.write(f"#### {today_date}時点の")
    st.write(f"御社の得点は {score} です。（20点満点中）")

    if score < 18:
        st.write("BCP取り組みの改善を行い、またチャレンジしてください！")

    situation_check(score)

    show_chart(dfg)

    st.write("**右上のケバブメニュー（３つの点）のPrintから内容をPDFで出力できます。**")
    st.write("環境変化が激しい時代に備えるため、BCPの策定をご検討の場合、長目までご相談ください。")
    st.link_button('長目のサイトへ行く', 'https://www.chomoku.info', type='primary')

    st.button("もう一度アプリを使う", on_click=reset_func)

    st.divider()
    st.write(
        "このBCPチェックアプリは、中小企業庁: BCP取り組み状況チェックを基に作成しています"
    )
    st.write("https://www.chusho.meti.go.jp/bcp/contents/level_a/bcpgl_01_3.html")
    st.write("回答されたデータは保存されません")
    st.write("作成: 合同会社長目 https://www.chomoku.info")
    # for i, answer in enumerate(st.session_state["answers"], start=1):
    #     st.write(f"質問 {i}: {answer}")


def show_quiz():

    c_num = st.session_state["current_num"]
    q_num = c_num - 1
    quiz = df.loc[q_num, "質問"]
    st.header("BCPチェッカー", divider="rainbow")

    st.title(f"質問: {c_num}")
    st.write(f"{quiz}")
    st.button("はい", on_click=increment_session, args=(1,))
    st.button("いいえ", on_click=increment_session, args=(0,))
    st.button("?", on_click=increment_session, args=(0,))

    progress = (st.session_state["current_num"]) / len(df)

    st.progress(progress)
    st.write(f"{c_num} / {len(df)}")

    st.divider()
    st.write(
        "このBCPチェックアプリは、中小企業庁: BCP取り組み状況チェックを基に作成しています"
    )
    st.write("https://www.chusho.meti.go.jp/bcp/contents/level_a/bcpgl_01_3.html")
    st.write("作成: 合同会社長目 https://www.chomoku.info")


_BCP_TEXT = """
近年、自然災害や予期せぬ事故が増加しています。こうしたリスクに対して、あなたの会社はどれだけ準備できていますか？「事業継続計画」（BCP: Business Continuity Plan）は、そんな不測の事態に備えるための重要なツールです。

## BCPとは何か？

BCPは、災害や事故が起きた時に、会社の重要な機能を維持し、できるだけ早く通常の業務に戻るための計画です。具体的には：

- 従業員の安全確保
- 重要な業務の継続
- 顧客や取引先とのコミュニケーション維持
- 財務的な影響の最小化

などが含まれます。

## BCPチェッカーの重要性

「BCPは必要だと分かっていても、どこから手をつければいいか分からない」という声をよく聞きます。そこで役立つのが「BCPチェッカー」です。

中小企業庁の指針を基に作成された20の質問に答えるだけで、あなたの会社の災害対策の現状が明確になります。このチェッカーは、人的資源、物的資源（モノと金）、情報資源、そして全体的な体制といった重要な側面をカバーしています。

## BCPチェッカーを活用しよう

BCPチェッカーの質問に答えることで、自社の強みと弱みが明確になります。「ここはできている！」「ここは要注意だな」と、次にすべきことが見えてくるのです。

BCPは一朝一夕にはできません。しかし、BCPチェッカーを使えば、今日から第一歩を踏み出せます。災害に強い会社づくりは、小さな準備の積み重ねから始まるのです。

あなたの会社の未来を守るため、今すぐBCPチェッカーを試してみませんか？ 適切な準備があれば、どんな困難な状況でも、ビジネスを継続し、迅速に回復する力を手に入れることができます。

"""


def stream_data():
    for word in _BCP_TEXT:
        yield word + " "
        time.sleep(0.04)


def show_title():
    st.header("災害などのリスクに備える：あなたの会社は本当に大丈夫？", divider="rainbow")

    # st.write_stream(stream_data)
    st.markdown(_BCP_TEXT)
    st.button(label="BCPチェッカーで会社の状況をチェック", on_click=increment_session, type='primary')

    st.divider()
    st.write(
        "このBCPチェックアプリは、中小企業庁: BCP取り組み状況チェックを基に作成しています"
    )
    st.write("https://www.chusho.meti.go.jp/bcp/contents/level_a/bcpgl_01_3.html")
    st.write("作成: 合同会社長目 https://www.chomoku.info")


if st.session_state["current_num"] == 0:
    show_title()
elif st.session_state["current_num"] <= len(df):
    show_quiz()
else:
    display_results()
