# Running

Quick steps to run the prediction script locally (Windows / PowerShell):

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run a single URL prediction:

```powershell
python predict.py "https://www.example.com" --verbose
```

4. Optional helper (PowerShell):

```powershell
# run_predict.ps1 wraps predict.py and accepts -url parameter
.\run_predict.ps1 -url "https://www.example.com" -Verbose
```

Notes
- The repo includes a trained model file `XGBoostClassifier.pickle.dat`. If you want to replace it, train and save a new model with the same name or pass `--model <path>` to `predict.py`.
- If you see scikit-learn unpickle warnings, retrain/resave the model with the scikit-learn version in your environment.
