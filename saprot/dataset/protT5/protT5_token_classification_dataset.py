import json
import random
import torch

from ..data_interface import register_dataset
from transformers import T5Tokenizer
from ..lmdb_dataset import *
from data.data_transform import pad_sequences
import re


@register_dataset
class ProtT5TokenClassificationDataset(LMDBDataset):
    def __init__(self,
                 tokenizer: str,
                 max_length: int = 1024,
                 **kwargs):
        """
        Args:
            tokenizer: Path to tokenizer
            max_length: Max length of sequence
            **kwargs:
        """
        super().__init__(**kwargs)
        self.tokenizer = T5Tokenizer.from_pretrained(tokenizer)
        self.max_length = max_length

    def __getitem__(self, index):
        entry = json.loads(self._get(index))
        seq = entry['seq'][::2]
        seq = " ".join(seq)

        # Add -1 to the end of the label to ignore the cls token
        label = entry["label"][:self.max_length] + [-1]
        
        return seq, label

    def __len__(self):
        return int(self._get("length"))

    def collate_fn(self, batch):
        seqs, labels = tuple(zip(*batch))
        labels = torch.tensor(labels)
        labels = {"labels": labels}
        
        encoder_info = self.tokenizer.batch_encode_plus(seqs, return_tensors='pt', padding=True, max_length=self.max_length, truncation=True)
        inputs = {"inputs": encoder_info}
        
        return inputs, labels