
## Convert BBMB to JSON

This is used internally to transform the BBMB model repository to a single JSON file.

Skips a few large models that make the file too large.

```bash
python booleannet/bbm2json.py \
       --summary ~/src/biodivine-boolean-models/models/summary.csv 
       --models ~/src/biodivine-boolean-models/models 
       --skip 253,248,79,261,256
       --output models.json.gz
```
