# GridSignal AI — Key Findings

## 1. Research Question

How did negative electricity prices in the German day-ahead market vary between 2024 and 2025, and how did renewable generation differ between negative-price and nonnegative-price hours?

## 2. Finding One: Negative Prices Increased in May and June 2025

Negative-price hours became substantially more frequent in May and June 2025 compared with the same months in 2024.

| Month | 2024 negative-price hours | 2024 frequency | 2025 negative-price hours | 2025 frequency |
|---|---:|---:|---:|---:|
| May | 78 | 10.48% | 129 | 17.34% |
| June | 64 | 8.89% | 141 | 19.58% |

The frequency increased by 6.86 percentage points in May and 10.69 percentage points in June.

**Interpretation:** These results identify late spring and early summer 2025 as periods worth investigating further. They do not establish the underlying causes of the increase.

**Visualization:** `negative_price_frequency_2024_2025.png`

## 3. Finding Two: Solar Generation Was Higher During Negative-Price Hours

In May 2025, average solar generation was approximately 34,775 MWh during negative-price hours, compared with 9,415 MWh during nonnegative-price hours.

In June 2025, the corresponding averages were approximately 35,296 MWh and 9,713 MWh.

These are differences in average generation per observed hourly interval, not monthly generation totals.

**Interpretation:** The observed data show an association between higher solar generation and negative prices in these months. Other factors, including electricity demand, wind generation, conventional power plant operations, cross-border flows, and market conditions, may also contribute. This analysis does not establish causation.

## 4. Finding Three: Mild Negative Prices Made Up a Larger Share of Events in 2025

Negative-price hours were grouped into five severity bands and compared as a share of all negative-price hours in each year.

| Negative-price range | 2024 hours | 2024 share | 2025 hours | 2025 share |
|---|---:|---:|---:|---:|
| Below -100 EUR/MWh | 5 | 1.1% | 13 | 2.3% |
| -100 to -50 EUR/MWh | 22 | 4.8% | 17 | 3.0% |
| -50 to -20 EUR/MWh | 61 | 13.3% | 54 | 9.4% |
| -20 to -10 EUR/MWh | 49 | 10.7% | 51 | 8.9% |
| -10 to 0 EUR/MWh | 320 | 70.0% | 438 | 76.4% |
| **Total negative-price hours** | **457** | **100.0%** | **573** | **100.0%** |

Mild negative prices, between -10 and 0 EUR/MWh, represented 70.0% of negative-price hours in 2024 and 76.4% in 2025. This is an increase of 6.4 percentage points.

The number of hours below -100 EUR/MWh increased from 5 in 2024 to 13 in 2025. Although this represents an increase in the observed extreme-price share from 1.1% to 2.3%, the counts remain small.

**Interpretation:** Negative prices became more frequent in 2025, and their distribution shifted toward the mildest negative-price band. At the same time, the dataset recorded more hours below -100 EUR/MWh. The annual minimum price was also more extreme in 2025 (-250.32 EUR/MWh versus -135.45 EUR/MWh in 2024), but this single extreme does not mean negative prices were generally more severe. The mean and median negative prices were nearly unchanged between years.

**Visualization:** `negative_price_severity_2024_2025.png`

## 5. Data Coverage and Limitations

- The combined dataset contains 17,541 matched hourly records for 2024 and 2025.
- The 2024 dataset contains 8,784 records, covering the leap year.
- The 2025 dataset contains 8,757 records. The final three hours of the year are absent from the source data.
- All price timestamps matched generation timestamps in the combined dataset.
- February, November, and December 2025 had no observed negative-price hours, so negative-versus-nonnegative generation comparisons are unavailable for those months.
- The severity-band percentages describe the distribution of observed negative-price hours, not the share of all hours in a year.
- The analysis is descriptive. It does not control for demand, imports and exports, conventional generation, or other factors that can influence electricity prices.
- The selected renewable-generation measure includes the wind and solar components available in this dataset; it should not be interpreted as a complete measure of every renewable energy source.

## 6. Conclusion

The analysis identifies a clear increase in negative-price frequency during May and June 2025, alongside higher average solar generation during negative-price hours in those months.

The severity analysis adds that mild negative prices accounted for a larger share of negative-price events in 2025, while the observed number of hours below -100 EUR/MWh also increased. These are descriptive patterns, not evidence of causation.

Together, the findings provide a starting point for deeper investigation into the relationship between renewable generation and electricity-market prices. Further analysis is needed before drawing conclusions about causes or implications for market participants.
