import joblib
import numpy as np

path = 'rf_pipeline.pkl'
model = joblib.load(path)
changed = False
try:
    pre = model.named_steps.get('preprocessor', None)
    if pre is not None:
        cat = pre.named_transformers_.get('cat', None)
        if cat is not None and hasattr(cat, 'categories_'):
            new_cats = []
            for arr in cat.categories_:
                if np.issubdtype(getattr(arr, 'dtype', None), np.integer):
                    new_cats.append(arr.astype(float))
                    changed = True
                else:
                    new_cats.append(arr)
            if changed:
                cat.categories_ = new_cats
except Exception as e:
    print('Patch failed:', e)

if changed:
    joblib.dump(model, 'rf_pipeline_fixed.pkl')
    print('Wrote rf_pipeline_fixed.pkl')
else:
    print('No changes needed')
