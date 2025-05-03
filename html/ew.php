<?php
require __DIR__ . '/vendor/autoload.php'; 

use InfluxDB2\Client;
use InfluxDB2\Model\WritePrecision;
use InfluxDB2\Point;

$env = parse_ini_file('.env');

$client = new Client([
    "url" => "http://127.0.0.1:8086",
    "token" => $env["DB_TOKEN"],
]);

$query = 'a = from(bucket: "energiewendeuhr")
  |> range(start: now(), stop: 7h)
  |> filter(fn: (r) => r["_measurement"] == "renewableFraction")
  |> filter(fn: (r) => r["_field"] == "fraction")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value"])
  |> rename(columns: {_value: "a_val"})

b = from(bucket: "energiewendeuhr")
  |> range(start: now(), stop: 7h)
  |> filter(fn: (r) => r["_measurement"] == "sun_wind")
  |> filter(fn: (r) => r["_field"] == "sun_fraction_of_renewable")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value"])
  |> rename(columns: {_value: "b_val"})

c = from(bucket: "energiewendeuhr")
  |> range(start: now(), stop: 7h)
  |> filter(fn: (r) => r["_measurement"] == "sun_wind")
  |> filter(fn: (r) => r["_field"] == "wind_fraction_of_renewable")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value"])
  |> rename(columns: {_value: "c_val"})

joinAB = join(
  tables: {a: a, b: b},
  on: ["_time"]
)

joinABC = join(
  tables: {ab: joinAB, c: c},
  on: ["_time"]
)

joinABC
  |> map(fn: (r) => ({
      _time: r._time,
      renewable: r.a_val,
      sun: r.b_val * r.a_val,
      wind: r.c_val * r.a_val,
      color: if r.a_val >= 0.5 then 4      // green
             else if r.a_val >= 0.3 then 3 // yellow
             else if r.a_val >= 0.2 then 2 // orange
             else 1                        // red
  }))
';

$tables = $client->createQueryApi()->query($query, 'energiewendeuhr');

$renewableForecast = [0,0,0,0,0,0];  // renewable fraction now, 1h, 2h, 3h, 4h, 5h
$sunForecast = [0,0,0,0,0,0]; // wind fraction of renewable
$windForecast = [0,0,0,0,0,0]; // wind fraction of renewable
$colorNumbers = [0,0,0,0,0,0]; // 1=red; 2=orange; 3=yellow; 4=green

$i = 0;
foreach ($tables[0]->records as $record) {
    $renewableForecast[$i] = $record->values["renewable"];
    $sunForecast[$i] = $record->values["sun"];
    $windForecast[$i] = $record->values["wind"];
    $colorNumbers[$i] = $record->values["color"];
    $i += 1;
    if ($i >= 6) break;
}


$sun_fraction = $sunForecast[0];
$wind_fraction = $windForecast[0];

// load the template and execute its php echos
$requested_template = $_GET["t"];
$templates = ["classic_light", "classic_dark", "raw", "now_fraction", "now_state"];
if (isset($requested_template) && in_array($requested_template, $templates)) {
    include("templates/$requested_template.php");
} else {
    echo "invalid template name";
}
?>
