#include "WiFi.h"

#define BAUD_RATE 115200

void sendScanResult(const char* result) {
    Serial.write(result, strlen(result));
}

void scan_wifi(int nb_scan) {
    Serial.println(F("Start"));
    for (int n = 0; n < nb_scan; ++n) {
        int nb_network = WiFi.scanNetworks();
        if (nb_network == 0) {
            sendScanResult("No Networks\n");
        } else {
            char buffer[128];
            snprintf(buffer, sizeof(buffer), "%d Networks\n", nb_network);
            sendScanResult(buffer);
            for (int i = 0; i < nb_network; ++i) {
                snprintf(buffer, sizeof(buffer), "%d | %s | %d | %d | %s\n",
                         i + 1,
                         WiFi.SSID(i).c_str(),
                         WiFi.RSSI(i),
                         WiFi.channel(i),
                         WiFi.BSSIDstr(i).c_str());
                sendScanResult(buffer);
            }
        }
    }
    sendScanResult("End Scan\n");
}

void setup() {
    Serial.begin(BAUD_RATE);
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    Serial.println(F("Setup done"));

    while (!Serial.available()) {
        // Attendre jusqu'à ce que des données soient disponibles sur le port série
    }
    int nb_scan = Serial.parseInt();
    scan_wifi(nb_scan);
}

void loop() {

}
