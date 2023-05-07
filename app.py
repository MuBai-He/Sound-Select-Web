from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from filelock import FileLock

app = Flask(__name__)
audio_folder = r'static/audio'
audio_files = os.listdir(audio_folder)
options = ['白石 罗塞塔', '渡边柚', '林雨幕','克里斯蒂娜 琼斯','安娜 伊凡诺娃','东山 抚子','般若','德川 璃璃子','艾普曼 菲利普','“船长”丹妮斯','娜塔莉 舒尔茨','温莎 法兰','其他']  # 请替换为您的实际选项内容

# 初始化CSV文件
csv_file = 'selections.csv'
lock_file = 'selections.lock'
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=[r'User I\Wav Name'] + audio_files)
    df.to_csv(csv_file, index=False)

@app.route('/')
def index():
    return render_template('index.html', audio_files=audio_files, options=options)

@app.route('/load_more', methods=['POST'])
def load_more():
    start_index = request.get_json()['start_index']
    end_index = start_index + 10
    return jsonify({'audio_files': audio_files[start_index:end_index]})


@app.route('/save_selection', methods=['POST'])
def save_selection():
    user_ip = request.remote_addr
    audio_selection = request.get_json()

    with FileLock(lock_file):
        # 读取现有CSV文件并添加或更新记录
        df = pd.read_csv(csv_file)

        user_index = df[df[r'User I\Wav Name'] == user_ip].index

        if user_index.empty:
            new_record = pd.DataFrame(
                {r'User I\Wav Name': user_ip, audio_selection['audio_file']: audio_selection['user_selection']},
                index=[0])
            df = pd.concat([df, new_record], ignore_index=True)

        else:
            df.loc[user_index, audio_selection['audio_file']] = audio_selection['user_selection']

        df.to_csv(csv_file, index=False)

    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0',port=5000)
