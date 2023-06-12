// Programa Grupo 3
// PARAMETROS:
int arT = 1;  // articulos (1 = clavos pequeños, 2 = clavos medianos, 3 = clavos grandes)
//double pesoS = 0.2; // peso solicitado
int clavosSolictados = 25;  // cargar aca la solitud de cavos
int clavosReales = 0;       // definimos la vafibale clavos que hay en la balanza
double pesoR = 0;


//Balanza
#include "HX711.h"
#define POWER_PIN 7
#define POWER_PINN 8
const int DOUT = A0;  // Data A0
const int CLK = A1;   // Hora A1
HX711 balanza;



// Motores Paso a Paso
#define STEP1 4  // pin STEP de A4988 a pin 4 digital
#define DIR1 5   // pin DIR de A4988 a pin 5 digital
#define STEP2 2  // pin STEP pin 2 digital
#define DIR2 3   // pin DIR pin 3 digital

//---------------------------

void setup() {
  // Configuracion Balanza
  Serial.begin(9600);
  balanza.begin(DOUT, CLK);
  Serial.println(balanza.read());
  balanza.set_scale(211600);  // Establecemos la escala --> este numero primero sale del codigo de calibracion de balanza
  balanza.tare(20);           //El peso actual es considerado Tara.
  //Serial.println("Listo para pesar");
  // Motores
  pinMode(STEP1, OUTPUT);  // pin 4 como salida
  pinMode(DIR1, OUTPUT);   // pin 5 como salida
  pinMode(STEP2, OUTPUT);  // pin 2 como salida
  pinMode(DIR2, OUTPUT);   // pin 3 como salida
  // puerto 5v
  pinMode(POWER_PIN, OUTPUT);
  digitalWrite(POWER_PIN, HIGH);
  pinMode(POWER_PINN, OUTPUT);
  digitalWrite(POWER_PINN, HIGH);
}


void loop() {

  if (Serial.available() > 0) {            // Si hay datos disponibles en el puerto serial
    clavosSolictados = Serial.parseInt();  // Leer un valor entero y asignarlo al parámetro
    Serial.print("Clavos solicitados: ");  // Imprimir un mensaje de confirmación
    Serial.println(clavosSolictados);
    char arTValue = Serial.read();           // Leer una cadena de texto y asignarla al parámetro
    Serial.print("Tipo de artículo: ");  // Imprimir un mensaje de confirmación
    Serial.println(arTValue);
    switch (arTValue) {  // Asignar el valor numérico según el identificador
      case 'C':
        arT = 1;
        break;
      case 'M':
        arT = 2;
        break;
      case 'G':
        arT = 3;
        break;
      default:
        Serial.println("Identificador inválido");
        exit(0);
    }
  }

  if (clavosSolictados == 0 || clavosSolictados < 0) {  // Si el valor es 0 o negativo
    Serial.println("Valor inválido de clavos solicitados");                         // Imprimir un mensaje de error
    exit(0);                                                                        // Salir del loop
  }

  // necesitamos psar de peso a unidades, con el siguiente if podemos saber el numero de clavos en la balanza segun el tamaño de clavos
  pesoR = balanza.get_units(20);
  if (arT == 1) {
    clavosReales = pesoR * 2500;
  } else if (arT == 2) {
    clavosReales = pesoR * 1000;
  } else if (arT == 3) {
    clavosReales = pesoR * 500;
  }


  delay(1000);
  if (clavosReales < clavosSolictados) {  // si el N° real es menor que el peso solicitado necesita mas clavos,

    if (arT == 1) {
      Serial.println(pesoR * 2500, 0);  // 40 calvos son 20 gramos
    } else if (arT == 2) {
      Serial.println(pesoR * 1000, 0);  //
    } else if (arT == 3) {
      Serial.println(pesoR * 500, 0);  //
    }

    //Aca deberia ir la señal al robot de festo

  } else {
    if (arT == 1) {
      descarga();  // realizamos descarga en la posicion de 1 (home)
    } else if (arT == 2) {
      rotacionUno();  // rotamos hasta la posicion 2
      delay(1000);
      descarga();  // descargamos
      delay(10);
      rotacionUnoVuelta();  // volvemos al home
    } else if (arT == 3) {
      rotacionDos();  // rotamos hasta la posicion 3
      delay(1000);
      descarga();  //descargamos
      delay(10);
      rotacionDosVuelta();  // volvemos a home
    }
  }
}
//----------------------------------------------------------------------------------
//funciones

//codigo para la descarga
void descarga() {

  digitalWrite(DIR1, LOW);         //giro en un sentido (configurar)
  for (int i = 0; i < 250; i++) {  // cada paso es 1.8°, 200 pasos es una vuelta completa son 45° de inclincacion de la balanza.
    digitalWrite(STEP1, HIGH);
    delay(2);
    digitalWrite(STEP1, LOW);
    delay(2);  // en estas 4 lineas generamos un paso (esto como esta en un for se repite 400 veces)
  }
  for (int j = 0; j < 11; j++) {
    for (int i = 0; i < 20; i++) {
      digitalWrite(DIR1, HIGH);
      digitalWrite(STEP1, HIGH);
      delay(3);
      digitalWrite(STEP1, LOW);
      delay(3);
    }
    for (int i = 0; i < 20; i++) {
      digitalWrite(DIR1, LOW);
      digitalWrite(STEP1, HIGH);
      delay(3);
      digitalWrite(STEP1, LOW);
      delay(3);
    }
  }
  delay(2);  // damos 2 segudnos para qe caigan todos los calvos

  digitalWrite(DIR1, HIGH);  // giramos en el sentido opuesto para volver a la posición incicial
  for (int j = 0; j < 250; j++) {
    digitalWrite(STEP1, HIGH);
    delay(2);
    digitalWrite(STEP1, LOW);
    delay(2);
  }
  delay(1000);
}
//------------------------
void rotacionUno() {

  digitalWrite(DIR1, HIGH);  // giro en un sentido
  digitalWrite(DIR2, LOW);
  for (int i = 0; i < 200; i++) {  // 200 pasos para motor de 0.9 grados de angulo de paso
    digitalWrite(STEP1, HIGH);
    delay(2);
    digitalWrite(STEP2, HIGH);
    delay(2);
    digitalWrite(STEP1, LOW);
    delay(2);
    digitalWrite(STEP2, LOW);
    delay(2);
  }
}
//------------------------

void rotacionUnoVuelta() {

  digitalWrite(DIR1, LOW);  // giro en un sentido
  digitalWrite(DIR2, HIGH);
  // digitalWrite(DIR2, LOW);
  for (int i = 0; i < 200; i++) {  // 200 pasos para motor de 0.9 grados de angulo de paso
    digitalWrite(STEP1, HIGH);
    delay(3);
    digitalWrite(STEP2, HIGH);
    delay(3);
    digitalWrite(STEP1, LOW);
    delay(3);
    digitalWrite(STEP2, LOW);
    delay(3);
  }
}
//------------------------

void rotacionDos() {

  digitalWrite(DIR1, HIGH);  // giro en un sentido
  digitalWrite(DIR2, LOW);
  // digitalWrite(DIR2, LOW);
  for (int i = 0; i < 415; i++) {  // 200 pasos para motor de 0.9 grados de angulo de paso
    digitalWrite(STEP1, HIGH);
    delay(1);
    digitalWrite(STEP2, HIGH);
    delay(1);
    digitalWrite(STEP1, LOW);
    delay(1);
    digitalWrite(STEP2, LOW);
    delay(1);
  }
}
//------------------------

void rotacionDosVuelta() {

  digitalWrite(DIR1, LOW);  // giro en un sentido
  digitalWrite(DIR2, HIGH);
  // digitalWrite(DIR2, LOW);
  for (int i = 0; i < 415; i++) {  // 200 pasos para motor de 0.9 grados de angulo de paso
    digitalWrite(STEP1, HIGH);
    delay(1);
    digitalWrite(STEP2, HIGH);
    delay(1);
    digitalWrite(STEP1, LOW);
    delay(1);
    digitalWrite(STEP2, LOW);
    delay(1);
  }
}