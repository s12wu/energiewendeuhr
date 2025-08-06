/* Shelly script, entwickelt auf Plug Plus S.
Alle 15 Min wird die aktuelle Farbe von der Energiewendeuhr ausgelesen und die Steckdose dementsprechend ein-/ausgeschaltet.

Am Shelly die WLAN-Verbindung einrichten. Tipp: Wenn unten in der Statusleiste die korrekte Uhrzeit steht, funktioniert die Internetverbindung.
Shelly Weboberfläche -> Scripts -> Create Script.
Code von hier kopieren und einfügen. Gewünschten Schwellwert setzen (siehe unten). Mit "Save" speichern.
Links in der Navigation nochmal auf "Scripts". Für das gerade erstellte "Run on startup" aktivieren, dann mit dem Play-Symbol neben "Status" starten.
*/

let CONFIG = {
  /* Hier den gewünschten Schwellwert eintragen, ab dem die Steckdose angeschaltet wird:
  1 - rot und höher: also immer an
  2 - orange und höher
  3 - gelb und höher
  4 - nur bei grün
  
  ! 0 - Modus Balkonkraftwerk: Dann einschalten, wenn in Waiblingen die Sonne scheint. wurde abgeschafft (6. August 2025), !
  ! weil ich dazu bei mir zuhause die Helligkeit messen musste und es niemand benutzt hat.                                 !
  ! An dieser Stelle wird jetzt eine 1 gesendet, wenn der aktuelle Erneuerbaren-Anteil mindestens Gelb (30%) ist.          !
  ! So schaltet eine Steckdose immer noch grob passend an und aus, wenn sie auf BALKON gestellt ist, auch wenn ich keine   !
  ! echten Messwerte mehr erhebe.                                                                                          !
  */
  min_color: 3
};

function processHttpResponse(result, error_code, error) {
  if (error_code != 0) {
    print("HTTP error"); // könnte man das besser lösen? ja.
  } else {
    /* body format "renewable fraction now, color now, 1h, 2h, 3h, 4h, 5h, balkon,"
    for example "0.55464412950202,4,3,3,2,1,1,1," */
    if (CONFIG.min_color > 0){
      let current_color = result.body.split(",")[1];
      
      if (current_color >= CONFIG.min_color) {
        Shelly.call("Switch.set", {'id': 0, 'on': true});
      } else {
        Shelly.call("Switch.set", {'id': 0, 'on': false});
      }
    } else {
      // balkon mode
      if (result.body.split(",")[7] == 1) {
        Shelly.call("Switch.set", {'id': 0, 'on': true});
      } else {
        Shelly.call("Switch.set", {'id': 0, 'on': false});
      }
    }
  }
};


function energiewendeUpdate() {
  Shelly.call("HTTP.GET", {url: "https://wieland.srvx.de/energiewende/rawvalues.php"}, processHttpResponse);
};

energiewendeUpdate();
Timer.set(
  /* number of miliseconds (15 min=900000)*/ 900000,
  /* repeat? */ true,
  /* callback */ energiewendeUpdate
);
