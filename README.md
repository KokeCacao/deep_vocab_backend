# DeepVocab Backend
To see documentation, please go to [DeepVocab Documentation Repository](https://github.com/KokeCacao/deep_vocab).

## Runtime

DeepVocab uses a uv-managed Python environment:

```bash
./install.sh
./run.sh
```

`./install.sh` creates `.venv` from the committed `uv.lock` and runs the
runtime tests. Production executes `.venv/bin/gunicorn` directly through
`deepvocab.service`; Conda activation is not required.
