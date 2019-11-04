# Page Count of 3GPP Standards


### Mirror 3GPP Standards:

[Harald Welte](https://laforge.gnumonks.org)'s [`mirror.sh`](http://git.osmocom.org/3gpp-etsi-pdf-links/plain/mirror.sh)
```
wget -c -r -np http://www.etsi.org/deliver/etsi_ts/
```


### Create Symlinks:

Use (`create_links.py`)[create_links.py]

```
python3 create_links.py
```


### Count pages in linux:
```
sudo apt-get install poppler-utils # installs pdfinfo
cd target_dir

echo "" > pages.csv
for f in *.pdf; do 
 (echo -n "$f;" ; pdfinfo "$f"|grep Pages| awk '{print $2}') |tee -a pages.csv
done
```

### Eval Page Counts


```
import pandas as pd
import numpy as np

print("Release | Pages ")
print("----------------")
for release in range(12, 16):
    filename = "pages_release%d.csv" % release
    data = pd.read_csv(filename, sep=";", names=["filename", "pages"])
    pages = data.pages.sum()
    print("%7d | %6d" % (release, pages))

```

Result:
```
Release | Pages 
----------------
     12 |  84335
     13 |  63091
     14 |  81216
     15 | 130328
 ```