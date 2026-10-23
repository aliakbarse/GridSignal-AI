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

These figures represent average generation per observed hourly interval, not monthly generation totals.

**Interpretation:** The observed data show an association between higher solar generation and negative prices in these months. Other factors, including electricity demand, wind generation, conventional power-plant operations, cross-border electricity flows, and broader market conditions, may also contribute. This analysis does not establish causation.

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

The number of hours below -100 EUR/MWh increased from 5 in 2024 to 13 in 2025. The observed share of negative-price hours in this band rose from 1.1% to 2.3%, although the counts remain small.

The annual minimum price was also more extreme in 2025 (-250.32 EUR/MWh versus -135.45 EUR/MWh in 2024). However, this single extreme does not mean negative prices were generally more severe. The mean negative price was -11.50 EUR/MWh in 2024 and -10.95 EUR/MWh in 2025, while the median was approximately -2.01 EUR/MWh and -2.02 EUR/MWh, respectively.

**Interpretation:** Negative prices became more frequent in 2025, and their distribution shifted toward the mildest negative-price band. At the same time, the dataset recorded more hours below -100 EUR/MWh. These patterns show why frequency and severity should be examined separately.

**Visualization:** `negative_price_severity_2024_2025.png`

## 5. Finding Four: Higher Solar Generation Was Consistent Across Eligible Months

A monthly consistency analysis compared average solar generation during negative-price hours with average solar generation during nonnegative-price hours. To reduce reliance on months with very few negative-price observations, the analysis used a screening threshold of at least 30 negative-price hours per month.

Across the 2024–2025 dataset:

- **13 year-month combinations** met the 30-hour threshold.
- In all 13 eligible combinations, average solar generation was higher during negative-price hours.
- The mean monthly difference was 20,334.1 MWh, while the median monthly difference was 19,167.5 MWh.
- The median relative difference was 245.8%.
- The smallest eligible monthly difference was 1,818.9 MWh, and the largest was 29,726.7 MWh.

The mean monthly difference remained positive when any single eligible month was excluded. In this leave-one-month-out sensitivity check, the mean ranged from 19,551.4 to 21,877.0 MWh.

These comparisons use averages across observed hourly intervals within each price category. The differences are not monthly generation totals.

**Interpretation:** The positive association between solar generation and negative prices was consistent across the eligible year-month combinations, and the direction of the average difference did not depend on any single month. This supports treating the relationship as a priority for further investigation.

However, the 30-hour threshold is a practical screening rule, not a formal statistical significance test. The eligible months are not independent experimental observations, and the analysis does not isolate solar generation from other potential influences. In particular, it does not control for time of day, demand, wind generation, conventional generation, or cross-border electricity flows.

**Supporting analysis:** `monthly_solar_consistency_2024_2025.csv`

**Visualization:** `monthly_solar_comparison_2024_2025.png`

## 6. Finding Five: Negative Prices Were Concentrated Around Midday

An hourly analysis examined the proportion of observed intervals with negative prices at each German local hour. The rate was calculated separately for 2024 and 2025 using the observed intervals for each hour as the denominator.

The highest hourly negative-price rates were:

| Year | Hour of peak rate (German local time) | Negative-price hours | Observed hours | Negative-price rate |
|---|---:|---:|---:|---:|
| 2024 | 14:00 | 75 | 366 | 20.49% |
| 2025 | 13:00 | 99 | 365 | 27.12% |

The highest observed hourly rate increased by approximately 6.63 percentage points between these two annual peaks. The peak shifted from 14:00 in 2024 to 13:00 in 2025.

The hourly profiles show that negative prices were substantially more frequent during the middle of the day than overnight, particularly in 2025.

**Interpretation:** Negative-price frequency varied considerably by time of day. The midday concentration is consistent with a potential relationship between periods of high solar generation and negative prices, but the hourly frequency pattern alone cannot establish the mechanism behind it.

**Visualization:** `hour_of_day_analysis_2024_2025.png`

## 7. Finding Six: Solar Generation Was Generally Higher During Daytime Negative-Price Hours

The hourly solar analysis compared average solar generation during negative-price and nonnegative-price intervals at each hour, separately for 2024 and 2025.

The results show that average solar generation was generally higher during negative-price hours through much of the daytime in both years. For example, at 11:00 in 2025:

- Average solar generation during negative-price hours was approximately 35,216 MWh.
- Average solar generation during nonnegative-price hours was approximately 22,946 MWh.

The difference was approximately 12,270 MWh per observed hourly interval, or about 53% relative to the nonnegative-price average.

The daytime comparison is descriptive. It does not show that high solar generation independently caused negative prices. The observed differences may also reflect other factors associated with the timing of negative-price intervals, including electricity demand, wind generation, conventional generation, and cross-border electricity flows.

Some overnight hour-and-price-category combinations contain very few observations. In particular, the hourly averages based on fewer than 30 negative-price intervals should be treated cautiously. The 30-observation threshold is a practical warning, not a statistical significance test.

**Interpretation:** The hourly analysis adds a time-of-day perspective to the monthly findings. It shows that the association between solar generation and negative prices is particularly visible during daytime hours, while also demonstrating why hourly sample sizes and other market factors matter when interpreting the relationship.

**Supporting analyses:**
- `hourly_negative_price_frequency_2024_2025.csv`
- `hourly_solar_by_price_category_2024_2025.csv`
- `seasonal_price_and_solar_summary_2024_2025.csv`

**Visualization:** `hour_of_day_analysis_2024_2025.png`

## 8. Data Coverage and Limitations

- The combined dataset contains 17,541 matched hourly records for 2024 and 2025.
- The 2024 dataset contains 8,784 records, covering the leap year.
- The 2025 dataset contains 8,757 records. The final three hours of the year are absent from the source data.
- All price timestamps matched generation timestamps in the combined dataset.
- February, November, and December 2025 had no observed negative-price hours, so negative-versus-nonnegative generation comparisons are unavailable for those months.
- The severity-band percentages describe the distribution of observed negative-price hours, not the share of all hours in a year.
- The solar-consistency analysis includes 13 year-month combinations meeting the 30-negative-hour screening threshold. The threshold is a practical rule, not a statistical significance criterion.
- Hourly frequency rates use observed intervals as their denominators. Local daylight-saving transitions can result in different observation counts for certain hours.
- Some hourly solar averages during negative-price intervals are based on fewer than 30 observations and should be interpreted cautiously.
- The analysis is descriptive. It does not control for demand, imports and exports, conventional generation, time of day in the monthly comparisons, or other factors that can influence electricity prices.
- The selected renewable-generation measure includes the wind and solar components available in this dataset; it should not be interpreted as a complete measure of every renewable energy source.
- Before publication, verify the original SMARD field definitions and units for generation data. The numerical differences reported here are preserved from the analysis output and should not be interpreted as monthly totals.
- The dataset covers 2024–2025 and should not automatically be assumed to represent future market conditions.

## 9. Conclusion

The analysis identifies a clear increase in negative-price frequency during May and June 2025, alongside higher average solar generation during negative-price hours in those months.

The severity analysis shows that mild negative prices accounted for a larger share of negative-price events in 2025, while the observed number of hours below -100 EUR/MWh also increased. These findings demonstrate that negative-price frequency and severity provide different perspectives on market conditions.

The monthly consistency analysis adds evidence that higher solar generation coincided with negative prices in all 13 year-month combinations meeting the screening threshold. The direction of the average difference remained positive when any one eligible month was excluded.

The hourly analysis adds a temporal dimension: negative prices peaked around midday in both years, and average solar generation was generally higher during daytime negative-price intervals. These patterns are consistent with a relationship worth investigating further, but they do not establish causation or isolate the effects of individual market factors.

Together, the findings provide a foundation for deeper investigation into the relationship between renewable generation and electricity-market prices. Further work should examine additional market variables and account for time-of-day effects before drawing conclusions about causes or implications for market participants.
