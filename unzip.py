import zipfile

with zipfile.ZipFile("./data.zip", "r") as zip_ref:
    zip_ref.extractall()
