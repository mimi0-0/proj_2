import os
import re
from collections import defaultdict, deque

# ノードのクラスを定義
class Node:
    def __init__(self, word, pos, start, cost):
        self.word = word  # 形態素
        self.pos = pos  # 品詞
        self.start = start  # 開始位置
        self.cost = cost  # コスト
        self.next_nodes = []  # 次に接続されるノードのリスト

# IPAdic辞書を読み込む関数（ディレクトリ内のすべてのCSVファイルを読み込み）
def load_ipadic_dict(directory_path):
    dictionary = defaultdict(list)
    for filename in os.listdir(directory_path):
        # .csvファイルのみを対象とする
        if filename.endswith(".csv"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='euc-jp') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) > 8:  # フォーマットの確認
                        word = parts[0]  # 表層形（単語の形）
                        pos = parts[4]    # 品詞
                        cost = int(parts[3])  # コスト (第4列に仮定)
                        dictionary[word].append((pos, cost))
    return dictionary

# テキストからラティスを構築する関数
def build_lattice(text, dictionary):
    lattice = defaultdict(list)
    for start in range(len(text)):
        for end in range(start + 1, len(text) + 1):
            word = text[start:end]
            if word in dictionary:
                for pos, cost in dictionary[word]:
                    node = Node(word, pos, start, cost)
                    lattice[start].append(node)

    """
    print("Lattice structure:")
    for start, nodes in lattice.items():
        print(f"Start position {start}: {[node.word for node in nodes]}")
    """
    
    return lattice

# ダイクストラ法で最短経路を探索する関数
def dijkstra_lattice(lattice, text_len):
    distances = {0: 0}
    previous_nodes = {0: None}
    queue = deque([0])

    while queue:
        current_position = queue.popleft()
        
        # current_positionがテキストの長さ以上の場合は終了
        if current_position >= text_len:
            break

        # 現在の位置からのノードを処理
        for node in lattice[current_position]:
            next_position = current_position + len(node.word)
            cost = distances[current_position] + node.cost

            # next_positionがcurrent_position + node.wordの終わりに一致する場合のみ
            if next_position == current_position + len(node.word):
                if next_position not in distances or cost < distances[next_position]:
                    distances[next_position] = cost
                    previous_nodes[next_position] = node
                    queue.append(next_position)

    return previous_nodes, distances


# 最短経路から形態素を取得する関数
def get_shortest_path(previous_nodes, text_len):
    result = []
    position = text_len
    while position > 0:
        node = previous_nodes.get(position)  # 辞書から取得
        if node is None:  # ノードが存在しない場合
            break
        result.append((node.word, node.pos))
        position -= len(node.word)
    return list(reversed(result))

# 名詞が連続する場合に結合するメソッド
def combine_nouns(morphemes):
    combined_result = []
    buffer_word = ""
    buffer_pos = None

    for word, pos in morphemes:
        if pos == "名詞":
            # 名詞が連続している場合はバッファに追加
            if buffer_pos == "名詞":
                buffer_word += word
            else:
                # バッファの内容を追加して新たにバッファをセット
                if buffer_word:
                    combined_result.append((buffer_word, buffer_pos))
                buffer_word = word
                buffer_pos = pos
        else:
            # 名詞でない場合は、バッファをリセットし通常の処理を行う
            if buffer_word:
                combined_result.append((buffer_word, buffer_pos))
                buffer_word = ""
                buffer_pos = None
            combined_result.append((word, pos))

    # 最後に残ったバッファの内容を追加
    if buffer_word:
        combined_result.append((buffer_word, buffer_pos))
    
    return combined_result


# 形態素解析を行うメイン関数
def morphological_analysis(text, dictionary):
    lattice = build_lattice(text, dictionary)
    """
    print("Lattice structure:")
    for start, nodes in lattice.items():
        print(f"start: {start} -> {[node.word for node in nodes]}")  # Latticeの内容を表示
    
    previous_nodes, distances = dijkstra_lattice(lattice, len(text))
    print("Previous Nodes:", previous_nodes)  # 経路のノードを表示
    print("Distances:", distances)  # 距離を表示
    """
    
    previous_nodes, distances = dijkstra_lattice(lattice, len(text))
    result =  get_shortest_path(previous_nodes, len(text))
    
    # メモリの解放
    del lattice
    del previous_nodes
    del distances
    dictionary.clear()
    del dictionary
    
    # 名詞の結合
    combined_result = combine_nouns(result)
    
    return combined_result
"""
# IPAdic辞書の読み込み（ディレクトリパスを指定）
ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/" # 読み込む先の辞書が保存されているディレクトリのパスを指定
dictionary = load_ipadic_dict(ipadic_dir_path)

# 辞書の内容を確認
print("Loaded Dictionary:")
print(f"Dictionary size: {len(dictionary)} entries")  # 辞書のエントリ数を表示
#for word, entries in list(dictionary.items())[:10]:  # 最初の10エントリだけ表示
#    print(f"{word}: {entries}")

# テストするテキストを確認
#text = "形態素解析を行う"  # テストするテキスト

# 形態素解析の実行
result = morphological_analysis(text, dictionary)


# 結果の表示
if result:
    for word, pos in result:
        print(f'{word} ({pos})')
else:
    print("No morphological analysis result found.")
"""
