📌 RollSyncPro2

多軸ロール制御・巻取り計算・速度同期を行う Streamlit アプリ

RollSyncPro2 は、複数ロールの速度同期、巻取り計算、運転シミュレーション、
スケジュール運転、ログ管理などを一体化した 産業向け制御支援アプリ です。

Python + Streamlit で構築され、
現場オペレーションの効率化と安全性向上を目的としています。

🚀 主な機能

1. ロール速度同期（Roll Control）
マスター/スレーブ方式の速度同期

プーリー比・速度差（%）のリアルタイム反映

表面速度・移動距離の自動計算

グループ単位でのマスター自動選択


2. 巻取り計算（Winding Calculation）
巻取り長さ

ロール重量

ロール径

残り運転時間

残量（%）
リアルタイムで自動計算。


3. 運転シミュレーション（Simulation）
加速距離・減速距離の自動計算

速度プロファイルのリアルタイム描画

走行距離の積算

運転時間の自動算出


4. スケジュール運転（Schedule Run）
A/B プロファイルの切替

繰り返し運転

待機時間設定

実行ログの記録


5. ログ管理（Operation Log）
最新 200 件のログを表示

CSV エクスポート

運転履歴の確認が容易


🛠️ インストール方法
1. リポジトリをクローン
コード
git clone https://github.com/kojostyle/RollSyncPro2.git
cd RollSyncPro2
2. 仮想環境を作成
コード
python -m venv .venv
3. 仮想環境を有効化
Windows:

コード
.venv\Scripts\activate
4. 必要パッケージをインストール
コード
pip install -r requirements.txt
▶ アプリの起動
コード
streamlit run app.py
ブラウザが自動で開き、アプリが起動します。

📁 ディレクトリ構成
コード
RollSyncPro2/
│  app.py
│  requirements.txt
│  style.css
│  winding_calc.py
│  app_settings.json
│  アプリ起動方法.txt
│  .gitignore
│
├─ ui/        # 各ページのUI
├─ logic/     # 計算ロジック
├─ utils/     # 共通関数
├─ pages/     # Streamlit pages
└─ assets/    # 画像・アイコン
📜 ライセンス
このプロジェクトは個人利用を前提としています。
商用利用や再配布を行う場合はご相談ください。