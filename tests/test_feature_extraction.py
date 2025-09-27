import os
from URLFeatureExtraction import featureExtraction


def test_feature_count():
    # basic smoke test: returns 16 features for a well-formed URL
    features = featureExtraction('https://www.example.com')
    assert isinstance(features, list)
    assert len(features) == 16
