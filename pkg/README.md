# asx-shorts
Tiny helper that downloads ASIC's daily aggregated short position report and returns a tidy pandas DataFrame.
```python
from asx_shorts import latest
df, as_of = latest()
print(df.head())
```
Data: ASIC short position reports. Check ASIC's terms before redistributing. Not financial advice.
