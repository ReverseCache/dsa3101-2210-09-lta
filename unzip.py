import zipfile

with zipfile.ZipFile("./datax.zip", "r") as zip_ref:
    zip_ref.extractall()
