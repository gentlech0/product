# ③ Docker を用いたタイムトラッカー導入 (標準化済み)  
  
## 作成中  
これも載せるコードはないので内容をイラストで説明する  
  
## 特徴  
◯ 各設計者の担当作業(時間、項目)をGUIで確認できる  
◯ データ加工後、各設計者のスキルマップを可視化できる予定 (現在データ蓄積中)
◯ 新規プロジェクトに対して「最適チーム構成」「予測人日数」が割り出せる予定  

## 仕様 (公式アプリをカスタマイズ)
① 社員にアカウントとパスワードを配布済み。  
　 各自Webサーバーにログインし、作業項目、時間、内容を適宜記載する  
② 社員(一般ユーザー権限)の作業時間が自動集計され、  
　 部署長(admin権限)は社員の作業内容を表・グラフで確認できる  
③ 「機種名」「設計段階(例：試作、量産など)「項目(例：検討、基板設計、講習会など)」  
　　「詳細(例：締切、進捗率、作業内容)」が自動集計される

## 公式サイト  
https://www.kimai.org/

## 構築手順
① 第３設計部の共有PC (Windows 10)を使用  
② Hyper-Vを有効化する  
③ 仮想PCにUbuntu Serverをインストールする  
④ UbuntuにDocker、Docker Composeをインストールする  
⑤ Docker ComposeでKimai(with mysql + apache)のコンテナを起動する  
    https://www.kimai.org/documentation/docker-compose.html  
⑥ コンテナの中でadminアカウントを作成する  
    docker exec -ti kimai /opt/kimai/bin/console kimai:user:create admin admin@example.com ROLE_SUPER_ADMIN  
⑦ Ubuntuの有線LANが「管理対象外」になる問題を修正する  
⑧ ネットワークのルーティングを構築する
⑨ 自動バックアップ体制を構築する (後で記述)