# UPTC EcoEnergy — Despliegue local (rama: lilian)

Instrucciones rápidas para ejecutar la pila completa (base de datos, backend, frontend y bot Telegram) en local usando Docker Compose.

Requisitos:
- Docker y Docker Compose instalados
- Variables de entorno configuradas en los archivos `.env` correspondientes

1) Configura variables de entorno
- `telegram_bot/.env`: añade `TELEGRAM_BOT_TOKEN` y opcionalmente `OPENAI_API_KEY`.
- (Opcional) Crea/ajusta `.env` en la raíz si quieres usar sustituciones para `OPENAI_API_KEY`.

2) Construir y levantar todos los servicios en background

```bash
docker compose -f docker-compose.yml up --build -d
```

3) Ver estado y logs
- Listar contenedores y estado:

```bash
docker compose -f docker-compose.yml ps
```

- Ver logs en tiempo real (ejemplo: backend):

```bash
docker compose -f docker-compose.yml logs -f backend
```

4) Accesos
- Frontend: http://localhost:3001
- Backend API health: http://localhost:8000/health
- Bot Telegram: se ejecuta con polling; revisa logs con `logs -f telegram-bot`.

5) Detener y eliminar contenedores/volúmenes (limpieza)

```bash
docker compose -f docker-compose.yml down -v
```

Notas y troubleshooting
- Si el bot no arranca, verifica `telegram_bot/.env` y que `TELEGRAM_BOT_TOKEN` tenga el valor correcto.
- Si el backend no carga modelos ML puedes ver errores sobre `libgomp.so.1` (falta de librería en la imagen). El servicio seguirá funcionando sin predicciones.
- Si el frontend no muestra datos: abre DevTools → Network y revisa llamadas a `http://localhost:8000/api/v1/...`. También revisa que `NEXT_PUBLIC_API_URL` esté apuntando a `http://localhost:8000/api/v1`.

Si quieres, puedo crear un script `make` o un `scripts/` con atajos para los comandos anteriores.
