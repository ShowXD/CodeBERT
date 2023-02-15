from transformers import RobertaTokenizer, RobertaForMaskedLM
from transformers import LineByLineTextDataset
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import torch


# load model and tokenize
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = RobertaForMaskedLM.from_pretrained('roberta-base')


# load dataset
dataset = LineByLineTextDataset(
    tokenizer=tokenizer,
    file_path="../../data/code2nl/CodeSearchNet/python/txt/train.txt",
    block_size=512,
)


# prepare data_collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)


training_args = TrainingArguments(
    output_dir="./roberta-retrained",
    overwrite_output_dir=True,
    num_train_epochs=25,
    per_device_train_batch_size=48,
    save_steps=500,
    save_total_limit=2,
    seed=1
)


trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset
)


trainer.train()
trainer.save_model("./model/roberta-retrained")
