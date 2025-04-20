# Telegram CRM Bot

A professional Telegram bot designed for handyman and home service businesses. Built using `aiogram` and deployed on Railway, this bot helps manage customer requests directly from Telegram.

## 🚀 Features

- Multilingual support: 🇷🇺 Russian and 🇺🇸 English
- Step-by-step request collection: name, phone, address, description, media
- Request status control via inline buttons:
  - 🔄 In Progress
  - ✅ Done
  - 🗑 Delete
- Admin notification in a Telegram group with full request info
- Media support: images and video
- Unique request IDs with timestamps
- Clean message formatting and error handling

## 🧰 Built With

- Python 3.10+
- [aiogram](https://docs.aiogram.dev/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- Railway for deployment

## 📁 Files

- `bot.py`: Main bot logic (handlers, media, status)
- `db.py`: (reserved for future storage)
- `get_group_id.py`: Helper script to retrieve group ID
- `Procfile`: Entry point for Railway
- `requirements.txt`: Dependency list

## ⚙️ Deployment

This bot is deployed using [Railway](https://railway.app/).

1. Connect to GitHub
2. Add `.env` variable `BOT_TOKEN`
3. Click **Deploy**
4. Enjoy automation 🎉

## 📷 Preview

This bot is running on [@ChicagoHandymanBot](https://t.me/ChicagoHandymanBot)

## 📞 Support

For business inquiries or questions: `Chicago Handyman Services` Telegram group.

---

> Made with ❤️ by DesmondBD