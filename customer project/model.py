from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from utils import load_data
import pandas as pd

def train_model():
    df = load_data()

    # Create target
    threshold = df['total_spend'].quantile(0.75)
    df['high_value'] = (df['total_spend'] >= threshold).astype(int)

    X = df.drop(['high_value'], axis=1)
    y = df['high_value']

    # Convert categorical
    X = pd.get_dummies(X, drop_first=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    return model, acc