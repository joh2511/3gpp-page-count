import pandas as pd
import numpy as np

print("Release | Pages ")
print("----------------")
for release in range(12, 16):
    filename = "pages_release%d.csv" % release
    data = pd.read_csv(filename, sep=";", names=["filename", "pages"])
    pages = data.pages.sum()
    print("%7d | %6d" % (release, pages))
