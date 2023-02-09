# cd code2nl

# Fine-Tune

# lang=python #programming language
# lr=5e-5
# batch_size=4
# beam_size=10
# source_length=256
# target_length=128
# data_dir=../data/code2nl/CodeSearchNet
# output_dir=model/$lang
# train_file=$data_dir/$lang/train.jsonl
# dev_file=$data_dir/$lang/valid.jsonl
# eval_steps=1000 #400 for ruby, 600 for javascript, 1000 for others
# train_steps=50000 #20000 for ruby, 30000 for javascript, 50000 for others
# pretrained_model=microsoft/codebert-base #Roberta: roberta-base

python run.py --do_train --do_eval --model_type roberta --model_name_or_path microsoft/codebert-base-mlm --train_filename D:\Saves\Pycharm\GitHub\CodeBERT\data\code2nl\CodeSearchNet\python\train.jsonl --dev_filename D:\Saves\Pycharm\GitHub\CodeBERT\data\code2nl\CodeSearchNet\python\valid.jsonl --output_dir model/python --max_source_length 256 --max_target_length 128 --beam_size 10 --train_batch_size 4 --eval_batch_size 4 --learning_rate 5e-5 --train_steps 50000 --eval_steps 1000


# Inference and Evaluation


# lang=python #programming language
# beam_size=10
# batch_size=4
# source_length=256
# target_length=128
# output_dir=model/python
# data_dir=../data/code2nl/CodeSearchNet
# dev_file=$data_dir/$lang/valid.jsonl  D:/Saves/Pycharm/GitHub/CodeBERT/data/code2nl/CodeSearchNet/python/student_valid.jsonl
# test_file=$data_dir/$lang/test.jsonl  D:/Saves/Pycharm/GitHub/CodeBERT/data/code2nl/CodeSearchNet/python/student_test.jsonl
# test_model=$output_dir/checkpoint-best-bleu/pytorch_model.bin #checkpoint for test
#
# python run.py --do_test --model_type roberta --model_name_or_path microsoft/codebert-base --load_model_path model/python/semicon_checkpoint-best-ppl/pytorch_model.bin --dev_filename D:/Saves/Pycharm/GitHub/CodeBERT/data/code2nl/CodeSearchNet/python/student_test.jsonl --test_filename D:/Saves/Pycharm/GitHub/CodeBERT/data/code2nl/CodeSearchNet/python/mutant_train_5.jsonl --output_dir model/python --max_source_length 256 --max_target_length 128 --beam_size 10 --eval_batch_size 4 --is_mutant True