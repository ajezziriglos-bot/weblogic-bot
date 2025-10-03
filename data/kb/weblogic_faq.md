# FAQ WebLogic

## Reinicio seguro de WebLogic (AdminServer / ManagedServer)
**Prerrequisitos**
- Avisar ventana de mantenimiento y usuarios.
- Identificar DOMAIN_HOME y Admin URL.

**Pasos**
1) Parar con scripts:
   - AdminServer: `stopWebLogic.sh`
   - ManagedServer: `stopManagedWebLogic.sh <ServerName> http://<adminhost>:7001`
2) Validar que no quede el proceso (ps/Task Manager). Evitar `kill -9` salvo último recurso.
3) Iniciar:
   - AdminServer: `startWebLogic.sh`
   - ManagedServer: `startManagedWebLogic.sh <ServerName> http://<adminhost>:7001`
4) Verificar health en `/console` y revisar logs:
   - `<DOMAIN_HOME>/servers/<ServerName>/logs/<ServerName>.log`

**Notas**
- Si un Managed no baja con el script, intentar `nmKill` vía NodeManager antes de `kill -9`.
