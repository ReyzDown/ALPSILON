#include "NimBLEDevice.h"

NimBLEScan* pBLEScan;

class MyAdvertisedDeviceCallbacks: public NimBLEAdvertisedDeviceCallbacks {
    void onResult(NimBLEAdvertisedDevice* advertisedDevice) {
      Serial.printf("Advertised Device: %s \n", advertisedDevice->toString().c_str());
    }
};
void sendScanResult(const char* result) {
    Serial.write(result, strlen(result));
}

void setup() {
    Serial.begin(115200);
    Serial.println("Scanning...");


    NimBLEDevice::setScanFilterMode(CONFIG_BTDM_SCAN_DUPL_TYPE_DEVICE);

    NimBLEDevice::setScanDuplicateCacheSize(200);

    NimBLEDevice::init("");

    pBLEScan = NimBLEDevice::getScan(); //create new scan
    // Set the callback for when devices are discovered, no duplicates.
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks(), false);
    pBLEScan->setActiveScan(true); // Set active scanning, this will get more data from the advertiser.
    pBLEScan->setInterval(97); // How often the scan occurs / switches channels; in milliseconds,
    pBLEScan->setWindow(37);  // How long to scan during the interval; in milliseconds.
    pBLEScan->setMaxResults(0); // do not store the scan results, use callback only.

    while (!Serial.available()) {
    // Attendre jusqu'à ce que des données soient disponibles sur le port série
    } 
    int nb_scan = Serial.parseInt();
    for(int i=0; i<nb_scan;i++){
        if(pBLEScan->isScanning() == false) {
            // Start scan with: duration = 0 seconds(forever), no scan end callback, not a continuation of a previous scan.
            pBLEScan->start(5, nullptr, false);
        }
    }
    sendScanResult("End Scan\n");

}

void loop() {
}