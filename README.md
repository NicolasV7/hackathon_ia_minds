# UPTC EcoEnergy — Setup notes

Breve instrucciones para configurar variables de entorno locales y cómo usar GitHub Secrets.

**Configurar `.env` localmente:**
- Copia el ejemplo: `cp .env.example .env`.
- Edita `.env` y completa **solo** los valores locales (`TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, credenciales de DB, etc.).
- NO cometas `.env` al repositorio. `.env` está en `.gitignore`.

Comandos útiles:
```bash
# copiar y editar
cp .env.example .env
# editar .env con tu editor favorito
nano .env

# levantar el bot (usa variables del archivo .env)
docker compose -f docker-compose.telegram.yml up --build
```

**Usar GitHub Secrets (para despliegues / CI):**
- En GitHub, ve a Settings → Secrets → Actions → New repository secret.
- Crea secretos llamados `TELEGRAM_BOT_TOKEN` y `OPENAI_API_KEY` (o los nombres que uses en workflows).
- En GitHub Actions usa los secretos así:
```yaml
env:
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

Para despliegues con Docker Compose en entornos remotos, usa Docker secrets o variables de entorno del host en vez de archivos `.env` comprometidos.

**Seguridad / pasos recomendados ahora:**
- Si alguna clave estuvo expuesta accidentalmente, revócala en el proveedor (por ejemplo, rota la API key en OpenAI Dashboard).
- Si necesitas eliminar claves del historial git de forma segura, usa `git filter-repo` o `bfg` (te puedo ayudar con los pasos).

Si quieres, añado un ejemplo de workflow de GitHub Actions que despliegue el bot usando los Secrets.
