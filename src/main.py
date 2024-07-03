import os
from pathspec import PathSpec
import pyperclip

def get_files(path, target_spec, exclude_spec):
    """
    指定されたディレクトリ内のファイルをフィルタリングしてリストとして返す関数

    Args:
        path (str): 検索を開始するディレクトリのパス
        target_spec (object): ターゲットとするファイル名のパターンを指定するオブジェクト
                              (例えば、`fnmatch` モジュールや `pathspec` モジュールを使用したパターン)
        exclude_spec (object): 除外するファイル名のパターンを指定するオブジェクト
                               (例えば、`fnmatch` モジュールや `pathspec` モジュールを使用したパターン)

    Returns:
        list of str: 指定された条件に一致するファイルの相対パスのリスト
    """
    filtered_files = []
    for root, _, files in os.walk(path, topdown=False):
        for name in files:
            rel_path = os.path.relpath(os.path.join(root, name), path)
            if exclude_spec.match_file(rel_path):
                continue
            if not target_spec.match_file(name):
                continue
            filtered_files.append(rel_path)

    return filtered_files


def generate_tree(files):
    def files_2_dir_tree(files):
        """
        ファイルパスのリストを基にディレクトリツリーを構築する関数

        Args:
            file_list (list of str): ファイルパスのリスト

        Returns:
            dict: ディレクトリツリーを表す辞書
        """
        import os
        dir_tree = {}  # ディレクトリツリーを格納するための空の辞書

        for file in files:
            parts = file.split(os.sep)  # ファイルパスをディレクトリごとに分割
            current_level = dir_tree  # 現在のディレクトリレベルをルートに設定

            for part in parts:
                if part not in current_level:
                    current_level[part] = {}  # 新しいディレクトリまたはファイルを追加
                current_level = current_level[part]  # 次のレベルに移動
        
        return dir_tree

    def format_tree(node, prefix=""):
        """
        辞書構造のディレクトリツリーを再帰的に読み込み、ツリー構造を文字列として返す関数

        Args:
            node (dict): ディレクトリツリーを表す辞書
            prefix (str): 各レベルのインデントを表す文字列

        Returns:
            str: ツリー構造を表す文字列
        """
        tree_str = ""
        # ファイルとディレクトリのリストを取得
        children = list(node.keys())
        # ファイルとディレクトリの数を取得
        count = len(children)

        for i, child in enumerate(children):
            # 最後の要素には異なるプレフィックスを使用する
            if i == count - 1:
                tree_str  += f"{prefix}`-- {child}\n"
                new_prefix = f"{prefix}    "
            else:
                tree_str  += f"{prefix}|-- {child}\n"
                new_prefix = f"{prefix}|   "

            # 子ノードが辞書の場合、再帰的に関数を呼び出す
            if isinstance(node[child], dict):
                tree_str += format_tree(node[child], new_prefix)

        return tree_str

    dir_tree = files_2_dir_tree(files)
    return format_tree(dir_tree)


def normalize_path(path):
    """
    ファイルパスの区切り文字を "/" に統一する関数

    Args:
        file_path (str): 変換するファイルパス

    Returns:
        str: 区切り文字が "/" に統一されたファイルパス
    """
    return path.replace("\\", "/").replace("//", "/")  # "\\"を"/"に、"//"を"/"に置換


def generate_files_content(path, files):
    """
    指定されたファイルの内容を取得し、指定された形式で文字列として返す関数

    Args:
        path (str): ファイルが存在するディレクトリのパス
        files (list of str): ファイル名のリスト

    Returns:
        str: 指定された形式で結合されたファイルの内容
    """
    content = ""
    
    for file in files:
        file_path = os.path.join(path, file)
        content += f"\n```{normalize_path(file)}\n"
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content += f.read()
        content += "\n```\n"

    return content


import argparse
parser = argparse.ArgumentParser(
    prog='code2text',
    add_help=True,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument(
    'path', 
    nargs='?', 
    default='.', 
    help='対象ディレクトリのパス. 指定がなければカレントディレクトリ.'
)
parser.add_argument(
    '-m', '--mode', 
    choices=['code', 'tree', 'all'], 
    default='all', 
    help='code または tree を指定. 指定がなければ両方表示される. '
)
parser.add_argument(
    '-t', '--target', 
    nargs='+', 
    default=['*'],
    help='対象とするファイル. 複数指定可能.'
)
parser.add_argument(
    '-e', '--exclude', 
    nargs='+',
    default=[],
    help='対象とするファイル. 複数指定可能.'
)

if __name__ == "__main__":
    result = ''
    try:
        args = parser.parse_args()

        path = os.path.abspath(args.path)
        if not os.path.isdir(path):
            raise Exception(f"指定されたパスが存在しないか、ディレクトリではありません: {path}")
        result = f"path: {normalize_path(args.path)}"

        #############################
        # 対象ファイルの取得
        #############################
        # 対象外条件のPathSpecの作成
        gitignore_path = os.path.join(path, '.gitignore') # .gitignoreの読み込みとパース
        gitignore_patterns = []
        if os.path.exists(gitignore_path):
            with open(gitignore_path) as f:
                gitignore_patterns = f.read().splitlines()
        
        exclude_patterns = (['.git', '.gitignore']) + gitignore_patterns + (args.exclude)
        exclude_spec = PathSpec.from_lines('gitwildmatch', exclude_patterns)

        # 対象条件のPathSpecの作成
        target_patterns = args.target
        target_spec = PathSpec.from_lines('gitwildmatch', target_patterns)

        # 対象ファイルの取得
        files = get_files(path, target_spec, exclude_spec)

        #############################
        # ツリー
        #############################
        if args.mode in ('tree', 'all'):
            result += f"\n\n```tree\n{normalize_path(args.path)}\n{generate_tree(files)}```"
        
        #############################
        # ファイルコンテンツ
        #############################
        if args.mode in ('code', 'all'):
            result += f"\n\n{generate_files_content(path, files)}"

        #############################
        # 出力・クリップボードへのコピー
        #############################
        max_length = 5000
        print(f"結果文字数: {len(result)}")
        if len(result) > max_length:
            print(f"テキストの長さが {max_length} 文字を超えています。コピーしますか？ (y/n)")
            if input().lower() != 'y':
                print("コピーをキャンセルしました。")
                exit(1)

        pyperclip.copy(result)
        print(result)
        print("\nクリップボードにコピーしました")

    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)