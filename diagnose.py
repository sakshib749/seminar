import pickle
import joblib
import os
import sys
from URLFeatureExtraction import featureExtraction

url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.google.com'
print('URL:', url)
features = featureExtraction(url)
feature_names = [
    'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth',
    'Redirection', 'https_Domain', 'TinyURL', 'Prefix/Suffix',
    'DNS_Record', 'Web_Traffic', 'Domain_Age', 'Domain_End',
    'iFrame', 'Mouse_Over', 'Right_Click', 'Web_Forwards'
]
print('\nExtracted features:')
for n,v in zip(feature_names, features):
    print(f'  {n}: {v}')

# load model
p = 'XGBoostClassifier.pickle.dat'
if not os.path.exists(p):
    print('\nModel file not found:', p)
    sys.exit(1)

model = None
try:
    model = pickle.load(open(p, 'rb'))
    print('\nLoaded model with pickle')
except Exception as e:
    try:
        model = joblib.load(p)
        print('\nLoaded model with joblib')
    except Exception as e2:
        print('\nFailed to load model:', e, e2)
        sys.exit(1)

print('\nModel type:', type(model))
# print classes if available
classes = getattr(model, 'classes_', None)
print('classes_:', classes)

# prediction
import pandas as pd
df = pd.DataFrame([features], columns=feature_names)
try:
    pred = model.predict(df)[0]
    print('\npredict ->', pred)
except Exception as e:
    print('predict error:', e)

try:
    probs = model.predict_proba(df)[0]
    print('predict_proba ->', probs)
except Exception as e:
    print('predict_proba error:', e)

# print feature importance (if any)
try:
    fi = getattr(model, 'feature_importances_', None)
    print('\nfeature_importances_ ->', fi)
except Exception as e:
    print('feature importance error:', e)
