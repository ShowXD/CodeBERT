import torch
import torch.nn as nn
import torch.optim as optim
from CodeBERT.code2nl.model import Seq2Seq
from transformers import (WEIGHTS_NAME, AdamW, get_linear_schedule_with_warmup,
                          RobertaConfig, RobertaModel, RobertaTokenizer)

MODEL_CLASSES = {'roberta': (RobertaConfig, RobertaModel, RobertaTokenizer)}
config_class, model_class, tokenizer_class = MODEL_CLASSES['roberta']
config = config_class.from_pretrained('microsoft/codebert-base')
tokenizer = tokenizer_class.from_pretrained('microsoft/codebert-base', do_lower_case=False)

encoder = model_class.from_pretrained('microsoft/codebert-base', config=config)
decoder_layer = nn.TransformerDecoderLayer(d_model=config.hidden_size, nhead=config.num_attention_heads)
decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)

model = Seq2Seq(encoder=encoder, decoder=decoder, config=config,
                beam_size=10, max_length=128,
                sos_id=tokenizer.cls_token_id, eos_id=tokenizer.sep_token_id)

no_decay = ['bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
     'weight_decay': 0.0},
    {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
]
optimizer = AdamW(optimizer_grouped_parameters, lr=5e-5, eps=1e-8)
checkpoint = torch.load('CodeBERT/code2nl/model/python/checkpoint-last/pytorch_model.bin')
model.load_state_dict(torch.load(checkpoint))
optimizer.load.state.dict(checkpoint['optimizer_state_dict'])
epoch = checkpoint['epoch']
loss = checkpoint['loss']
model.eval()
