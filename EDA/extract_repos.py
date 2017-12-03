import zipfile
import pandas as pd

def repo_to_df(zip_fn):
    archive = zipfile.ZipFile(zip_fn)

    res = []
    for zfile in archive.filelist:
        if zfile.filename.endswith('/'): # is it a directory?
            continue

        text = archive.read(zfile)
        if zfile.filename.endswith('.ipynb'):
            text = ipynb_to_code(text.decode())

        file = {
            'filename': zfile.filename,
            'code': text,
            'extention': zfile.filename.split('.')[-1]
        }
        res.append(file)

    return pd.DataFrame(res)
