# code2text

- 指定されたディレクトリ内のファイルをフィルタリングして対象とする
- 対象ファイルのディレクトリツリーの生成と表示
- 対象ファイルの内容の表示
- 内容をクリップボードにコピー

## 実行

```
code2text.exe [path] [-m|--mode <mode>] [-t|--target <target>] [-e|--exclude <exclude>] [-i] [-c]
```

- path: 対象ディレクトリのパス（指定がなければカレントディレクトリ）
- -m, --mode: code または tree を指定（指定がなければ両方表示）
- -t, --target: 対象とするファイル（複数指定可能）
- -e, --exclude: 除外するファイル（複数指定可能）
- -i, --info: tree 表示でファイルの詳細を表示
- -c, --copy: 結果をクリップボードにコピー

- -v, --version: ビルド日時を表示
- -h, --help: ヘルプの表示

# 開発

実行環境
```
> python -V
Python 3.11.1
```

## ディレクトリ構造

```
|-- .venv               : 仮想環境
|-- build               : exe化 するときに生成される
|-- dist
|   `-- code2text.exe   : exe化したファイル
|-- scripts
|   |-- build.ps1
|   `-- run_python.ps1
|-- src
|   `-- main.py
|-- README.md
`-- requirements.txt
```

## 仮想環境の構築

1. 仮想環境の作成
    ```
    python -m venv .venv
    ```

1. 仮想環境のアクティベート
    ```
    ./.venv/Scripts/activate
    (.venv) > 
    ```

1. pip の更新

    仮想環境 をアクティベートした状態で実行する
    ```
    (.venv) > python -m pip install --upgrade pip
    ```

1. 必要なパッケージの導入

    仮想環境 をアクティベートした状態で実行する
    ```
    (.venv) >  pip install -r ./requirements.txt
    ```

## 実行

- python のコードとして実行する
    ```
    ./script/run_python.ps1 [path] [-m|--mode <mode>] [-t|--target <target>] [-e|--exclude <exclude>] [-i] [-c]
    ```

- ビルド

    ビルドのみの実行
    ```
    ./script/build.ps1
    ```

    バージョン（ビルド日時）を更新して、ビルドを実行
    ```
    ./script/build_versioning.ps1
    ```
