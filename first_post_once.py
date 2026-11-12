"""Send one real introductory VK post and preserve its ID to prevent repeats."""
import logging
from datetime import datetime, timezone
from main import GROUP_ID, history_load, history_save, format_message, post_vk, slot

POST_KEY = "krasnodar_welcome_first_2026"
DRAFT = {
    "publish": True,
    "sentence": "🌴 Братва, «Чёткий Краснодар» на связи — кто из какого района, пишите в комменты!",
    "hashtags": ["#КраснодарНаСвязи", "#КраснодарЗнакомимся", "#КраснодарНашЧат"]
}


def main():
    now = datetime.now(timezone.utc)
    current_slot = slot(now)
    history = history_load()
    if any(p.get("game_key") == POST_KEY for p in history["posts"]):
        logging.info("Приветственный пост уже опубликован. Повтор не нужен.")
        return
    if any(p.get("slot") == current_slot for p in history["posts"]):
        logging.info("Этот 48-минутный слот уже занят — не создаём второй пост.")
        return
    if sum(str(p.get("slot", "")).startswith(current_slot[:10]) for p in history["posts"]) >= 30:
        logging.info("Достигнут лимит 30 постов.")
        return
    message = format_message(DRAFT, history)
    if message is None:
        raise RuntimeError("Неверный формат поста или хэштеги уже использованы")
    post_id = post_vk(message, "one-time-welcome-krasnodar-2026")
    history["posts"].append({
        "slot": current_slot, "post_id": post_id, "kind": "game", "game_key": POST_KEY,
        "title": "Приветственный пост и знакомство", "text": DRAFT["sentence"],
        "published_at": now.isoformat()
    })
    history["used_tags"].extend(DRAFT["hashtags"])
    history_save(history)
    logging.info("ПЕРВЫЙ ПОСТ ОПУБЛИКОВАН: https://vk.com/wall-%s_%s", GROUP_ID, post_id)


if __name__ == "__main__":
    main()
