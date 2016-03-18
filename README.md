# udbcmp
Compares two SciTools Understand UDBs and extracts metrics that changed for certain files

## How to run

Here is an example of how to get 2 separate versions of a codebase and run the
comparison and export the results.

```
export PATH=$PATH:/Applications/scitools/bin/macosx/
rm -rf tmp
mkdir tmp
cd tmp
git clone https://github.com/junit-team/junit.git
cd junit
git checkout tags/r4.9
und create -languages java ../before.udb
und add ./src/main/java/junit ../before.udb
und analyze ../before.udb
git checkout tags/r4.12
und create -languages java ../after.udb
und add ./src/main/java/junit ../after.udb
und analyze ../after.udb
# activate python 3
# . ~/venvs/und2s101/bin/activate
cd ../..
python udbcmp.py --before=./tmp/before.udb --after=./tmp/after.udb --dllDir=/Applications/scitools/bin/macosx/python > result.json
```

