"""Adaptador SMTP y buzón local de pruebas.

El adaptador sólo informa éxito cuando el servidor SMTP aceptó el mensaje para el destinatario;
encolar no es enviar. El buzón local (aiosmtpd) guarda cada mensaje recibido como `.eml`.
"""
from __future__ import annotations

import itertools
import os
import smtplib
import ssl
import time
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import formatdate, make_msgid
from pathlib import Path

from .config import SmtpConfig, is_loopback_host


class SmtpSender:
    def __init__(self, cfg: SmtpConfig):
        self.cfg = cfg

    def send(self, recipient: str, subject: str, body: str) -> None:
        message = EmailMessage(policy=policy.SMTP)
        message["From"] = self.cfg.sender
        message["To"] = recipient
        message["Subject"] = subject
        message["Date"] = formatdate(usegmt=True)
        message["Message-ID"] = make_msgid(domain="cerbero-pf.invalid")
        message.set_content(body)
        client = smtplib.SMTP(self.cfg.host, self.cfg.port, timeout=self.cfg.timeout_seconds)
        try:
            if self.cfg.starttls:
                client.starttls(context=ssl.create_default_context())
            if self.cfg.username:
                client.login(self.cfg.username, os.environ.get(self.cfg.password_env, ""))
            refused = client.send_message(message)
        finally:
            try:  # un QUIT fallido tras aceptar DATA no convierte un envío aceptado en fallo
                client.quit()
            except (smtplib.SMTPException, OSError):
                client.close()
        if refused:
            raise smtplib.SMTPRecipientsRefused(refused)


class _SaveHandler:
    def __init__(self, directory: Path):
        self.directory = directory
        self.counter = itertools.count(1)

    async def handle_DATA(self, server, session, envelope):  # noqa: N802 (API de aiosmtpd)
        name = f"{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}-{os.getpid()}-{next(self.counter):04d}.eml"
        with open(self.directory / name, "xb") as handle:
            handle.write(envelope.original_content or envelope.content)
        return "250 Message accepted for delivery"


def start_mailbox(directory: Path, host: str = "127.0.0.1", port: int = 8025):
    """Arranca un buzón SMTP local (sólo loopback). Devuelve el controlador; llama a `.stop()` al terminar."""
    from aiosmtpd.controller import Controller

    if not is_loopback_host(host):
        raise ValueError("el buzón de pruebas sólo escucha en loopback")
    directory.mkdir(parents=True, exist_ok=True)
    controller = Controller(_SaveHandler(directory), hostname=host, port=port)
    controller.start()
    return controller


def read_mailbox(directory: Path) -> list[tuple[Path, EmailMessage]]:
    messages = []
    for path in sorted(Path(directory).glob("*.eml")):
        with path.open("rb") as handle:
            messages.append((path, BytesParser(policy=policy.default).parse(handle)))
    return messages
