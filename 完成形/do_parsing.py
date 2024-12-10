# #構文解析
from collections import defaultdict
from filler_to_newtext import morphological_analysis, load_ipadic_dict

# ノード
class SyntaxTreeNode:
    def __init__(self, word, pos, children=None):
        self.word = word
        self.pos = pos
        self.children = children if children else []

    def __repr__(self):
        return f"{self.word}/{self.pos} -> {['/'.join([child.word, child.pos]) for child in self.children]}"


def dependency_analysis_with_syntax_tree(text, dictionary):
    # 形態素解析の結果を取得
    result = morphological_analysis(text, dictionary)
    print("形態素解析結果:", result)

    # 全文の構文木を保持するリスト
    syntax_trees = []
    all_dependencies = []

    # 各文の解析
    for analysis in result:
        dependencies = defaultdict(list)
        nodes = {}

        # ノードを作成
        for word, pos, read in analysis:
            if is_directional(word) and pos == "名詞":
                pos = "副詞(方向の可能性あり)"
            nodes[word] = SyntaxTreeNode(word, pos)

        # 動詞への依存候補を収集し、最も近い（後方優先）動詞に割り当てる
        for i, (word, pos, read) in enumerate(analysis):
            if pos in {"名詞", "副詞", "形容詞", "副詞(方向の可能性あり)", "数詞", "英字", "記号", "距離"}:
                # 名詞や副詞、形容詞の依存先動詞を探す
                closest_verb = None
                min_distance = float("inf")
                for j in range(i + 1, len(analysis)):  # 後方優先で動詞を探索
                    other_word, other_pos, other_read = analysis[j]
                    if other_pos == "動詞":
                        distance = abs(i - j)
                        if distance < min_distance:
                            closest_verb = other_word
                            min_distance = distance

                if closest_verb:
                    dependencies[closest_verb].append(word)
                    nodes[closest_verb].children.append(nodes[word])

                    # 助詞が続く場合、その助詞も動詞に従属
                    if i + 1 < len(analysis) and analysis[i + 1][1] == "助詞":
                        particle_word = analysis[i + 1][0]
                        dependencies[word].append(particle_word)
                        nodes[word].children.append(nodes[particle_word])
            

        # 動詞ごとに構文木を作成
        root_nodes = [node for node in nodes.values() if node.pos == "動詞"]
        for root_node in root_nodes:
            syntax_tree = [root_node]
            visited_nodes = set()
            add_children_to_tree(root_node, visited_nodes)
            syntax_trees.append(syntax_tree)

        all_dependencies.append(dependencies)

    """
    # 依存関係の出力
    print("依存関係:")
    for dependencies in all_dependencies:
        for word, dependents in dependencies.items():
            print(f"{word} -> {', '.join(dependents)}")
    
    # 構文木の出力
    print("\n構文木:")
    for syntax_tree in syntax_trees:
        for root in syntax_tree:
            print_tree(root, set())
    """
    

    del dependencies  # メモリ解放
    
    return syntax_trees


# 副詞(方向)かどうかを判定
def is_directional(word):
    # 「右」「左」などをチェック
    directional_words = {"右", "左", "上", "下", "前", "後ろ"}
    return word in directional_words

# 副詞的な名詞かどうかを判定
def is_adverbial_noun(word, index, analysis):
    if index + 1 < len(analysis):
        next_word, next_pos, _ = analysis[index + 1]
        if next_pos == "助詞" and next_word in {"に", "で"}:
            return True
        if next_pos == "動詞":
            return True
    return False

# 子ノードを追加するヘルパー関数
def add_children_to_tree(node, visited_nodes):
    for child in node.children:
        if child not in visited_nodes:
            visited_nodes.add(child)
            add_children_to_tree(child, visited_nodes)

# 構文木を階層的に出力する
def print_tree(node, visited_nodes, depth=0):
    # 再帰的にノードを出力する前に訪問済みチェック
    if node in visited_nodes:
        return
    visited_nodes.add(node)
    
    print("  " * depth + f"{node.word} ({node.pos})")
    for child in node.children:
        print_tree(child, visited_nodes, depth + 1)

"""
# メイン実行部分
if __name__ == "__main__":
    ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"

    # load_ipadic_dict：辞書を読み込む
    dictionary = load_ipadic_dict(ipadic_dir_path)

    text = "先に右に回る前に後ろに100進んで"
    dependency_analysis_with_syntax_tree(text, dictionary)
"""