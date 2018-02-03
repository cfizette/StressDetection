unsigned long interval = 1000;
unsigned long start = 0;
unsigned long current = 10000;
int delayTime = 4;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(19200);
  

}

void loop() {
  // put your main code here, to run repeatedly:
  start = millis();
  current = millis();
  

  while(current-start < interval){
    Serial.println(100);
    delay(delayTime);
    current = millis();
  }

  start = millis();
  current = millis();

  while(current-start < interval){
    Serial.println(0);
    delay(delayTime);
    current = millis();
  }

  

}
