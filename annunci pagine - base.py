import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Configurazione del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Definizioni degli stati della conversazione
TITOLO, DESCRIZIONE, PREZZO, CONFERMA = range(4)

# Dizionario per memorizzare i dati dell'annuncio
annuncio_data = {}

# Gestore del comando /start e /nuovo_annuncio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        logger.info("Comando /start o /nuovo_annuncio ricevuto.")
        await update.message.reply_text("Ok, iniziamo a creare il tuo annuncio. Inserisci il titolo:")
        return TITOLO
    except Exception as e:
        logger.error(f"Errore in start: {e}")
        await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
        return ConversationHandler.END

# Gestore per l'input del titolo
async def get_titolo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        logger.info("get_titolo chiamato.")
        titolo = update.message.text
        logger.info(f"Titolo ricevuto: {titolo}")
        annuncio_data['titolo'] = titolo
        await update.message.reply_text(f"Ottimo, il titolo è: {titolo}\nOra inserisci la descrizione:")
        return DESCRIZIONE
    except Exception as e:
        logger.error(f"Errore in get_titolo: {e}")
        await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
        return ConversationHandler.END

# Gestore per l'input della descrizione
async def get_descrizione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        logger.info("get_descrizione chiamato.")
        descrizione = update.message.text
        annuncio_data['descrizione'] = descrizione
        await update.message.reply_text(f"Bene, la descrizione è:\n{descrizione}\nOra inserisci il prezzo (o scrivi 'nessuno'):")
        return PREZZO
    except Exception as e:
        logger.error(f"Errore in get_descrizione: {e}")
        await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
        return ConversationHandler.END

# Gestore per l'input del prezzo
async def get_prezzo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        prezzo = update.message.text
        if prezzo.lower() != 'nessuno':
            try:
                prezzo = float(prezzo)
                annuncio_data['prezzo'] = prezzo
            except ValueError:
                await update.message.reply_text("Prezzo non valido. Inserisci un numero o 'nessuno'.")
                return PREZZO
        else:
            annuncio_data['prezzo'] = 'Non specificato'
        await update.message.reply_text(f"Il prezzo è: {annuncio_data['prezzo']}\nConfermi la pubblicazione dell'annuncio? (sì/no)")
        return CONFERMA
    except Exception as e:
        logger.error(f"Errore in get_prezzo: {e}")
        await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
        return ConversationHandler.END

# Gestore per la conferma della pubblicazione
async def conferma_pubblicazione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        risposta = update.message.text.lower()  # Converti in minuscolo
        if risposta == 'sì' or risposta == 'si':  # Accetta "sì", "si", "Sì", "Si"
            try:
                GRUPPO_ID = int(-numero)  # Sostituisci con l'ID del tuo gruppo
                messaggio_pubblicazione = f"**NUOVO ANNUNCIO**\n\n**Titolo:** {annuncio_data['titolo']}\n**Descrizione:** {annuncio_data['descrizione']}\n**Prezzo:** {annuncio_data.get('prezzo', 'Non specificato')}"
                await context.bot.send_message(chat_id=GRUPPO_ID, text=messaggio_pubblicazione, parse_mode='Markdown')
                await update.message.reply_text("Annuncio pubblicato con successo!")
            except Exception as e:
                logger.error(f"Errore durante la pubblicazione dell'annuncio: {e}")
                await update.message.reply_text("Errore durante la pubblicazione dell'annuncio. Riprova più tardi.")
        else:
            await update.message.reply_text("Operazione annullata.")
        annuncio_data.clear()
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Errore in conferma_pubblicazione: {e}")
        await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
        return ConversationHandler.END

# Gestore per l'annullamento della conversazione
async def annulla(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        await update.message.reply_text("Operazione annullata.")
        annuncio_data.clear()
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Errore in annulla: {e}")
        await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
        return ConversationHandler.END

def main() -> None:
    TOKEN = ""  # Sostituisci con il tuo token del bot
    application = Application.builder().token(TOKEN).build()

    # Gestore della conversazione
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("nuovo_annuncio", start)],
        states={
            TITOLO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_titolo)],
            DESCRIZIONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_descrizione)],
            PREZZO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_prezzo)],
            CONFERMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, conferma_pubblicazione)],
        },
        fallbacks=[CommandHandler("annulla", annulla)],
    )

    # Aggiunta dei gestori
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))  # Gestore per /start
    application.add_handler(CommandHandler("nuovo_annuncio", start))  # Gestore per /nuovo_annuncio

    # Avvio del bot
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione del bot: {e}")

if __name__ == "__main__":
    main()
