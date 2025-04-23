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

$query = 'from(bucket: "energiewendeuhr")
  |> range(start: now(), stop: 7h)
  |> filter(fn: (r) => r["_measurement"] == "renewableFraction")
  |> filter(fn: (r) => r["_field"] == "fraction")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({
      r with
      color: 
        if r._value >= 0.5 then 4 // green
        else if r._value >= 0.3 then 3 // yellow
        else if r._value >= 0.2 then 2 //orange
        else 1 // red
  }))
  |> yield(name: "mean_with_color")';

$tables = $client->createQueryApi()->query($query, 'energiewendeuhr');

$renewableForecast = [0,0,0,0,0,0];  // renewable fraction now, 1h, 2h, 3h, 4h, 5h
$colorNumbers = [0,0,0,0,0,0]; // 1=red; 2=orange; 3=yellow; 4=green

$i = 0;
foreach ($tables[0]->records as $record) {
    $renewableForecast[$i] = $record->getValue();
    $colorNumbers[$i] = $record->values["color"];
    $i += 1;
    if ($i >= 6) break;
}


// TODO: parse SMARD
$sun_fraction = 0.5;
$wind_fraction = 0.5;

// load the template and execute its php echos
$requested_template = $_GET["t"];
$templates = ["classic_light", "classic_dark", "raw", "now_fraction", "now_state"];
if (isset($requested_template) && in_array($requested_template, $templates)) {
    include("templates/$requested_template.php");
} else {
    echo "invalid template name";
}
?>
