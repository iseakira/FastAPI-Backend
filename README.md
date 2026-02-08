## バックエンドの起動方法

- 仮想環境は.\venv\Scripts\activate で有効か
- fastapi devでよき
- /scalarでAPIドキュメントを見れるよ

## postgressDBの見方

- pgAdmin起動
- shipmet開いてtablesのall_arrowをみたらOK

##　非同期データベースについて　session.py
モジュール読み込み時

settings.POSTGRES_URL を読む。

create_async_engine(...) で 非同期エンジン engine を作る（この時点では基本まだ接続しない。接続は後で必要になった瞬間）。

（アプリ起動時などに）create_db_tables() を呼んだとき

engine.begin() で DB接続を確保してトランザクション開始。

SQLModel.metadata.create_all を run_sync 経由で実行し、定義済みの table=True な全テーブルを作成（存在してればスキップ）。

ブロックを抜けると commit/rollback して接続を返す。

HTTPリクエストで依存注入が走り、SessionDep が必要になったとき

Depends(get_session) により get_session() が呼ばれる。

get_session() の中

sessionmaker(...) で AsyncSession を作るための工場（factory）を作る。

async_session() で セッション生成。

async with ... as session: で セッションの開始と後片付けを保証。

yield session で エンドポイントに session を渡す。

エンドポイント処理が終わった後

yield の後ろ側が再開され、async with が終了することで セッションがクローズされる（接続もプールに返る）。

※ commit()/rollback() はこのコードでは自動ではないので、必要ならエンドポイント側やCRUD層で明示的に呼ぶ設計になる。

SessionDep = Annotated[...]

「引数に session: SessionDep と書けるようにする型エイリアス」で、Depends付きのAsyncSession注入を短く書くための道具だ。

非同期エンジンとは

非同期エンジンとは、ざっくり言うと 「DBへの接続確保・クエリ実行などのI/O待ちを await で待てるようにしたSQLAlchemyのエンジン」 だ。待っている間にイベントループが他の処理（他リクエストなど）を進められる。

エンジンってそもそも何か

SQLAlchemyにおける Engine は「DBへつなぐための入口」で、

接続プールを持つ（毎回つなぎ直さず再利用）

DBドライバと通信する

セッションが内部で接続を借りる元

みたいな役割をまとめて担う。

非同期エンジン（AsyncEngine）の意味

create_async_engine(...) で作るのが AsyncEngine。特徴は：

DB接続やクエリのI/Oを 非同期で扱える

接続を取る/返す、トランザクション開始/終了などが async with / await 前提になる

その代わり、使うDBドライバも async対応が必要（例：PostgreSQLなら asyncpg）

あなたのコードだとこれ：

engine = create_async_engine(url=settings.POSTGRES_URL, echo=True)

同期エンジンとの違い（最小）
同期

create_engine(...)

実行中はそのスレッドがDB待ちで止まりやすい

FastAPIでも動くが、並行性を維持するにはスレッド運用が絡む

非同期

create_async_engine(...)

await で待ってる間、他の処理にCPUを譲れる

FastAPI（ASGI）と相性が良い

非同期エンジンを使うとコードがこう変わる

接続やトランザクションが async with になる：

async with engine.begin() as conn:
...

同期API（SQLModel.metadata.create_all）はそのまま呼べないので run_sync が必要：

await conn.run_sync(SQLModel.metadata.create_all)

重要な注意（混ぜるな危険）

非同期エンジン + AsyncSession を使うなら、DBアクセスは基本 await session.execute(...) など async流儀で統一する

同期版の Session や create_engine と混ぜると事故りやすい

必要なら、settings.POSTGRES_URL の「async用URLの書き方」（例：postgresql+asyncpg://...）と、AsyncSession での典型的なCRUD例も最小で示す。

このsessionとやらは

Session（ここでは AsyncSession）は一言でいうと 「DB操作の作業机（作業単位）」 だ。エンジンが“入口/接続プール”だとすると、セッションは“その入口から借りた接続で実際にCRUDするための窓口”になる。

Session がやっていること

SQLを実行する窓口

SELECT/INSERT/UPDATE/DELETE を投げるのは基本セッション経由だ。

トランザクション管理

「ここまでの変更を確定する（commit）」

「なかったことにする（rollback）」
をまとめる単位がセッション。

ORMの状態管理（キャッシュ/追跡）

取得したオブジェクトを「いま管理してるオブジェクト」として追跡し、

変更されたらUPDATE対象にする、などをやる（“ユニットオブワーク”）。

イメージ図

engine：接続プール付きの“会社の受付”

session：受付で借りた“会議室”
会議室の中で作業（SQL実行）して、最後に「この議事録を正式版にする＝commit」みたいな感じ

あなたの get_session() がしてること
async with async_session() as session:
yield session

リクエストが来る

セッション（作業机）を1個作ってエンドポイントに渡す

リクエストが終わったら自動でクローズして片付ける

つまり「1リクエスト = 1セッション」の典型パターンだ。

重要：このコードだと commit は自動じゃない

async with session: は closeは保証するが、基本 commit/rollbackは自分でやる設計だ。

典型例：

@app.post("/shipments")
async def create_shipment(session: SessionDep):
shipment = Shipment(...)
session.add(shipment)
await session.commit() # 確定
await session.refresh(shipment) # DB側で採番されたid等を反映
return shipment

失敗時は：

try:
...
await session.commit()
except:
await session.rollback()
raise

expire_on_commit=False って何

コミット後に、取得済みオブジェクトを「期限切れ」にして再読込を強制する挙動を止める設定だ。APIでレスポンスを返す用途だと、コミット後に属性アクセスしたら追加クエリが走る…みたいな事故を避けやすいのでよく False にする。

まとめると、**Session = クエリ実行 + トランザクション + ORM状態管理をまとめた“作業単位”**だ。
次に「SessionとConnectionの違い」も混乱ポイントなので、そこも続けて整理できる。
