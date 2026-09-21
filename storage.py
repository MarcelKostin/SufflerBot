import json
import os
import threading
from datetime import datetime

APPLICATIONS_FILE = "applications.json"
MAPPING_FILE = "reply_mapping.json"

_lock = threading.Lock()


def _read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_application(data: dict) -> int:
    """Сохраняет заявку, возвращает её порядковый номер (id)."""
    with _lock:
        applications = _read_json(APPLICATIONS_FILE, [])
        app_id = len(applications) + 1
        record = {
            "id": app_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **data,
        }
        applications.append(record)
        _write_json(APPLICATIONS_FILE, applications)
        return app_id


def save_reply_mapping(admin_message_id: int, user_chat_id: int, user_name: str) -> None:
    """Запоминает, какому пользователю соответствует сообщение с заявкой в чате админа,
    чтобы Reply на это сообщение можно было переслать клиенту."""
    with _lock:
        mapping = _read_json(MAPPING_FILE, {})
        mapping[str(admin_message_id)] = {"chat_id": user_chat_id, "name": user_name}
        _write_json(MAPPING_FILE, mapping)


def get_user_by_admin_message(admin_message_id: int):
    mapping = _read_json(MAPPING_FILE, {})
    return mapping.get(str(admin_message_id))
