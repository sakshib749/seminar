import sys
import pickle
import os
import glob
import argparse
import pandas as pd
from URLFeatureExtraction import featureExtraction
try:
    from joblib import load as joblib_load
except Exception:
    joblib_load = None

# -------------------------------
# 1. Take input URL from command line
# -------------------------------
parser = argparse.ArgumentParser(description='Predict phishing or legitimate for a URL')
parser.add_argument('url', help='URL to classify')
parser.add_argument('--model', '-m', help='Path to trained model file (optional)')
parser.add_argument('--no-calibrate', action='store_true', help='Skip automatic label calibration')
parser.add_argument('--verbose', action='store_true', help='Print raw model prediction and probabilities')
parser.add_argument('--no-rule', action='store_true', help='Skip rule-based override for obvious phishing patterns')
args = parser.parse_args()
url = args.url

# -------------------------------
# 2. Extract features from the URL
# -------------------------------
features = featureExtraction(url)

# These must match the training order (without Label column)
feature_names = [
    'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth',
    'Redirection', 'https_Domain', 'TinyURL', 'Prefix/Suffix',
    'DNS_Record', 'Web_Traffic', 'Domain_Age', 'Domain_End',
    'iFrame', 'Mouse_Over', 'Right_Click', 'Web_Forwards'
]

df = pd.DataFrame([features], columns=feature_names)

# --- simple rule-based override --------------------------------------------------
# If any of these high-risk binary features are present, treat as phishing unless
# the user opts out with --no-rule. This is conservative and meant to catch
# obvious patterns when the ML model misclassifies.
rule_features = ['Have_IP','Have_At','TinyURL','Prefix/Suffix','Redirection','DNS_Record','Web_Forwards','URL_Length']
rule_flag = any(int(df[f].iloc[0]) == 1 for f in rule_features if f in df.columns)

# -------------------------------
# 3. Load trained model
# -------------------------------
# Try common model filenames (the repo includes XGBoostClassifier.pickle.dat)
def try_load_model(path):
    # try pickle
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        pass
    # try joblib if available
    if joblib_load is not None:
        try:
            return joblib_load(path)
        except Exception:
            pass
    return None

model = None
if args.model:
    if os.path.exists(args.model):
        model = try_load_model(args.model)
        if model is None:
            print(f"Failed to load model from {args.model}. Tried pickle and joblib.")
            sys.exit(1)
    else:
        print(f"Specified model file does not exist: {args.model}")
        sys.exit(1)
else:
    possible_names = ["model.pkl", "model.pickle", "model.joblib", "XGBoostClassifier.pickle.dat", "XGBoostClassifier.pkl", "XGBoostClassifier.pickle"]
    for name in possible_names:
        if os.path.exists(name):
            model = try_load_model(name)
            if model is not None:
                break
    if model is None:
        # try to find any pickle/dat/joblib file in the repo root
        candidates = glob.glob("*.pkl") + glob.glob("*.pickle.*") + glob.glob("*.dat") + glob.glob("*.joblib")
        msg = "No trained model found. Looked for: {}.\n".format(possible_names)
        if candidates:
            msg += f"Found candidate files in current folder: {candidates}\nYou can pass the desired model filename with --model <path>."
        else:
            msg += "No candidate model files (.pkl/.pickle/.dat/.joblib) found in the current directory. Ensure the trained model file (e.g. XGBoostClassifier.pickle.dat) is present."
        print(msg)
        sys.exit(1)

# --- Automatic label calibration -------------------------------------------------
# Some older models may have inverted label mapping. Do a quick sanity-check on a
# small list of known-safe sites; if the model marks most of them as phishing (1),
# flip the label interpretation for user-facing output.
def _calibrate_label_mapping(model):
    try:
        import pandas as _pd
        from URLFeatureExtraction import featureExtraction as _fe
        safe_urls = [
            'https://www.google.com',
            'https://www.github.com',
            'https://www.wikipedia.org'
        ]
        feature_names = [
            'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth',
            'Redirection', 'https_Domain', 'TinyURL', 'Prefix/Suffix',
            'DNS_Record', 'Web_Traffic', 'Domain_Age', 'Domain_End',
            'iFrame', 'Mouse_Over', 'Right_Click', 'Web_Forwards'
        ]
        rows = []
        for u in safe_urls:
            rows.append(_fe(u))
        df = _pd.DataFrame(rows, columns=feature_names)
        preds = model.predict(df)
        # fraction predicted as '1' (phishing in original labeling)
        frac = sum(1 for p in preds if int(p) == 1) / len(preds)
        # if model marks majority of safe urls as phishing, invert mapping
        return frac > 0.5
    except Exception:
        return False

if args.no_calibrate:
    _invert_label_output = False
else:
    _invert_label_output = _calibrate_label_mapping(model)
    if _invert_label_output:
        print('Warning: automatic label calibration applied — flipping predicted labels for display')

# -------------------------------
# 4. Make prediction
# -------------------------------
prediction = model.predict(df)[0]

# if verbose, print raw model outputs (before any display flip)
if args.verbose:
    try:
        probs = model.predict_proba(df)[0]
    except Exception:
        probs = None
    print(f'Raw model prediction: {int(prediction)}, probabilities: {probs}, classes_: {getattr(model, "classes_", None)}')

# Apply rule-based override (highest priority)
if not args.no_rule and rule_flag:
    if args.verbose:
        print('Rule-based override triggered: one or more high-risk features detected -> marking as phishing')
    display_pred = 1
else:
    # Apply calibration flip if needed
    if _invert_label_output:
        display_pred = 0 if int(prediction) == 1 else 1
    else:
        display_pred = int(prediction)

# -------------------------------
# 5. Display user-friendly output (display_pred already computed above)
if display_pred == 1:
    print("❌ Phishing Website Detected!")
else:
    print("✅ Legitimate Website")
