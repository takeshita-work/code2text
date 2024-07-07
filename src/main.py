import os
import sys
from pathspec import PathSpec
import pyperclip

import lib as lib
from version import BUILD_DATE

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
    help='除外するファイル. 複数指定可能.'
)
parser.add_argument(
    '-i', '--info', 
    action='store_true', 
    help='tree 表示でファイルの詳細を表示'
)
parser.add_argument(
    '-c', '--copy', 
    action='store_true', 
    help='結果をクリップボードにコピー'
)
parser.add_argument(
    '-v', '--version',
    action='store_true',
    help='ビルド日時を表示'
)
if __name__ == "__main__":
    result = ''
    try:
        args = parser.parse_args()
        
        if args.version:
            print(f"build date: {BUILD_DATE}")
            sys.exit(1)

        path = os.path.abspath(args.path)
        if not os.path.isdir(path):
            raise Exception(f"指定されたパスが存在しないか、ディレクトリではありません: {path}")

        ######################################################################
        # 対象ファイルの取得
        ######################################################################
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
        files = lib.get_files(path, target_spec, exclude_spec)

        ######################################################################
        # 総サイズと総ライン数と総文字数の計算
        ######################################################################
        total_size, total_lines, total_chars, info_padding = lib.calculate_totals(path, files)

        ######################################################################
        # 結果の取得と表示
        ######################################################################
        print(f"path: {path}")
        print("")
        print(f"total size : {total_size:,} bytes")
        print(f"total lines: {total_lines}")
        print(f"total chars: {total_chars}")
        
        # ツリー
        if args.mode in ('tree', 'all'):
            tree = (
                f"```tree\n"
                f"{lib.normalize_path(args.path)}\n"
                f"{lib.generate_tree(files, show_info=args.info, info_padding=info_padding)}"
                f"```"
            )
            print("")
            print(tree)
            result += tree
        
        # ファイルコンテンツ, クリップボードへのコピー
        if (
            args.mode in ('code', 'all') or
            args.copy 
        ):
            # 処理継続の確認
            print("")
            input_result = input("処理を継続しますか？ (y/n): ")
            if input_result.lower() != 'y':
                print("処理を中断しました。")
                sys.exit(1)

            # ファイルコンテンツ
            if args.mode in ('code', 'all'):
                content = f"{lib.generate_files_content(path, files)}"
                print("")
                print(content)
                result += f"\n\n{content}"

            # クリップボードへのコピー
            if args.copy:
                pyperclip.copy(result)
                print("")
                print("クリップボードにコピーしました")

    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
