from filler_to_newtext import load_ipadic_dict
from do_parsing import dependency_analysis_with_syntax_tree


# CommandProcessor クラスはデータ保持用
class CommandProcessor:
    def __init__(self):
        self.verbs = []  # 動詞のみを格納するリスト
        self.verb_dependents = []  # 動詞に対応する依存語とその品詞を格納するリスト
        

# 「前に」を含む動詞を検出し、その動詞以前の要素を最後に移動
def reorder_verbs(verbs, verb_dependents):
    pre_verb_index = None

    # 「前に」を含む動詞を探す
    for i, (verb, _) in enumerate(verbs):
        if "前に" in verb:
            pre_verb_index = i
            break

    if pre_verb_index is not None:
        verbs = verbs[pre_verb_index + 1:] + verbs[:pre_verb_index + 1]
        verb_dependents = verb_dependents[pre_verb_index + 1:] + verb_dependents[:pre_verb_index + 1]

    return verbs, verb_dependents

# リストから数詞を抜き取る
def extract_numbers(sentences):
    num = ''
    for sentence in sentences:
        if isinstance(sentence, tuple) and len(sentence) >= 2:
            sentence_word, sentence_pos = sentence  # 2つにアンパック
            if sentence_pos == "数詞":  # POSが数詞の場合
                num = sentence_word
        else:
            # Debug用に予期しないデータを確認
            print(f"Unexpected sentence format: {sentence}")
    return num


# 構文木を処理して動詞と依存語をリストに追加する
def process_root_and_generate_commands(root, processor):
    for phrase in root:
        verb = phrase[0].word  # 動詞
        verb_pos = phrase[0].pos  # 動詞の品詞
        dependents = []  # その動詞に依存する語を格納するリスト
        dependents_pos = []  # 依存語の品詞を格納するリスト

        for child in phrase[0].children:
            dependents.append(child.word)  # 依存語（名詞や形容詞など）を追加
            dependents_pos.append(child.pos)  # 依存語の品詞を追加
            print(f"dependents: {child.word}({child.pos})")

        # 動詞とその依存語のリストを表示
        print(f"Processing verb: {verb} ({verb_pos})")

        # verbs と verb_dependents に動詞とその依存語情報を追加
        processor.verbs.append((verb, verb_pos))
        processor.verb_dependents.append(list(zip(dependents, dependents_pos)))  # 依存語と品詞をペアでリストに追加
        
 
def change_to_command(verb_list, dependents_list):
    com = ""
    i = 0
    for verb in verb_list:
        exec_com = ""
        speed_num = 40
        height_num = 10
        far_num = 100
        ran_num = 90
        plus_com = ""

        if "ゆっくり" in [dep[0] for dep in dependents_list[i]]:
            plus_com = f"speed {speed_num - 20} /"
        elif "はやく" in [dep[0] for dep in dependents_list[i]] or "早" in [dep[0] for dep in dependents_list[i]]:
            plus_com = f"speed {speed_num + 20} /"

        # 動詞部分（verb[0]）を分割してチェックするように修正
        if any("進" in word for word in verb[i].split()): 
            if any("前" in word for word in verb[i].split()):
                exec_com = 'forward'
            elif any("後" in word for word in verb[i].split()):
                exec_com = 'back'
            else:
                if any("後" in word for word in dependents_list[i]):
                    exec_com = 'back' 
                elif any("右" in word for word in dependents_list[i]):
                    exec_com = 'right' 
                elif any("左" in word for word in dependents_list[i]):
                    exec_com = 'left'        
                else:
                    exec_com = 'forward'

            # 数詞とその単位を処理
            exta_num = extract_numbers(dependents_list[i])
            if exta_num != '':
                
                far_num = int(exta_num)
            exec_com = exec_com + " " + str(far_num)
        
        
        elif "落" in verb[0]:
            if any("速" in dep[0] for dep in dependents_list[i]) or any("スピード" in dep[0] for dep in dependents_list[i]):
                exec_com = 'speed ' + str(speed_num - 20)
            else:
                exec_com = 'down '
                exta_num = extract_numbers(dependents_list[i])
                if exta_num != '':
                    height_num = int(exta_num)
                exec_com = exec_com + str(height_num)
        
        elif "上" in verb[0]:
            if any("速" in dep[0] for dep in dependents_list[i]) or any("スピード" in dep[0] for dep in dependents_list[i]):
                exec_com = 'speed ' + str(speed_num + 20)
            else:
                exec_com = 'up '
                exta_num = extract_numbers(dependents_list[i])
                if exta_num != '':
                    height_num = int(exta_num)
                exec_com = exec_com + str(height_num)

        elif "反転" in verb[0] or "宙返り" in verb[0]:
            if any("後ろ" in dep[0] for dep in dependents_list[i]):
                exec_com = 'flip b'
            elif any("右" in dep[0] for dep in dependents_list[i]):
                exec_com = 'flip r'
            elif any("左" in dep[0] for dep in dependents_list[i]):
                exec_com = 'flip l'
            else:
                exec_com = 'flip f'

        elif "旋回" in verb[0] or "描" in verb[0]:
            exta_num = extract_numbers(dependents_list[i])
            if exta_num != '':
                far_num = int(exta_num)
            if any("右" in dep[0] for dep in dependents_list[i]):
                exec_com = 'curve ' + str(far_num) + " 0 0"
            else:
                exec_com = 'curve ' + str(-far_num) + " 0 0"

        elif "回" in verb[0] or "曲" in verb[0]:
            if any("右" in dep[0] for dep in dependents_list[i]):
                exec_com = 'cw'
            else:
                exec_com = 'ccw'
            exta_num = extract_numbers(dependents_list[i])
            if exta_num != '':
                ran_num = int(exta_num)
            exec_com = exec_com + " " + str(ran_num)
        elif "見" in verb[0] or "写" in verb[0] or "と" in verb[0] or "撮" in verb[0] or "オン" in verb[0] :
            if any("映像" in dep[0] for dep in dependents_list[i]) or any("写真" in dep[0] for dep in dependents_list[i]) or any("ストリーム" in dep[0] for dep in dependents_list[i]):
                exec_com = 'streamon'
                
        elif "消" in verb[0] or "オフ" in verb[0]:
            if any("映像" in dep[0] for dep in dependents_list[i]) or any("写真" in dep[0] for dep in dependents_list[i]) or any("ストリーム" in dep[0] for dep in dependents_list[i]):
                exec_com = 'streamoff'
        com = com + plus_com + exec_com + " /"
        i += 1

    return com

def process_text(text, dictionary):
    # CommandProcessor インスタンスの生成
    processor = CommandProcessor()

    # 構文解析
    root = dependency_analysis_with_syntax_tree(text, dictionary)

    # 構文木の処理
    process_root_and_generate_commands(root, processor)

    # 動詞順序の再整理
    processor.verbs, processor.verb_dependents = reorder_verbs(processor.verbs, processor.verb_dependents)

    # コマンド作成
    command = change_to_command(processor.verbs, processor.verb_dependents)

    return command, processor.verbs, processor.verb_dependents



if __name__ == "__main__":
    ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"

    # load_ipadic_dict：辞書を読み込む
    dictionary = load_ipadic_dict(ipadic_dir_path)

    text = "右に曲がる前に右に100cm進む"
    root = dependency_analysis_with_syntax_tree(text, dictionary)
    
    # 構文木の出力
    print("\n返ってくる構文:")
    print(root)

    # CommandProcessor クラスのインスタンスを作成
    processor = CommandProcessor()

    # 構文解析結果を処理
    process_root_and_generate_commands(root, processor)
    
    # 動詞の順序を再整理
    processor.verbs, processor.verb_dependents = reorder_verbs(processor.verbs, processor.verb_dependents)

    # コマンドを作成
    command = change_to_command(processor.verbs, processor.verb_dependents)

    print("\n生成されたコマンド:")
    print(command)

    # 結果を直接アクセス（パブリック変数にアクセス）
    print("\nパブリック変数としての動詞と依存語のリスト:")
    print("Verbs:", processor.verbs)
    print("Verb Dependents:", processor.verb_dependents)

