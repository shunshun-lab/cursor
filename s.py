import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# メールテンプレートの定義
templates = {
    "1. 通常通知": "{recipient_name}様\n\nお世話になっております。\n生成AI塾運営事業部です。\n\n本日の[{course_name}]のURLです。\n\n{meeting_info}\n\nご不明点がございましたら、ご連絡ください。",
    "2. 講義前事前告知": "{recipient_name}様\n\nお世話になっております。\n生成AI塾運営事業部です。\n\n本日の[{course_name}]のURLです。\n\n{meeting_info}\n\nご不明点がございましたら、このkanri@kandaquantum.co.jpにご連絡ください。",
    "3. その他": "{recipient_name}様\n\nお世話になっております。\n生成AI塾運営事業部です。\n\n詳細は以下をご確認ください。\n\n{meeting_info}\n\nご不明点がございましたら、ご連絡ください。",
    "4. DAO特化型ハッカソン協業のご相談": """【協業のご相談】8月にDAO特化型ハッカソンを開催します。

ご担当者様

初めてフォームをお送りさせていただきます。
DAOATHON運営チーム、{affiliation}の{sender_name}と申します。私たちはDAOATHONというDAO特化型ハッカソン/アイディアソンの第2回目を、今年の8/7-8/20に行う計画をしております。WebX様にメディアパートナーとしてご協賛をいただいており、参加者は昨年度実績も踏まえ、学生/社会人、国内/海外、エンジニア/非エンジニアなど様々な属性を想定しております。また、ハッカソンに先駆けて、6月から全9回のDAO勉強会を開催します。詳細は添付資料に記載しておりますのでご確認いただけますと幸いです。
「100万のDAOで革命を。」のキャッチコピーのもと、DAOを一般的に普及させることで日本経済、また世界経済に貢献したいという想いで本イベントを企画しております。合同会社型DAOの設立を目指し、これまでWeb3に関わってこなかった人もオンボーディングしていく計画です。
本イベントに興味をお持ちいただけましたら、ぜひ一度カジュアルに協業のご相談をさせていただきたく考えております！お忙しい中恐縮ではございますが、30分ほどオンラインでお話させていただく機会を設けていただけると幸いです。 以下のリンクからご都合のつく日程をお選びいただければと思います。
https://calendly.com/0xdaoasia/30min?month=2024-05

また、簡単な資料を添付させていただきます。https://www.canva.com/design/DAGBVcRdlsg/YUCYbyuszpytP1Q2mb5exA/edit?utm_content=DAGBVcRdlsg&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

ご不明点等ございましたらお気軽にお問い合わせください。今後ともよろしくお願いいたします。

＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿ 
DAO-a-Thon運営チーム
{sender_name}
TEL: {sender_phone}
Email: 0xdaoasia@gmail.com
"""
}

# サイドバーの設定
st.sidebar.header('設定')
template_option = st.sidebar.selectbox(
    'メールテンプレートを選択',
    list(templates.keys())
)

# 選択されたテンプレートの内容表示
selected_template = templates[template_option]
st.sidebar.write('選択されたメールテンプレート:')
st.sidebar.text_area('メールテンプレートの内容', value=selected_template, height=200)

# メール情報の入力フィールド
st.title('メール送信アプリ')

recipient_name = st.text_input('受信者名')
recipient_email = st.text_input('受信者のメールアドレス')
course_name = st.text_input('コース名', 'C.2.3 バックエンド開発講座')
meeting_info = st.text_area('ミーティング情報', '''6月2日（日曜日）・午後1:00〜4:00
タイムゾーン: Asia/Tokyo
Google Meet の参加に必要な情報
ビデオ通話のリンク: https://meet.google.com/ege-abcu-fnd''')

# 追加された入力フィールド
sender_name = st.text_input('あなたの名前')
sender_phone = st.text_input('あなたの電話番号')
affiliation = st.text_input('あなたの所属（大学学部など）')

# メールのプレビュー
st.subheader('メールのプレビュー')

email_content = selected_template.format(
    recipient_name=recipient_name,
    course_name=course_name,
    meeting_info=meeting_info,
    sender_name=sender_name,
    sender_phone=sender_phone,
    affiliation=affiliation
)

st.text_area('メールの内容', value=email_content, height=200)

# メール送信機能


def send_email(recipient_email, subject, content):
    sender_email = "youraddress@gmail.com"
    sender_password = "yourGmailPW"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = Header(subject, 'utf-8')

    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        st.success("メールが送信されました。")
    except Exception as e:
        st.error(f"メールの送信に失敗しました: {str(e)}")


# 送信ボタン
if st.button('送信'):
    if recipient_name and recipient_email:
        send_email(recipient_email, f"【{course_name}】のご案内", email_content)
    else:
        st.error("受信者名と受信者のメールアドレスを入力してください。")
