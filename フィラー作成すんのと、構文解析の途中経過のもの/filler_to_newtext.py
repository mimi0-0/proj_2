#フィラーをつなげて一つの単語にするかつ、同じ音の単語を探し、その候補を全て列挙する
import os
import re
from collections import defaultdict, deque

# ノードのクラスを定義
class Node:
    def __init__(self, word, pos, read, start, cost):
        self.word = word  # 形態素
        self.pos = pos  # 品詞
        self.read = read  # 読み仮名
        self.start = start  # 開始位置
        self.cost = cost  # コスト
        self.next_nodes = []  # 次に接続されるノードのリスト

# IPAdic辞書を読み込む関数（ディレクトリ内のすべてのCSVファイルを読み込み）
def load_ipadic_dict(directory_path):
    dictionary = defaultdict(list)
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='euc-jp') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) > 8:  # フォーマットの確認
                        word = parts[0]  # 表層形（単語の形）
                        pos = parts[4]    # 品詞
                        read = parts[12]  # 読み仮名
                        cost = int(parts[3])  # コスト (第4列に仮定)
                        dictionary[word].append((pos, read, cost))  # 読み仮名も含めて保存
    return dictionary

# テキストからラティスを構築する関数
def build_lattice(text, dictionary):
    lattice = defaultdict(list)
    for start in range(len(text)):
        for end in range(start + 1, len(text) + 1):
            word = text[start:end]
            if word in dictionary:
                for pos, read, cost in dictionary[word]:
                    node = Node(word, pos, read, start, cost)
                    lattice[start].append(node)
    return lattice

# ダイクストラ法で最短経路を探索する関数
def dijkstra_lattice(lattice, text_len):
    distances = {0: 0}
    previous_nodes = {0: None}
    queue = deque([0])

    while queue:
        current_position = queue.popleft()
        if current_position >= text_len:
            break

        for node in lattice[current_position]:
            next_position = current_position + len(node.word)
            cost = distances[current_position] + node.cost

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
        result.append((node.word, node.pos, node.read))  # 読み仮名も追加
        position -= len(node.word)
    return list(reversed(result))

# 名詞が連続する場合に結合するメソッド
def combine_words(check_text, check_pos):
    combined_result = []
    buffer_word = ''
    buffer_read = ''
    buffer_pos = None

    for word, pos, read in check_text:  # 読み仮名も考慮
        if pos == check_pos:
            # check_posが連続している場合はバッファに追加
            if buffer_pos == check_pos:
                buffer_word += word
                buffer_read += read
            else:
                # バッファの内容を追加して新たにバッファをセット
                if buffer_word:
                    combined_result.append((buffer_word, buffer_pos, buffer_read))
                buffer_word = word
                buffer_read = read
                buffer_pos = pos
        else:
            # check_posでない場合は、バッファをリセットし通常の処理を行う
            if buffer_word:
                combined_result.append((buffer_word, buffer_pos, buffer_read))
                buffer_word = ''
                buffer_read = ''
                buffer_pos = None
            combined_result.append((word, pos, read))

    # 最後に残ったバッファの内容を追加
    if buffer_word:
        combined_result.append((buffer_word, buffer_pos, buffer_read))

    return combined_result

# フィラーの読み仮名をチェックして複数候補を生成する関数
def check_filler_reading(combined_result, dictionary):
    results = []  # 全ての組み合わせの結果を保持するリスト
    current_result = combined_result[:]  # オリジナルの組み合わせを保持
    unique_results = set()  # 重複を避けるためのセット

    for idx, (word, pos, read) in enumerate(combined_result):
        if pos == 'フィラー':
            matches = []
            # 辞書内に同じ読み仮名を持つ単語をすべて収集
            for dict_word, pos_data in dictionary.items():
                for pos, read_in_dict, cost in pos_data:
                    if read_in_dict == read:
                        matches.append((dict_word, pos, read_in_dict, cost))

            if matches:
                # フィラーに対応する複数の候補が見つかった場合、それぞれの解を生成
                for match in matches:
                    new_result = current_result[:]
                    new_result[idx] = (match[0], match[1], match[2])  # フィラーの部分を置き換える
                    result_tuple = tuple(new_result)
                    if result_tuple not in unique_results:
                        unique_results.add(result_tuple)
                        results.append(new_result)

    if results:
        # 複数の候補を出力
        for res in results:
            print("New morphological analysis result:")
            for word, pos, read in res:
                print(f'{word} ({pos})[{read}]')
    else:
        # 候補が見つからない場合、元の結果を出力
        print("No alternative matches found.")
        results.append(current_result)

    return results

# 形態素解析を行うメイン関数
def morphological_analysis(text, dictionary):
    lattice = build_lattice(text, dictionary)
    previous_nodes, distances = dijkstra_lattice(lattice, len(text))
    result = get_shortest_path(previous_nodes, len(text))

    # 名詞、フィラーの結合
    cmbd_noun = combine_words(result, '名詞')
    combined_result = combine_words(cmbd_noun, 'フィラー')

    # フィラーについてのチェック
    final_results = check_filler_reading(combined_result, dictionary)

    del lattice
    del previous_nodes
    del distances
    dictionary.clear()
    del dictionary

    return final_results

# IPAdic辞書の読み込み（ディレクトリパスを指定）
#ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"  
#dictionary = load_ipadic_dict(ipadic_dir_path)

# 辞書の内容を確認
#print("Loaded Dictionary:")
#print(f"Dictionary size: {len(dictionary)} entries")  # 辞書のエントリ数を表示

# テストするテキストを確認
#text = "形態素解析でまえに進む"  # テストするテキスト

# 形態素解析の実行
#result = morphological_analysis(text, dictionary)

# 結果の表示
#if not result:
#    print("No morphological analysis result found.")
