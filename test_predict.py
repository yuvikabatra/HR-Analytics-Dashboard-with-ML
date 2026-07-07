import joblib
import pandas as pd
import traceback

model = joblib.load('rf_pipeline.pkl')
import numpy as np
# Patch categories in OneHotEncoder if integer dtypes cause isnan issues
try:
    pre = model.named_steps.get('preprocessor', None)
    if pre is not None:
        cat = pre.named_transformers_.get('cat', None)
        if cat is not None and hasattr(cat, 'categories_'):
            new_cats = []
            changed = False
            for arr in cat.categories_:
                if np.issubdtype(getattr(arr, 'dtype', None), np.integer):
                    new_cats.append(arr.astype(float))
                    changed = True
                else:
                    new_cats.append(arr)
            if changed:
                cat.categories_ = new_cats
except Exception:
    pass
# Rebuild a safe preprocessor using the original training data and attach classifier
try:
    from sklearn.pipeline import Pipeline as SKPipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    train_df = pd.read_excel('HR Data.xlsx', engine='openpyxl')
    all_cols = [c for c in df.columns if c in train_df.columns]
    num_cols_train = [c for c in all_cols if c in train_df.select_dtypes(include=['number', 'int64', 'float']).columns]
    cat_cols_train = [c for c in all_cols if c not in num_cols_train]
    new_pre = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols_train),
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), cat_cols_train)
        ], remainder='drop'
    )
    new_pre.fit(train_df[all_cols])
    # convert integer categories to float
    try:
        cat_enc = new_pre.named_transformers_.get('cat', None)
        if cat_enc is not None and hasattr(cat_enc, 'categories_'):
            new_cats = []
            for arr in cat_enc.categories_:
                if np.issubdtype(getattr(arr, 'dtype', None), np.integer):
                    new_cats.append(arr.astype(float))
                else:
                    new_cats.append(arr)
            cat_enc.categories_ = new_cats
    except Exception:
        pass
    classifier = model.named_steps.get('classifier', None)
    if classifier is not None:
        # Build SafeModel using get_dummies + StandardScaler to avoid OneHotEncoder issues
        try:
            scaler = new_pre.named_transformers_['num']
            dummy_df = pd.get_dummies(train_df[all_cols].astype(str), drop_first=True)
            dummy_columns = list(dummy_df.columns)

            class SafeModel:
                def __init__(self, classifier, scaler, num_cols, cat_cols, dummy_columns):
                    self.classifier = classifier
                    self.scaler = scaler
                    self.num_cols = num_cols
                    self.cat_cols = cat_cols
                    self.dummy_columns = dummy_columns

                def _transform(self, X):
                    X_num = X[self.num_cols].astype(float) if len(self.num_cols) else pd.DataFrame()
                    if len(self.num_cols):
                        X_num_scaled = pd.DataFrame(self.scaler.transform(X_num), columns=self.num_cols, index=X.index)
                    else:
                        X_num_scaled = pd.DataFrame(index=X.index)

                    X_cat = pd.get_dummies(X[self.cat_cols].astype(str), drop_first=True)
                    X_cat = X_cat.reindex(columns=self.dummy_columns, fill_value=0)

                    X_final = pd.concat([X_num_scaled.reset_index(drop=True), X_cat.reset_index(drop=True)], axis=1)
                    return X_final

                def predict(self, X):
                    Xf = self._transform(X)
                    return self.classifier.predict(Xf)

                def predict_proba(self, X):
                    Xf = self._transform(X)
                    return self.classifier.predict_proba(Xf)

            model = SafeModel(classifier, scaler, num_cols_train, cat_cols_train, dummy_columns)
        except Exception:
            model = SKPipeline([('preprocessor', new_pre), ('classifier', classifier)])
except Exception:
    pass
    try:
        if cat is not None and hasattr(cat, 'transform'):
            _orig_transform = cat.transform
            def _patched_transform(X, *args, **kwargs):
                new_cats2 = []
                for arr in cat.categories_:
                    if np.issubdtype(getattr(arr, 'dtype', None), np.integer):
                        new_cats2.append(arr.astype(float))
                    else:
                        new_cats2.append(arr)
                cat.categories_ = new_cats2
                return _orig_transform(X, *args, **kwargs)
            cat.transform = _patched_transform
    except Exception:
        pass

input_data = {
    "Age":[30],
    "Daily Rate":[800],
    "Distance From Home":[5],
    "Hourly Rate":[60],
    "Monthly Income":[5000],
    "Monthly Rate":[10000],
    "Num Companies Worked":[2],
    "Percent Salary Hike":[14],
    "Total Working Years":[10],
    "Training Times Last Year":[3],
    "Years At Company":[5],
    "Years In Current Role":[3],
    "Years Since Last Promotion":[1],
    "Years With Curr Manager":[3],

    "Business Travel":["Travel_Rarely"],
    "Department":["Research & Development"],
    "Education Field":["Life Sciences"],
    "Gender":["Male"],
    "Job Role":["Research Scientist"],
    "Marital Status":["Single"],
    "Over Time":["No"],
    "Education":[3],
    "Environment Satisfaction":[3],
    "Job Involvement":[3],
    "Job Level":[2],
    "Job Satisfaction":[3],
    "Performance Rating":[3],
    "Relationship Satisfaction":[3],
    "Work Life Balance":[3],
    "CF_age band":["25 - 34"],
    "CF_current Employee":["Yes"]
}

df = pd.DataFrame(input_data)
print('Dtypes:')
print(df.dtypes)

try:
    print('Attempting predict...')
    pred = model.predict(df)
    print('Pred:', pred)
except Exception as e:
    print('Predict error:', repr(e))
    traceback.print_exc()
