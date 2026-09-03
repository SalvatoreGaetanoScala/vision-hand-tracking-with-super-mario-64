# Super Mario 64 Hand Controller

Un controller virtuale basato sul tracciamento delle mani tramite webcam, sviluppato in Python con OpenCV e MediaPipe. Questo script trasforma i movimenti delle tue mani in input della tastiera, permettendoti di giocare a Super Mario 64 muovendoti in 3D senza usare un controller fisico.

## 🎮 Come Funziona
Lo schermo della webcam è diviso verticalmente in due metà per gestire sia il movimento analogico che i pulsanti di azione:

- **Zona Sinistra (Joystick 3D - Movimento):** 
  Questa zona presenta una "zona morta" (un riquadro centrale). Spostando la mano (in particolare la base del dito medio) al di fuori di questo riquadro, attiverai il movimento nelle quattro direzioni:
  - Su / Avanti (`W`)
  - Giù / Indietro (`S`)
  - Sinistra (`A`)
  - Destra (`D`)

- **Zona Destra (Pulsanti A e B):**
  - **Salto / Tasto A:** Fai il gesto del "pizzico" unendo le punte di **pollice e indice** (Tasto `P`).
  - **Pugno / Tasto B:** Fai il gesto del "pizzico" unendo le punte di **pollice e medio** (Tasto `O`).

## 🐍 Requisiti e Versioni Python
Il progetto richiede **Python 3**. A causa delle dipendenze di libreria, è supportato ufficialmente sulle versioni da **Python 3.8 a Python 3.11** (la versione **3.10** è caldamente consigliata per la massima stabilità con MediaPipe).

Le dipendenze necessarie sono:
- `opencv-python`
- `mediapipe`
- `numpy`
- `pynput`

Puoi installare tutte le librerie necessarie tramite il terminale:
```bash
pip install opencv-python mediapipe numpy pynput
```

## 👾 Test
Il controller è stato configurato e testato con successo con la seguente configurazione:
- **ROM / Gioco:** `super Mario 64(USA).Z64`
- **Emulatore:** SIXTYFORCE (per Mac)

*(Nota: se desideri usare un emulatore diverso, assicurati di far coincidere la mappatura dei tasti nelle impostazioni dell'emulatore con quelli inviati dallo script, oppure modifica i tasti nel file Python).*

## 🚀 Avvio rapido
1. Apri l'emulatore SIXTYFORCE e vai nelle impostazioni dei controlli.
2. Assicurati che lo stick analogico sia mappato sui tasti `W` (Su), `S` (Giù), `A` (Sinistra), `D` (Destra). Mappa il tasto A dell'N64 su `P` e il tasto B su `O`.
3. Carica la ROM `super Mario 64(USA).Z64` e avvia il gioco.
4. Apri il terminale, naviga nella cartella del progetto ed esegui lo script:
   ```bash
   python main.py
   ```
5. Fai clic sulla finestra di SIXTYFORCE per portarla in primo piano: lo script ha bisogno che la finestra del gioco sia attiva per ricevere i comandi della tastiera.
6. Per chiudere correttamente il controller, clicca sulla finestra della webcam e premi il tasto `q`.
