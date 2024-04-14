#include <Adafruit_GFX.h>
#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;
#include <TouchScreen.h>
#define MINPRESSURE 100
#define MAXPRESSURE 2000
#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define MAGENTA 0xF81F
#define YELLOW   0xFFE0
#define WHITE   0xFFFF
#define RED     0xF800

unsigned long previousMillis = 0;
const int interval = 10;  // Refresh interval in milliseconds

// ALL Touch panels and wiring is DIFFERENT
// copy-paste results from TouchScreen_Calibr_native.ino
const int XP = 6, XM = A2, YP = A1, YM = 7; //ID=0x9341

const int TS_LEFT = 910, TS_RT = 169, TS_TOP = 900, TS_BOT = 180;

const String dataUnavailableString = "N/A";

TouchScreen ts = TouchScreen(XP, YP, XM, YM, 300);

int Started = 0;

Adafruit_GFX_Button on_btn;

int pixel_x, pixel_y;     //Touch_getXY() updates global vars
int button;
int onMode = 0;

void serialFlush(){
                  while(Serial.available() > 0) {
                    char t = Serial.read();
                  }
                }

bool Touch_getXY(void)
{
    TSPoint p = ts.getPoint();
    pinMode(YP, OUTPUT);      //restore shared pins
    pinMode(XM, OUTPUT);
    digitalWrite(YP, HIGH);   //because TFT control pins
    digitalWrite(XM, HIGH);
    bool pressed = (p.z > MINPRESSURE && p.z < MAXPRESSURE);
    if (pressed) {
        // Serial.println("P.X:"+String(p.x));
        // Serial.println("P.Y:"+String(p.y));
        pixel_x = map(p.x, TS_RT, TS_LEFT,  0, tft.width()); //.kbv makes sense to me
        pixel_y = map(p.y, TS_TOP, TS_BOT, 0, tft.height());
        // Serial.println("X:"+String(pixel_x));
        // Serial.println("Y:"+String(pixel_y));
        // Serial.println("");
        tft.setTextColor(WHITE, BLACK);
        if (pixel_y<=-25){
            button = 0;
            if (onMode == 0) {
                on_btn.initButton(&tft, 40, 70, 80, 50, WHITE, MAGENTA, WHITE, "J.I.P", 2);
                onMode = 1;
            } else {
                onMode = 0;
            }
            on_btn.drawButton(true);
        }
        if(pixel_y>-25){
          button = 2;
        }

    }
    //   tft.drawLine(160, 239,x,y, WHITE);
    if(pressed){
          tft.setTextSize(2);
       
          tft.setCursor(110,45);
          delay(1000);
          int textX = 110;
          int textY = 45;
          int textWidth = 200; 
          int textHeight = 20;
          uint16_t backgroundColor = BLACK;
          tft.fillRect(textX, textY, textWidth, textHeight, backgroundColor);
    }
    delay(200);
    return pressed;
}

String getSensorData() {
  unsigned long startTime = millis();
  while (millis() - startTime < 1000) { // Wait for up to 1000 milliseconds (1 second)
    if (Serial.available() > 0) {
      String data = Serial.readStringUntil('\n');
      return data;
    }
  }
  return dataUnavailableString;
}

void printValues() {

            String sensorString = getSensorData();
            int firstDelimiterIndex = sensorString.indexOf('|');
            int secondDelimiterIndex = sensorString.indexOf('|', firstDelimiterIndex + 1);
            int thirdDelimiterIndex = sensorString.indexOf('|', secondDelimiterIndex + 1);
            int fourthDelimiterIndex = sensorString.indexOf('|', thirdDelimiterIndex + 1);
            int fifthDelimiterIndex = sensorString.indexOf('|', fourthDelimiterIndex + 1);

            // Extract elapsed time value
            String elapsedStr = sensorString.substring(0, firstDelimiterIndex);

            // Extract CO value
            String carbonMonoxideStr = sensorString.substring(firstDelimiterIndex + 1, secondDelimiterIndex);

            // Extract LEL value
            String lelStr = sensorString.substring(secondDelimiterIndex + 1, thirdDelimiterIndex);

            // Extract H2S value
            String h2sStr = sensorString.substring(thirdDelimiterIndex + 1, fourthDelimiterIndex);

            // Extract JOB value
            String jobStr = sensorString.substring(fourthDelimiterIndex + 1, fifthDelimiterIndex);

            // Extract current time
            String currentTimeStr = sensorString.substring(fifthDelimiterIndex + 1, sensorString.length() - 3);

              tft.setTextSize(2);
   tft.fillRect(0,25,320,240,BLACK);
                tft.fillRect(100, 180, 100, 30, BLACK);

if (sensorString.indexOf("SOS") != -1) {
   tft.fillRect(0,25,320,240,RED);

            String currentTimeStr = sensorString.substring(fifthDelimiterIndex + 1, sensorString.length() - 9);
 }

              // Display the JSON data on the TFT LCD
              tft.setCursor(100, 100);
              if (sensorString.indexOf("SOS") == -1){
                            tft.fillRect(100, 100, 100, 30, BLACK);}
              tft.setTextColor(WHITE);
              tft.print("ELAPSED:  ");
              tft.print(elapsedStr);

              tft.setCursor(100, 120);
              if (sensorString.indexOf("SOS") == -1){
                            tft.fillRect(100, 120, 100, 30, BLACK);}
              tft.setTextColor(WHITE);
              tft.print("CO:  ");
              tft.print(carbonMonoxideStr);
              tft.print(" ppm");
              
              tft.setCursor(100, 140);
              if (sensorString.indexOf("SOS") == -1){
                            tft.fillRect(100, 140, 100, 30, BLACK);}
              tft.setTextColor(WHITE);
              tft.print("LEL: ");
              tft.print(lelStr);
              tft.print(" %");

              tft.setCursor(100, 160);
              if (sensorString.indexOf("SOS") == -1){
                            tft.fillRect(100, 160, 100, 30, BLACK);}
              tft.setTextColor(WHITE);
              tft.print("H2S: ");
              tft.print(h2sStr);
              tft.print(" ppm");

              if (sensorString.indexOf("SOS") != -1) {
                tft.setCursor(100, 180);
                tft.setTextColor(WHITE);
                tft.print("EVACUATE NOW!");
              }

               tft.fillRect(0,0,320,25,WHITE);
               tft.setTextColor(BLACK);
               tft.setCursor(0,5);
               tft.print(currentTimeStr);
               tft.print("         Job #"+jobStr);
               serialFlush();
               Serial.println("ACK");

              
}


float i=0;
int randomvalue=-90;
int returnx=0;
float angle,x,y;
bool down;
unsigned long old =0;
unsigned long current =0;
void setup(void)
{
    Serial.begin(9600);
    uint16_t ID = tft.readID();
    Serial.print("TFT ID = 0x");
    Serial.println(ID, HEX);
    Serial.println("Calibrate for your Touch Panel");
    if (ID == 0xD3D3) ID = 0x9486; // write-only shield
    tft.begin(ID);
    tft.setRotation(3);            //PORTRAIT
    tft.setTextSize(3);


    tft.fillScreen(BLACK);
    tft.setTextColor(YELLOW);

    tft.setTextSize(1);

    tft.println("      __,");
    tft.println("   .-'  / ");
    tft.println(" .'    /   /`.");
    tft.println(" |    /   /  |     .----.         .---.");
    tft.println(" |    \__/   |    '---,  `._____.'  _  `.");
    tft.println(" `.         .'         )   _____   <_>  :");
    tft.println("   `.     .'      .---'  .'     `.     .'");
    tft.println("     | ][ |       `----'          `---'");
    tft.println("     | ][ |");
    tft.print("     | ][ |");
    tft.setTextColor(WHITE);
    tft.println("     ____  __  ____ ____ ");
    tft.setTextColor(YELLOW);
    tft.print("     | ][ |");
    tft.setTextColor(WHITE);
    tft.println("    / ___)/ _\(  __(  __)");
    tft.setTextColor(YELLOW);
    tft.print("     | ][ |");
    tft.setTextColor(WHITE);
    tft.println("    \___ /    \) _) ) _)");
    tft.setTextColor(YELLOW);
    tft.print("     | ][ |");
    tft.setTextColor(WHITE);
    tft.println("    (____\_/\_(__) (____)");
    tft.setTextColor(YELLOW);
    tft.println("     | ][ |");
    tft.println("     | ][ |");
    tft.print("     | ][ |");
    tft.setTextColor(WHITE);
    tft.println("           ____ ____  __   ___ ____ ");
    tft.setTextColor(YELLOW);
    tft.print("   .'  __  `.");
    tft.setTextColor(WHITE);
    tft.println("        / ___(  _ \/ _\ / __(  __)");
    tft.setTextColor(YELLOW);
    tft.print("   |  /  \  | ");
    tft.setTextColor(WHITE);
    tft.println("         \___ \) __/    ( (__ ) _)");
    tft.setTextColor(YELLOW);
    tft.print("   |  \__/  |");
    tft.setTextColor(WHITE);
    tft.println("        (____(__) \_/\_/\___(____)");
    tft.setTextColor(YELLOW);
    tft.println("   `.      .'");
    tft.println("     `----'");


 


   delay(2500);

    tft.fillScreen(BLACK);
    tft.setTextColor(WHITE);
   tft.setCursor(0,0);
   tft.println("");
   tft.setTextSize(4);
   tft.println("SafeSpace");
    tft.setTextColor(YELLOW);
   tft.setTextSize(1);
   tft.println("");
   tft.println("Aaditya Rengarajan (21Z202)");
   tft.println("Hareesh S (21Z218)");
   tft.println("Kavin Dev R (21Z224)");
   tft.println("S Karun Vikhash (21Z247)");
   tft.println("Sanjay Kumaar Eswaran (21Z248)");
   delay(2500);

    tft.fillScreen(BLACK);
    on_btn.initButton(&tft,  40, 70, 80, 50, WHITE, MAGENTA, WHITE, "Start", 2);
    
    on_btn.drawButton(false);

    
    i=randomvalue;
    
   tft.setTextSize(2);
   tft.fillRect(0,0,320,25,WHITE);
   tft.setTextColor(BLACK);
   tft.setCursor(0,5);
   tft.print("SafeSpace | Gas Detector");
  //tft.setTextColor(YELLOW,BLACK);
}

void loop(void)
{   
  if(Started==1){
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval) {
        // Update display here
        printValues();  // Example function to update display
        previousMillis = currentMillis;
    }
  }

   down = Touch_getXY();
   
  //  Serial.println("Print");
  //  Serial.println("Wait");
    if (down)
    {
          Started = 1;
              tft.fillScreen(BLACK);

            
            on_btn.press(down && pixel_y<-15);        
            if (on_btn.justPressed() || button == 0 ) 
            {
               on_btn.press(false);
            }
  
  }
}