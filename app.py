import streamlit as st
import os
import pickle
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# メールテンプレートの定義
templates = {
    "1. 協業のご相談": """{recipient_name}様

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
TEL: {phone_number}
Email: 0xdaoasia@gmail.com
""",
    "2. 講義前事前告知": """{recipient_name}様

お世話になっております。
生成AI塾運営事業部です。

本日の[{course_name}]のURLです。

{meeting_info}

ご不明点がございましたら、このkanri@kandaquantum.co.jpにご連絡ください。
""",
    "3. その他": """{recipient_name}様

お世話になっております。
生成AI塾運営事業部です。

詳細は以下をご確認ください。

{meeting_info}

ご不明点がございましたら、ご連絡ください。
""",
    "4. 通常通知": """{recipient_name}様

お世話になっております。
生成AI塾運営事業部です。

本日の[{course_name}]のURLです。

{meeting_info}

ご不明点がございましたら、ご連絡ください。
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

# 受信者情報の入力フィールド
num_recipients = st.number_input('受信者の数', min_value=1, step=1, value=1)
recipient_names = []
recipient_emails = []

for i in range(num_recipients):
    recipient_names.append(st.text_input(f'受信者名 {i+1}'))
    recipient_emails.append(st.text_input(f'受信者のメールアドレス {i+1}'))

course_name = st.text_input('タイトル', '【協業のご相談】8月にDAO特化型ハッカソンを開催します。')
meeting_info = st.text_area('ミーティング情報', '''6月2日（日曜日）・午後1:00〜4:00
タイムゾーン: Asia/Tokyo
Google Meet の参加に必要な情報
ビデオ通話のリンク: https://meet.google.com/ege-abcu-fnd''')

# 新しいテンプレート用の入力フィールド
sender_name = st.text_input('送信者名')
phone_number = st.text_input('電話番号')
affiliation = st.text_input('所属（大学学部など）')

# メールのプレビュー
st.subheader('メールのプレビュー')

email_contents = []
for i in range(num_recipients):
    email_content = selected_template.format(
        recipient_name=recipient_names[i],
        course_name=course_name,
        meeting_info=meeting_info,
        sender_name=sender_name,
        phone_number=phone_number,
        affiliation=affiliation
    )
    email_contents.append(email_content)
    st.text_area(f'メールの内容 {i+1}', value=email_content, height=200)

# Gmail APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    # トークンが保存されているか確認
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # トークンが無効な場合、再認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8501)  # ポート番号を変更
        # トークンを保存
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def send_email(recipient_email, subject, content):
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEMultipart()
    message['From'] = 'me'
    message['To'] = recipient_email
    message['Subject'] = Header(subject, 'utf-8')

    message.attach(MIMEText(content, 'plain', 'utf-8'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw_message}

    try:
        message = service.users().messages().send(userId='me', body=body).execute()
        st.success(f"メールが{recipient_email}に送信されました。")
    except Exception as e:
        st.error(f"メールの送信に失敗しました: {str(e)}")

# 送信ボタン
if st.button('送信'):
    for i in range(num_recipients):
        if recipient_names[i] and recipient_emails[i]:
            send_email(recipient_emails[i], f"{course_name}", email_contents[i])
        else:
            st.error(f"受信者名と受信者のメールアドレスを入力してください。 (受信者 {i+1})")