A template will be included at the end of the main script.
They can use these variables:
$renewableForecast[]                -> 6 values 0 to 1, for now, 1h, 2h, 3h, 4h, 5h
$colors                             -> see above, but represented as hex colors
$sunForecast[] and $windForecast[]  -> 6 values 0 to 1, for now, 1h, 2h, 3h, 4h, 5h; sun and wind fractions respectively
$wind_fraction and $sun_fraction    -> the first item ("now") in each of the arrays above


available templates:
classic_light and classic_dark - for light and dark backgrounds, respectively
raw - returns the color codes for now, 1h, 2h, 3h, 4h, 5h
now_fraction - returns the current renewable fraction (e.g. 0.32456)
now_state - returns the current color code (e.g. 4 for green)

