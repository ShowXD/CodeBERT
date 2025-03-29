from transformers import RobertaTokenizer, RobertaForMaskedLM
from transformers import LineByLineTextDataset
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import torch
from sklearn.metrics import accuracy_score, f1_score


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# load model and tokenize
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = RobertaForMaskedLM.from_pretrained('roberta-base').to(device)


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
    learning_rate=2e-3,
    per_device_train_batch_size=8,
    disable_tqdm=False,
    save_steps=10000,
    save_total_limit=2,
    seed=1
)


def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    f1 = f1_score(labels, preds, average="weighted")
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "f1": f1}


trainer = Trainer(
    model=model,
    args=training_args,
    compute_metrics=compute_metrics,
    data_collator=data_collator,
    train_dataset=dataset,
    tokenizer=tokenizer
)


trainer.train()
trainer.save_model("./model/roberta-retrained")
