from filler_to_newtext import load_ipadic_dict
from do_parsing import dependency_analysis_with_syntax_tree

class CommandProcessor:
    def __init__(self):
        self.verbs = []  # 動詞のみを格納するリスト
        self.verb_dependents = []  # 動詞に対応する依存語とその品詞を格納するリスト

    def process_root_and_generate_commands(self, root):
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
            self.verbs.append((verb, verb_pos))
            self.verb_dependents.append(list(zip(dependents, dependents_pos)))  # 依存語と品詞をペアでリストに追加

    #「前に」を含む動詞を検出し、その動詞以前の要素を最後に移動
    def reorder_verbs(self):
        pre_verb_index = None
        
        # 「前に」を含む動詞を探す
        for i, (verb, _) in enumerate(self.verbs):
            if "前に" in verb:
                pre_verb_index = i
                break

        if pre_verb_index is not None:
            self.verbs = self.verbs[pre_verb_index + 1:] + self.verbs[:pre_verb_index + 1]
            self.verb_dependents = self.verb_dependents[pre_verb_index + 1:] + self.verb_dependents[:pre_verb_index + 1]

    def change_to_command(verb_list, dependents_list):
        com = ""
        i = 0
        for verb in verb_list:
            exec_com = ""
            speed_num = "50"
            height_num = "300"
            far_num = "100"
            ran_num = "90"
            plus_num = ""
            if("ゆっくり" in dependents_list[i]):
                plus_num = f"speed {speed_num - 10} /"
            elif("はやく" in dependents_list[i]) or ("早" in dependents_list[i]):
                plus_num = f"speed {speed_num + 10} /"
            
            if "進" in verb:
                if "前" in verb:
                    exec_com = 'forward'
                elif "後" in verb: 
                    exec_com = 'back'
                else:
                    if "後" in dependents_list[i]:
                        exec_com = 'back' 
                    elif "右" in dependents_list[i]:
                        exec_com = 'right' 
                    elif "左" in dependents_list[i]:
                        exec_com = 'left'        
                    else:
                        exec_com = 'forward'
            
            elif "落" in verb_list:
                if ("速" in dependents_list[i]) or ("スピード" in dependents_list[i]):
                    exec_com = 'speed ' + (speed_num -10)
                else:
                    exec_com = 'down '
            
            elif ("反転" in verb_list) or ("宙返り" in verb_list): 
                if "後" in dependents_list[i]:
                    exec_com = 'flip b'
                if "右" in dependents_list[i]:
                    exec_com = 'flip r' 
                elif "左" in dependents_list[i]:
                    exec_com = 'flip l'
                else:
                    exec_com = 'flip f'
                  
            elif ("旋回" in verb_list) or ("描" in verb_list):
                if "右" in dependents_list[i]:
                    exec_com = 'curve 0 0 0 ' 
                elif "左" in dependents_list[i]:
                    exec_com = 'curve 0 0 0'  
      
            elif ("回" in verb_list) or ("曲" in verb_list):
                if "右" in dependents_list[i]:
                    exec_com = 'cw' 
                else:
                    exec_com = 'ccw'  
            com = com +plus_num + exec_com + " /"
        
        return com
                    
            

if __name__ == "__main__":
    ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"

    # load_ipadic_dict：辞書を読み込む
    dictionary = load_ipadic_dict(ipadic_dir_path)

    text = "旋回して前に進む前に速度を落として後ろに進んで"
    root = dependency_analysis_with_syntax_tree(text, dictionary)
    
    # 構文木の出力
    print("\n返ってくる構文:")
    print(root)

    # CommandProcessor クラスのインスタンスを作成
    processor = CommandProcessor()
    
    # 構文解析結果を処理
    processor.process_root_and_generate_commands(root)
    
    # 動詞の順序を再整理
    processor.reorder_verbs()
    
    
    # 結果を直接アクセス（パブリック変数にアクセス）
    print("\nパブリック変数としての動詞と依存語のリスト:")
    print("Verbs:", processor.verbs)
    print("Verb Dependents:", processor.verb_dependents)
