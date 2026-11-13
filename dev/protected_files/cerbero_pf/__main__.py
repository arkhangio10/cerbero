"""Línea de órdenes: `python -m cerbero_pf <orden>` desde `dev/protected_files`."""
from __future__ import annotations

import argparse
import os
import secrets
import sys
import time
from pathlib import Path

from .config import ConfigError, is_loopback_host, load_config
from .crypto import MasterKeyError, generate_master_key_file
from .service import RequestContext, Service, ServiceError


def _service(args) -> Service:
    return Service(load_config(Path(args.config)))


def cmd_genkey(args) -> None:
    cfg = load_config(Path(args.config))
    kid = generate_master_key_file(cfg.master_key_file)
    print(f"Clave maestra creada en {cfg.master_key_file} (id {kid}).")
    print("Guárdala fuera del directorio de datos y haz una copia de seguridad separada: sin ella no se pueden "
          "abrir las exportaciones.")


def cmd_create_user(args) -> None:
    password = os.environ.get(args.password_env, "") if args.password_env else secrets.token_urlsafe(15)
    if args.password_env and not password:
        raise ServiceError(400, "no_password", f"la variable {args.password_env} está vacía")
    _service(args).create_user(args.username, password, args.display_name or "", args.email or "")
    print(f"Cuenta creada: {args.username}")
    if not args.password_env:
        print(f"Contraseña (se muestra una sola vez): {password}")


def cmd_serve(args) -> None:
    import uvicorn

    from .web import create_app

    service = _service(args)
    cfg = service.cfg
    print(f"Cerbero archivos protegidos en {cfg.base_url}  (panel: /panel, visor: /visor)")
    if is_loopback_host(cfg.host):
        print("Escucha sólo en loopback. Fuera del equipo hace falta HTTPS y una configuración de seguridad revisada.")
    else:
        print(f"AVISO: escucha en {cfg.host}, fuera de loopback. Usa HTTPS y una configuración de seguridad revisada.")
    uvicorn.run(create_app(service), host=cfg.host, port=cfg.port, proxy_headers=False, server_header=False,
                access_log=False, log_level="warning")


def cmd_export(args) -> None:
    doc, out = _service(args).export_path(args.owner, Path(args.source))
    print(f"Exportado {doc['display_name']} como {out} (documento {doc['id']}). El original no se modifica.")


def cmd_set_state(args) -> None:
    service = _service(args)
    doc = service.set_state(service.local_session(args.owner), args.doc_id, args.state, args.doc_id,
                            RequestContext(ip="local", ip_source="CLI"))
    print(f"{doc['container_name']}: {doc['state']}, efectivo desde {doc['effective_at']}. "
          "Las solicitudes nuevas de contenido se deniegan.")


def cmd_outbox(args) -> None:
    print(_service(args).process_outbox())


def cmd_mailbox(args) -> None:
    from .mail import read_mailbox, start_mailbox

    directory = Path(args.dir)
    if args.list:
        for path, message in read_mailbox(directory):
            print(f"--- {path.name}\nDe: {message['From']}\nPara: {message['To']}\nAsunto: {message['Subject']}\n"
                  f"Fecha: {message['Date']}\n\n{message.get_content().strip()}\n")
        return
    controller = start_mailbox(directory, args.host, args.port)
    print(f"Buzón SMTP de pruebas en {args.host}:{args.port}; guarda los mensajes en {directory}. Ctrl+C para salir.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()


def cmd_demo(args) -> None:
    from .demo import run_demo

    run_demo(Path(args.out), fresh=args.fresh, keep_running=args.keep_running, simulated_geo=args.geo_simulado)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m cerbero_pf", description="Archivos protegidos de Cerbero (prototipo local)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("genkey", help="crea la clave maestra (nunca sobrescribe)")
    p.add_argument("--config", required=True)
    p.set_defaults(func=cmd_genkey)

    p = sub.add_parser("create-user", help="crea una cuenta con contraseña aleatoria o tomada de una variable")
    p.add_argument("--config", required=True)
    p.add_argument("username")
    p.add_argument("--email", help="correo para avisos")
    p.add_argument("--display-name")
    p.add_argument("--password-env", help="variable de entorno con la contraseña (mín. 12 caracteres)")
    p.set_defaults(func=cmd_create_user)

    p = sub.add_parser("serve", help="inicia el servicio")
    p.add_argument("--config", required=True)
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("export", help="exporta un archivo del área autorizada a .cerbero")
    p.add_argument("--config", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("source")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("set-state", help="marca extraviado o revoca sin iniciar sesión (acceso local de administración)")
    p.add_argument("--config", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("doc_id")
    p.add_argument("state", choices=("lost", "revoked"))
    p.set_defaults(func=cmd_set_state)

    p = sub.add_parser("outbox", help="procesa una vez la cola de correo")
    p.add_argument("--config", required=True)
    p.set_defaults(func=cmd_outbox)

    p = sub.add_parser("mailbox", help="buzón SMTP local de pruebas")
    p.add_argument("--dir", required=True)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8025)
    p.add_argument("--list", action="store_true", help="muestra los mensajes recibidos y sale")
    p.set_defaults(func=cmd_mailbox)

    p = sub.add_parser("demo", help="demo reproducible con datos sintéticos")
    p.add_argument("--out", default=str(Path(__file__).resolve().parents[2] / "out" / "protected_files_demo"))
    p.add_argument("--fresh", action="store_true", help="borra una demo anterior (sólo si tiene la marca de demo)")
    p.add_argument("--keep-running", action="store_true", help="deja servicio y buzón activos para el navegador")
    p.add_argument("--geo-simulado", action="store_true", help="caso aparte con proveedor geográfico SIMULADO")
    p.set_defaults(func=cmd_demo)

    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    try:
        args.func(args)
    except (ConfigError, MasterKeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ServiceError as exc:
        print(f"error: {exc.message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
