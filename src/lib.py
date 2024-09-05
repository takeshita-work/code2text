""" ライブラリ """

import os

from tqdm import tqdm

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

    total_dirs = sum([len(dirs) for _, dirs, _ in os.walk(path)])
    with tqdm(total=total_dirs, desc="Processing", leave=False) as pbar:
        for root, _, files in os.walk(path, topdown=False):
            for name in files:
                rel_path = os.path.relpath(os.path.join(root, name), path)
                if exclude_spec.match_file(rel_path):
                    continue
                if not target_spec.match_file(name):
                    continue
                filtered_files.append(rel_path)
            pbar.update(1)

    return filtered_files

def calculate_totals(path, files):
    """
    総サイズ、総行数、総文字数、および開始位置を計算する関数

    Args:
        path (str): ファイルが存在するディレクトリのパス
        files (list of str): ファイル名のリスト

    Returns:
        tuple: 総サイズ、総行数、総文字数、ディレクトリ数x4 + ファイル名の最大値
    """
    total_size = 0
    total_lines = 0
    total_chars = 0
    info_padding = 0
    with tqdm(total=len(files), desc="Calculating totals", leave=False) as pbar:
        for file in files:
            file_path = os.path.join(path, file)
            total_size += os.path.getsize(file_path)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = sum(1 for _ in f)
                f.seek(0)
                chars = len(f.read())
            total_lines += lines
            total_chars += chars
            parts = file.split(os.sep)
            depth = len(parts) - 1
            info_padding = max(info_padding, (depth + 2) * 4 + len(parts[-1]))
            pbar.update(1)

    return total_size, total_lines, total_chars, info_padding

def generate_tree(files, show_info=False, info_padding=0):
    """ ツリーの生成 """

    def files_2_dir_tree(files):
        """
        ファイルパスのリストを基にディレクトリツリーを構築する関数

        Args:
            file_list (list of str): ファイルパスのリスト

        Returns:
            dict: ディレクトリツリーを表す辞書
        """
        dir_tree = {}  # ディレクトリツリーを格納するための空の辞書

        for file in files:
            parts = file.split(os.sep)  # ファイルパスをディレクトリごとに分割
            current_level = dir_tree  # 現在のディレクトリレベルをルートに設定

            for part in parts:
                if part not in current_level:
                    current_level[part] = {}  # 新しいディレクトリまたはファイルを追加
                current_level = current_level[part]  # 次のレベルに移動

        return dir_tree

    def format_tree(node, prefix="", base_path="", level=0):
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
            child_path = os.path.join(base_path, child)
            if show_info and os.path.isfile(child_path):
                size = os.path.getsize(child_path)
                with open(child_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = sum(1 for _ in f)
                    f.seek(0)
                    chars = len(f.read())
                info = f" ({size:,} bytes, {lines} lines, {chars} chars)"
            else:
                info = ""

            # 最後の要素には異なるプレフィックスを使用する
            if i == count - 1:
                tree_str += f"{prefix}`-- {child.ljust(info_padding - len(prefix) - 4)}{info}\n"
                new_prefix = f"{prefix}    "
            else:
                tree_str += f"{prefix}|-- {child.ljust(info_padding - len(prefix) - 4)}{info}\n"
                new_prefix = f"{prefix}|   "

            # 子ノードが辞書の場合、再帰的に関数を呼び出す
            if isinstance(node[child], dict):
                tree_str += format_tree(node[child], new_prefix, child_path, level + 1)

            pbar.update(1)

        return tree_str

    dir_tree = files_2_dir_tree(files)

    with tqdm(total=len(files), desc="Generating tree") as pbar:
        return format_tree(dir_tree, base_path=".", level=0)

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
