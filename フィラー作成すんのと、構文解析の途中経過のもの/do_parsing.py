import os
from collections import defaultdict
from filler_to_newtext import morphological_analysis, load_ipadic_dict 

#ノード
class SyntaxTreeNode:
    def __init__(self, word, pos, children=None):
        self.word = word
        self.pos = pos
        self.children = children if children else []

    def __repr__(self):
        return f"({self.word}/{self.pos} -> {[child.word for child in self.children]})"


def dependency_analysis_with_syntax_tree(text, dictionary):
    # 形態素解析の結果を取得
    result = morphological_analysis(text, dictionary)
    
    # 全文の構文木を保持するリスト
    syntax_tree = []
    
    # 各文の解析
    for analysis in result:
        # 依存関係を格納する辞書
        dependencies = defaultdict(list)
        nodes = {}  # 単語に対応するノードを格納する辞書
        
        # ノードを作成
        for word, pos, read in analysis:
            nodes[word] = SyntaxTreeNode(word, pos)

        # 依存関係を構築
        for i, (word, pos, read) in enumerate(analysis):
            #動詞の主語と目的語を探す
            if pos == "動詞":
                for j in range(len(analysis)):
                    prev_word, prev_pos, prev_read = analysis[j]
                    # 主語（「は」を持つ名詞）
                    if (
                        prev_pos == "名詞" and 
                        j + 1 < len(analysis) and 
                        analysis[j + 1][1] == "助詞" and 
                        analysis[j + 1][0] == "は"
                    ):
                        dependencies[word].append(prev_word)
                        nodes[word].children.append(nodes[prev_word])
                    # 目的語（「を」を持つ名詞）
                    elif (
                        prev_pos == "名詞" and 
                        j + 1 < len(analysis) and 
                        analysis[j + 1][1] == "助詞" and 
                        analysis[j + 1][0] == "を"
                    ):
                        dependencies[word].append(prev_word)
                        nodes[word].children.append(nodes[prev_word])
                    # 補語（「に」を持つ名詞）
                    elif (
                        prev_pos == "名詞" and 
                        j + 1 < len(analysis) and 
                        analysis[j + 1][1] == "助詞" and 
                        analysis[j + 1][0] == "に"
                    ):
                        dependencies[word].append(prev_word)
                        nodes[word].children.append(nodes[prev_word])

            elif pos == "助詞":
                # 助詞が名詞に依存している関係を設定
                for j in range(i - 1, -1, -1):
                    prev_word, prev_pos, prev_read = analysis[j]
                    if prev_pos == "名詞":
                        dependencies[prev_word].append(word)
                        nodes[prev_word].children.append(nodes[word])
                        break

            # 修飾する名詞を探す
            elif pos == "形容詞":
                if i + 1 < len(analysis):
                    next_word, next_pos, next_read = analysis[i + 1]
                    if next_pos == "名詞":
                        dependencies[word].append(next_word)
                        nodes[word].children.append(nodes[next_word])
                        # 構文木に形容詞を追加
                        if nodes[word] not in syntax_tree:
                            syntax_tree.append(nodes[word])

        # 動詞を優先してルートノードに設定
        root_nodes = [node for node in nodes.values() if node.pos == "動詞"]
        if not root_nodes:  # 動詞がない場合は名詞を代わりにルートノードとする
            root_nodes = [node for node in nodes.values() if node.pos == "名詞"]
        
        for root in root_nodes:
            if root not in syntax_tree:
                syntax_tree.append(root)

        # 依存関係の出力
        print("依存関係:")
        for word, dependents in dependencies.items():
            print(f"{word} -> {', '.join(dependents)}")
    
    # 構文木の出力
    print("\n構文木:")
    for root in syntax_tree:
        print_tree(root)

#構文木を階層的に出力する
def print_tree(node, depth=0):
    print("  " * depth + f"{node.word} ({node.pos})")
    for child in node.children:
        print_tree(child, depth + 1)


# メイン実行部分
if __name__ == "__main__":
    ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"
    
    # load_ipadic_dict：辞書を読み込む
    dictionary = load_ipadic_dict(ipadic_dir_path)
    
    text = "右に回転して、早く前に進む"
    
    dependency_analysis_with_syntax_tree(text, dictionary)
