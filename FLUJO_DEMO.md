## Flujo de la demo

1. **Preparar entorno**
   - Terminal 1: `cd /mnt/extra_space/Redes/Firewall-Redes`.
   - Verificar que `config/reglas_firewall.json` contenga las reglas pedidas.

2. **Levantar controlador POX**
   - Ejecutar 
      - Opcion 1: `./run_with_pox.sh`.
      - Opcion 2: `./run_with_pox.sh 127.0.0.1 6633 config/reglas_firewall.json s3`  --controller_ip  --puerto --ruta_firewall_rules --switch_con_firewall
   - Esperar el mensaje “POX en marcha”.

3. **Iniciar topología en Mininet**
   - Abrir otra terminal con permisos de root.
   - Correr `sudo python3 start_mininet.py <cantidad_switches> 127.0.0.1 6633`.
   - Confirmar que la CLI de Mininet quede activa.

4. **Pruebas básicas**
   - En la CLI: `pingall` para validar conectividad general.
   - Observar en POX los logs de instalación de reglas y respuestas a los pings.

5. **Verificar reglas del firewall con iperf**
   - Bloqueo HTTP: `h3 iperf3 -s -p 80` y `h1 iperf3 -c 10.0.0.3 -p 80` (debe fallar).
   - Bloqueo UDP h1→5001: `h4 iperf3 -s -u -p 5001` y `h1 iperf3 -c 10.0.0.4 -u -p 5001`.
   - Bloqueo entre hosts elegidos: iniciar servidor en uno (`iperf3 -s`) y cliente en el otro (cualquier puerto); no debe establecerse la sesión.

6. **Capturas y evidencias**
   - Opcional: usar `tcpdump` o Wireshark en los hosts para mostrar paquetes descartados.
   - Anotar logs de POX que indiquen qué regla disparó el drop.

7. **Finalizar demo**
   - En la CLI de Mininet: `exit`.
   - Cortar POX con Ctrl+C en la primera terminal.

