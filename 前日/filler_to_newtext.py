#形態素解析
import os
import re
from collections import defaultdict, deque

number_dit = {
    "0" : "０",
    "1" : "１",
    "2" : "２",
    "3" : "３",
    "4" : "４",
    "5" : "５",
    "6" : "６",
    "7" : "７",
    "8" : "８",
    "9" : "９"
}

# 例外的に動詞として扱う単語リスト
EXCEPTION_VERBS = {"離陸", "着陸", "離陸して", "着陸して", "離陸する", "着陸する"}

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
    number_pattern = re.compile(r'\d+')  # 数字の正規表現パターン

    for start in range(len(text)):
        for end in range(start + 1, len(text) + 1):
            word = text[start:end]

            # 数字の場合
            if number_pattern.fullmatch(word):
                full_width_word = ''.join(chr(ord(c) + 0xFEE0) if '0' <= c <= '9' else c for c in word)
                node = Node(word, "数詞", full_width_word, start, 1000)
                lattice[start].append(node)
            # 英字の場合
            elif all('A' <= c <= 'Z' or 'a' <= c <= 'z' for c in word):
                full_width_word = ''.join(chr(ord(c) + 0xFEE0) if 'A' <= c <= 'Z' or 'a' <= c <= 'z' else c for c in word)
                node = Node(word, "英字", full_width_word, start, 1000)
                lattice[start].append(node)
            # 記号の場合
            elif all(33 <= ord(c) <= 47 or 58 <= ord(c) <= 64 or 91 <= ord(c) <= 96 or 123 <= ord(c) <= 126 for c in word):
                full_width_word = ''.join(chr(ord(c) + 0xFEE0) for c in word)
                node = Node(word, "記号", full_width_word, start, 1000)
                lattice[start].append(node)
            # 例外的な動詞として扱う単語
            elif word in EXCEPTION_VERBS:
                node = Node(word, "動詞", word, start, 500)  # 動詞として追加（低いコストを設定）
                lattice[start].append(node)
            # 辞書に存在する場合
            elif word in dictionary:
                print(f"Adding to lattice: {word}")  # デバッグ用
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
            #print(f"Considering node: {node.word}, cost: {node.cost}, position: {current_position}")
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


# 名詞 + 「する」+ 「前に」の組み合わせを結合する処理を強化
def combine_noun_and_suru(result):
    combined_result = []
    skip_next = False

    # 'する'の変化形をリスト化
    suru_forms = {
        "する", "した", "して", "したら", "している", "される", "させる",
        "させて", "させられる", "していた", "しても", "してくれ", "してみる",
    }
    
    te_forms = {"て", "で", "た"}  # 助詞「て」「で」の形

    for i, (word, pos, read) in enumerate(result):
        if skip_next:
            skip_next = False
            continue
           
        if pos == "名詞" and i + 1 < len(result):
            next_word, next_pos, next_read = result[i + 1]
            # 名詞 + 「する」の組み合わせを検出して結合
            if next_word in suru_forms:
                if i + 2 < len(result):
                    next_next_word, next_next_pos, next_next_read = result[i + 2]
                    # 「前」と「に」の場合、動詞として結合
                    if next_next_word == "前" and next_next_pos == "名詞" and i + 3 < len(result):
                        next_next_next_word, next_next_next_pos, next_next_next_read = result[i + 3]
                        if next_next_next_word == "に" and next_next_next_pos == "助詞":
                            combined_result.append(
                                (word + next_word + next_next_word + next_next_next_word, "動詞", read + next_read + next_next_read + next_next_next_read)
                            )
                            skip_next = True  # 3つスキップ
                            continue
                combined_result.append((word + next_word, "動詞", read + next_read))
                skip_next = True
            # 名詞 + 「し」 + 「て」の組み合わせを検出して結合
            elif next_word == "し" and next_pos == "助動詞":
                if i + 2 < len(result):
                    next_next_word, next_next_pos, next_next_read = result[i + 2]
                    if next_next_word in te_forms and next_next_pos == "助詞":
                        combined_result.append(
                            (word + next_word + next_next_word, "動詞", read + next_read + next_next_read)
                        )
                        skip_next = True  # 2つスキップ
                        continue
            elif next_word in te_forms and (next_pos == "助詞" or next_pos == "助動詞"):
                combined_result.append(
                            (word + next_word, "動詞", read + next_read)
                )
                skip_next = True  # 2つスキップ
                continue
            
            else:
                combined_result.append((word, pos, read))
            
        
        elif pos == "動詞" and i + 1 < len(result):
            next_word, next_pos, next_read = result[i + 1]
            # 動詞 + て/での組み合わせを検出して結合
            if next_word in te_forms:
                combined_result.append((word + next_word, "動詞", read + next_read))
                skip_next = True
            # 動詞 + 「前」 + 「に」の組み合わせを検出して結合
            elif next_word == "前" and next_pos == "名詞":
                if i + 2 < len(result):
                    next_next_word, next_next_pos, next_next_read = result[i + 2]
                    if next_next_word == "に" and next_next_pos == "助詞":
                        # 修正: 動詞が「～して」の場合は結合しない
                        if word.endswith("て") or word.endswith("で"):
                            combined_result.append((word, pos, read))  # そのまま動詞として追加
                            combined_result.append((next_word, next_pos, next_read))  # 「前」として追加
                            combined_result.append((next_next_word, next_next_pos, next_next_read))  # 「に」として追加
                            skip_next = True  # 次の「前」と「に」をスキップ
                            continue
                        # 「上昇する前に」を一つの動詞として結合
                        combined_result.append(
                            (word + next_word + next_next_word, "動詞", read + next_read + next_next_read)
                        )
                        skip_next = True  # 2つスキップ
                        continue
            else:
                combined_result.append((word, pos, read))
        # 連体詞 + 名詞の組み合わせを結合
        elif pos == "連体詞" and i + 1 < len(result):
            next_word, next_pos, next_read = result[i + 1]
            if next_pos == "名詞":
                combined_result.append((word + next_word, "名詞", read + next_read))
                skip_next = True  # 次の名詞をスキップ
            else:
                combined_result.append((word, pos, read))
                
        else:
            combined_result.append((word, pos, read))
    
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

# 追加: 動詞 + 助詞や名詞 + 「後」のようなパターンを分ける処理を強化
def split_combined_words(result):
    new_result = []
    skip_next = False
    
    for i, (word, pos, read) in enumerate(result):
        if skip_next:
            skip_next = False
            continue
        
        # 動詞 + 名詞「後」を分ける
        if pos == "動詞" and i + 1 < len(result):
            next_word, next_pos, next_read = result[i + 1]
            # 「後」が名詞の場合
            if next_word == "後" and next_pos in {"名詞"}:
                # 動詞と名詞「後」を分ける
                new_result.append((word, pos, read))  # 動詞部分
                new_result.append((next_word, next_pos, next_read))  # 名詞「後」
                skip_next = True  # 次の「後」をスキップ
            else:
                new_result.append((word, pos, read))  # 通常の動詞
        elif pos == "名詞" and i + 1 < len(result):
            next_word, next_pos, next_read = result[i + 1]
            # 名詞 + 助詞「後」を分ける
            if next_word == "後" and next_pos in {"助詞", "名詞"}:
                new_result.append((word, pos, read))  # 名詞部分
                new_result.append((next_word, next_pos, next_read))  # 助詞「後」
                skip_next = True  # 次の「後」をスキップ
            else:
                new_result.append((word, pos, read))  # 通常の名詞
        else:
            new_result.append((word, pos, read))  # 他のケース
    
    return new_result


# 形態素解析の実行
def morphological_analysis(text, dictionary):
    lattice = build_lattice(text, dictionary)
    previous_nodes, distances = dijkstra_lattice(lattice, len(text))
    result = get_shortest_path(previous_nodes, len(text))

    # 名詞 + する の結合処理を追加
    combined_result = combine_noun_and_suru(result)

    # 名詞、フィラーの結合
    cmbd_noun = combine_words(combined_result, '名詞')
    combined_result = combine_words(cmbd_noun, 'フィラー')

    # 動詞 + 助詞や名詞 + 「後」を分ける処理を追加
    #final_result = split_combined_words(combined_result)

    # フィラーについてのチェック
    final_results = check_filler_reading(combined_result, dictionary)

    del lattice
    del previous_nodes
    del distances
    del result
    del cmbd_noun
    del combined_result
    dictionary.clear()  # ただし、これを呼び出すと後続で dictionary にアクセスできなくなります
    del dictionary

    return final_results

"""
if __name__ == "__main__":
    ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"

    # IPAdic辞書をロード
    dictionary = load_ipadic_dict(ipadic_dir_path)

    text = "離陸"

    # 形態素解析を実行
    final_results = morphological_analysis(text, dictionary)

    # 結果を表示
    for result in final_results:
        print("Morphological analysis result:")
        for word, pos, read in result:
            print(f"{word} ({pos}) [{read}]")
"""
