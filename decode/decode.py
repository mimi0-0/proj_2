import os
from CTC import CTC

if __name__ == "__main__":
    unit = "kana"
    path = "/Users/owner/proj/decode/record"
    exp_dir =  "/Users/Owner/proj/ex" 
    token_list_path = os.path.join(exp_dir, 'data', unit,
                                   'token_list')
    
    model_dir = os.path.join(exp_dir, unit+'_model_ctc')

    mean_std_file = os.path.join(model_dir, 'mean_std.txt')

    model_file = os.path.join(model_dir, 'best_model.pt')

    config_file = os.path.join(model_dir, 'config.json')

    hypothesis = CTC(unit =unit,token_list=token_list_path,mean_std=mean_std_file,model=model_file,config=config_file,recording_path=path)
    print(hypothesis)