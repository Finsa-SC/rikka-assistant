import imaplib, email, time

from logger import get_logger
from .event_queue import event_queue
from config import config

logger = get_logger("EmailWatcher")

def process_new_email(mail, last_uid: int):
    status, data = mail.uid(
        "search",
        None,
        f"UID {last_uid + 1}:*"
    )
    if status != "OK":
        logger.error("Failed to search new email")
        return last_uid

    for uid in data[0].split():
        status, msg_data = mail.uid(
            'fetch',
            uid,
            "(RFC822)"
        )

        if status != "OK":
            logger.error(f"Failed to fetch email {uid}")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        sender = msg.get("From")
        subject = msg.get("Subject")
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)

                    if payload:
                        body = payload.decode(
                            errors="replace"
                        )
                    break
        else:
            payload = msg.get_payload(decode=True)

            if payload:
                body = payload.decode(
                    errors="replace"
                )

        event = {
            "type": "email_received",
            'severity': 'info',
            "data": {
                "from": sender,
                "subject": subject,
                "body": body,
            }
        }

        logger.info(
            f"New email: {sender} | {subject}"
        )

        event_queue.put(
            f"[SYSTEM_MESSAGE]\n{event}")

        last_uid = int(uid)

    return last_uid

def email_watcher():
    mail = imaplib.IMAP4_SSL(
        config.email_host,
        config.email_port
    )

    mail.login(
        config.email_user,
        config.email_password
    )

    mail.select("INBOX")

    logger.info("Email watcher connected")

    status, data = mail.uid(
        'search',
        None,
        'ALL'
    )

    if status != "OK":
        logger.error("Failed to get latest email UID")
        return

    uids = data[0].split()
    if uids:
        last_uid = int(uids[-1])
    else:
        last_uid = 0

    logger.info(f"Starting from UID {last_uid}")

    while True:
        try:
            tag = mail._new_tag()
            mail.send(tag + b" IDLE\r\n")

            response = mail.readline()

            if not response.startswith(b"+"):
                logger.error(f"Failed to enter IDLE: {response}")
                continue
            logger.info("Waiting for new email.")

            response = mail.readline()

            logger.info(f"IMAP event: {response!r}")

            mail.send(b"DONE\r\n")
            mail.readline()

            last_uid = process_new_email(mail, last_uid)

        except Exception as e:
            logger.error(f"Email watcher error: {e}")

            try:
                mail.logout()
            except Exception:
                ...

            time.sleep(10)

            ## Reconnect
            mail = imaplib.IMAP4_SSL(
                config.email_host,
                config.email_port,
            )

            mail.login(
                config.email_user,
                config.email_password,
            )

            mail.select("INBOX")
