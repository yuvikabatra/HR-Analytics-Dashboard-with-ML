import joblib
import json

path = 'rf_pipeline.pkl'
model = joblib.load(path)
out = {}
out['model_type'] = str(type(model))
try:
    steps = list(model.named_steps.keys())
    out['pipeline_steps'] = steps
except Exception:
    out['pipeline_steps'] = None

pre = None
try:
    pre = model.named_steps.get('preprocessor', None)
    out['preprocessor_type'] = str(type(pre))
except Exception:
    out['preprocessor_type'] = None

if pre is not None:
    try:
        transformers = []
        for name, trans, cols in pre.transformers:
            transformers.append({'name': name, 'cols': cols, 'transformer_type': str(type(trans))})
        out['transformers'] = transformers
    except Exception as e:
        out['transformers_error'] = str(e)
    # If there's a OneHotEncoder under the 'cat' transformer, print its categories
    try:
        cat = pre.named_transformers_.get('cat', None)
        if cat is not None:
            cats = []
            for i, c in enumerate(cat.categories_):
                cats.append({'index': i, 'len': len(c), 'dtype': str(c.dtype), 'sample': list(c[:10])})
            out['onehot_categories'] = cats
    except Exception as e:
        out['onehot_error'] = str(e)

print('Model type:', out.get('model_type'))
print('Pipeline steps:', out.get('pipeline_steps'))
print('Preprocessor type:', out.get('preprocessor_type'))
if 'transformers' in out:
    for t in out['transformers']:
        print('Transformer:', t['name'], 'cols len=', len(t['cols']))

if 'onehot_categories' in out:
    print('\nOneHotEncoder categories summary:')
    for cat in out['onehot_categories']:
        print('Index', cat['index'], 'len', cat['len'], 'dtype', cat['dtype'], 'sample', cat['sample'])

