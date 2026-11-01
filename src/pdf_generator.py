from fpdf import FPDF
import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_REGULAR = os.path.join(BASE_DIR, 'DejaVuSans.ttf')
FONT_BOLD = os.path.join(BASE_DIR, 'DejaVuSans-Bold.ttf')


class ReceiptPDF(FPDF):
    def header(self):
        # Этот метод срабатывает при вызове add_page()
        self.set_font('DejaVu', 'B', 20)
        self.set_text_color(200, 0, 0)
        self.cell(0, 10, 'КАВЕР-ГРУППА "ЖАРА"', border=False, align='C')
        self.ln(15)


def generate_receipt(user_name, event_date, songs_list, total_time, total_price):
    pdf = ReceiptPDF()

    # 1. СНАЧАЛА РЕГИСТРИРУЕМ ШРИФТЫ!
    pdf.add_font('DejaVu', '', FONT_REGULAR)
    pdf.add_font('DejaVu', 'B', FONT_BOLD)

    # 2. И ТОЛЬКО ПОТОМ ДОБАВЛЯЕМ СТРАНИЦУ (это вызовет header, и он найдет шрифт)
    pdf.add_page()

    # Основной текст
    pdf.set_font('DejaVu', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f'Дата создания: {datetime.date.today().strftime("%d.%m.%Y")}', align='R')
    pdf.ln(10)

    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Детали заказа:', ln=True)

    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 8, f'Клиент: {user_name}', ln=True)
    pdf.cell(0, 8, f'Дата мероприятия: {event_date}', ln=True)
    pdf.ln(5)

    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Выбранный сет-лист:', ln=True)

    pdf.set_font('DejaVu', '', 12)
    for song in songs_list.split(", "):
        pdf.cell(0, 8, f'- {song}', ln=True)
    pdf.ln(5)

    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Итого:', ln=True)

    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 8, f'Общее время: {round(total_time, 1)} мин.', ln=True)
    pdf.cell(0, 8, f'Стоимость: {total_price} руб.', ln=True)

    pdf.ln(10)
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Спасибо, что выбираете нас! Менеджер свяжется с вами.', align='C')

    filename = os.path.join(BASE_DIR, f"receipt_{int(datetime.datetime.now().timestamp())}.pdf")
    pdf.output(filename)
    return filename
