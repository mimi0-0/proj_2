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

    hypothesis = CTC(unit,token_list_path,mean_std_file,model_file,config_file,path)
    print(hypothesis)