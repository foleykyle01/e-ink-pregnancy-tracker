import time
import json
import os
from datetime import datetime
from PIL import Image, ImageDraw

from .icons import carriage_icon_path, moon_icon_path
from .fonts import create_font
from .gray_scale import WHITE, DARK_GRAY, BLACK, LIGHT_GRAY
from .size_data import get_size_for_week


class ScreenUI:
    ICON_SIZE = 20
    ICON_CIRCLE_SIZE = 40
    ICON_X_MARGIN = 8
    PROGRESS_BAR_Y_CENTER = 105
    PROGRESS_BAR_HEIGHT = 10
    TEXT_MARGIN_TOP = 16
    TEXT_MARGIN_BOTTOM = 16
    TITLE_MARGIN_TOP = 8
    PAGE_DOTS_MARGIN_BOTTOM = 8
    PAGE_DOT_SIZE = 6
    PAGE_DOT_SPACING = 12

    def __init__(self, width, height, pregnancy, current_page=0):
        self.pregnancy = pregnancy
        self.width = width
        self.height = height
        self.current_page = current_page  # 0=progress, 1=size, 2=appointments, 3=baby info
        self._img = Image.new('L', (self.width, self.height), 255)  # 255: clear the frame
        self._img_draw = ImageDraw.Draw(self._img)
        self._load_appointments()

    def _calculate_text_size(self, message, font):
        _, _, w, h = self._img_draw.textbbox((0, 0), message, font=font)
        return w, h

    def _draw_title(self):
        font = create_font(20)
        title_str = "New Foley Tracker"
        w, h = self._calculate_text_size(title_str, font)
        pos = ((self.width-w)/2, self.TITLE_MARGIN_TOP)
        self._img_draw.text(pos, title_str, font=font, fill=BLACK)

    def _draw_percent(self):
        font = create_font(36)
        percent_str = self.pregnancy.get_percent_str()
        w, h = self._calculate_text_size(percent_str, font)
        title_font = create_font(20)
        _, title_h = self._calculate_text_size("New Foley Progress", title_font)
        # Adjust position to account for the decorative line
        pos = ((self.width-w)/2, self.TITLE_MARGIN_TOP + title_h + 18)
        self._img_draw.text(pos, percent_str, font=font, fill=BLACK)

    def _draw_weekday(self):
        font = create_font(30)
        percent_str = self.pregnancy.get_weekday_str()
        w, h = self._calculate_text_size(percent_str, font)
        pos = ((self.width-w)/2, (self.height-h-self.TEXT_MARGIN_BOTTOM))
        self._img_draw.text(pos, percent_str, font=font, fill=BLACK)

    def _draw_carriage(self):
        carriage = Image.open(carriage_icon_path)
        carriage.convert("1")
        circle_y1 = int(self.PROGRESS_BAR_Y_CENTER - self.ICON_CIRCLE_SIZE/2)
        circle_y2 = circle_y1 + self.ICON_CIRCLE_SIZE
        circle_x1 = self.width - self.ICON_CIRCLE_SIZE - self.ICON_X_MARGIN
        circle_x2 = self.width - self.ICON_X_MARGIN
        self._img_draw.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=DARK_GRAY)

        icon_x = int(circle_x1 + (self.ICON_CIRCLE_SIZE - carriage.width)/2)
        icon_y = int(circle_y1 + (self.ICON_CIRCLE_SIZE - carriage.height)/2)
        self._img.paste(carriage, (icon_x, icon_y), carriage)

    def _draw_moon(self):
        moon = Image.open(moon_icon_path)
        moon.convert("1")
        circle_y1 = int(self.PROGRESS_BAR_Y_CENTER - self.ICON_CIRCLE_SIZE/2)
        circle_y2 = circle_y1 + self.ICON_CIRCLE_SIZE
        circle_x1 = self.ICON_X_MARGIN
        circle_x2 = circle_x1 + self.ICON_CIRCLE_SIZE
        self._img_draw.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=LIGHT_GRAY)

        icon_x = int(circle_x1 + (self.ICON_CIRCLE_SIZE - moon.width)/2)
        icon_y = int(circle_y1 + (self.ICON_CIRCLE_SIZE - moon.height)/2)
        self._img.paste(moon, (icon_x, icon_y), moon)

    def _draw_progress_bar_mid(self):
        self._draw_progress_done()
        self._draw_progress_remaining()
        self._draw_progress_circle()

    def _draw_progress_bar(self):
        self._draw_moon()
        self._draw_progress_bar_mid()
        self._draw_carriage()

    def _load_appointments(self):
        """Load appointments from JSON file"""
        try:
            appointments_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                'appointments.json'
            )
            with open(appointments_path, 'r') as f:
                data = json.load(f)
                self.appointments = data.get('appointments', [])
        except Exception as e:
            self.appointments = []
    
    def set_page(self, page_num):
        """Set the current page (0-3)"""
        if 0 <= page_num <= 3:
            self.current_page = page_num

    def _draw_size_comparison(self):
        """Draw the size comparison screen with two-column layout"""
        week = self.pregnancy.get_pregnancy_week()
        size_comparison, size_length = get_size_for_week(week)
        
        title_font = create_font(20)
        _, title_h = self._calculate_text_size("New Foley Progress", title_font)
        
        # Line is already drawn in main draw() method
        line_y = self.TITLE_MARGIN_TOP + title_h + 6
        
        # Define column positions
        left_column_x = self.width * 0.25  # 25% from left
        right_column_x = self.width * 0.75  # 75% from left
        content_start_y = line_y + 20
        
        # LEFT COLUMN - Week information
        # Draw week label (bigger, darker)
        week_label_font = create_font(18)  # Increased from 14
        week_label = "WEEK"
        w, h = self._calculate_text_size(week_label, week_label_font)
        pos = (left_column_x - w/2, content_start_y)
        self._img_draw.text(pos, week_label, font=week_label_font, fill=BLACK)  # Changed to BLACK
        
        # Draw week number (large, bold)
        week_num_font = create_font(60)  # Increased from 54
        week_num_str = str(week)
        w, h = self._calculate_text_size(week_num_str, week_num_font)
        pos = (left_column_x - w/2, content_start_y + 22)
        self._img_draw.text(pos, week_num_str, font=week_num_font, fill=BLACK)
        
        # Draw vertical divider line
        divider_x = self.width / 2
        self._img_draw.line(
            [(divider_x, content_start_y), (divider_x, content_start_y + 90)],  # Extended line
            fill=BLACK, 
            width=2
        )
        
        # RIGHT COLUMN - Size information
        # Draw "Baby size" label
        size_label_font = create_font(16)  # Increased from 11
        size_label = "BABY SIZE"
        w, h = self._calculate_text_size(size_label, size_label_font)
        pos = (right_column_x - w/2, content_start_y)
        self._img_draw.text(pos, size_label, font=size_label_font, fill=BLACK)  # Changed to BLACK
        
        # Draw size comparison
        size_str = size_comparison.upper()
        
        # Dynamically adjust font size based on text length (all increased)
        if len(size_str) > 14:
            size_font = create_font(20)  # Increased from 14
        elif len(size_str) > 10:
            size_font = create_font(22)  # Increased from 16
        else:
            size_font = create_font(24)  # Increased from 18
        
        # Check if we need to break into two lines
        w, h = self._calculate_text_size(size_str, size_font)
        max_width = (self.width / 2) - 20  # Maximum width for right column
        
        if w > max_width and ' ' in size_comparison:
            # Break into two lines
            words = size_comparison.split()
            if len(words) == 2:
                line1 = words[0].upper()
                line2 = words[1].upper()
            else:
                mid = len(words) // 2
                line1 = ' '.join(words[:mid]).upper()
                line2 = ' '.join(words[mid:]).upper()
            
            w1, h1 = self._calculate_text_size(line1, size_font)
            w2, h2 = self._calculate_text_size(line2, size_font)
            
            pos1 = (right_column_x - w1/2, content_start_y + 22)
            pos2 = (right_column_x - w2/2, content_start_y + 44)
            
            self._img_draw.text(pos1, line1, font=size_font, fill=BLACK)
            self._img_draw.text(pos2, line2, font=size_font, fill=BLACK)
            
            length_y = content_start_y + 68
        else:
            # Single line
            w, h = self._calculate_text_size(size_str, size_font)
            pos = (right_column_x - w/2, content_start_y + 30)
            self._img_draw.text(pos, size_str, font=size_font, fill=BLACK)
            length_y = content_start_y + 56
        
        # Draw length (bigger and darker)
        length_font = create_font(18)  # Increased from 14
        w, h = self._calculate_text_size(size_length, length_font)
        pos = (right_column_x - w/2, length_y)
        self._img_draw.text(pos, size_length, font=length_font, fill=BLACK)  # Changed to BLACK
    
    def _draw_appointments_page(self):
        """Draw the appointments page showing next upcoming appointment"""
        title_font = create_font(20)
        _, title_h = self._calculate_text_size("New Foley Progress", title_font)
        
        # Line is already drawn in main draw() method
        line_y = self.TITLE_MARGIN_TOP + title_h + 6
        
        # Get next appointment
        next_appointment = self._get_next_appointment()
        
        if next_appointment:
            # Draw "COMING UP" header with better spacing
            header_font = create_font(16)
            header_text = "COMING UP"
            w, h = self._calculate_text_size(header_text, header_font)
            pos = ((self.width - w) / 2, line_y + 20)
            self._img_draw.text(pos, header_text, font=header_font, fill=DARK_GRAY)
            
            # Parse and format date
            appt_date = datetime.strptime(next_appointment['date'], '%Y-%m-%d')
            date_str = appt_date.strftime('%b %d').upper()  # Shortened format like "AUG 15"
            
            # Draw date and time in larger font on same line
            datetime_font = create_font(24)
            datetime_str = f"{date_str} • {next_appointment['time']}"
            w, h = self._calculate_text_size(datetime_str, datetime_font)
            pos = ((self.width - w) / 2, line_y + 48)
            self._img_draw.text(pos, datetime_str, font=datetime_font, fill=BLACK)
            
            # Draw appointment type in a box-like style
            type_font = create_font(18)
            type_text = next_appointment['type'].upper()
            w, h = self._calculate_text_size(type_text, type_font)
            
            # Draw a rounded rectangle background for the type
            type_y = line_y + 85
            rect_padding = 10
            rect_x1 = (self.width - w) / 2 - rect_padding
            rect_y1 = type_y - 3
            rect_x2 = (self.width + w) / 2 + rect_padding
            rect_y2 = type_y + h + 3
            
            # Draw the type text
            pos = ((self.width - w) / 2, type_y)
            self._img_draw.text(pos, type_text, font=type_font, fill=BLACK)
        else:
            # No appointments message
            no_appt_font = create_font(18)
            no_appt_text = "No upcoming appointments"
            w, h = self._calculate_text_size(no_appt_text, no_appt_font)
            pos = ((self.width - w) / 2, (self.height - h) / 2)
            self._img_draw.text(pos, no_appt_text, font=no_appt_font, fill=BLACK)
    
    def _get_next_appointment(self):
        """Get the next upcoming appointment"""
        if not self.appointments:
            return None
        
        today = datetime.now().date()
        future_appointments = []
        
        for appt in self.appointments:
            try:
                appt_date = datetime.strptime(appt['date'], '%Y-%m-%d').date()
                if appt_date >= today:
                    future_appointments.append(appt)
            except:
                continue
        
        # Sort by date and return the first one
        if future_appointments:
            future_appointments.sort(key=lambda x: x['date'])
            return future_appointments[0]
        
        return None
    
    def _draw_baby_info_page(self):
        """Draw baby information page in two columns"""
        title_font = create_font(20)
        _, title_h = self._calculate_text_size("New Foley Progress", title_font)
        
        # Line is already drawn in main draw() method
        line_y = self.TITLE_MARGIN_TOP + title_h + 6
        
        # Get current info
        week = self.pregnancy.get_pregnancy_week()
        days_left = self.pregnancy.get_days_until_due_date()
        trimester = "First" if week <= 13 else "Second" if week <= 27 else "Third"
        progress = self.pregnancy.get_percent_str()
        
        # Define column positions
        left_column_x = self.width * 0.25  # 25% from left
        right_column_x = self.width * 0.75  # 75% from left
        content_start_y = line_y + 25
        
        # LEFT COLUMN
        # Week label
        label_font = create_font(14)
        week_label = "WEEK"
        w, h = self._calculate_text_size(week_label, label_font)
        pos = (left_column_x - w/2, content_start_y)
        self._img_draw.text(pos, week_label, font=label_font, fill=DARK_GRAY)
        
        # Week number
        num_font = create_font(42)
        week_str = str(week)
        w, h = self._calculate_text_size(week_str, num_font)
        pos = (left_column_x - w/2, content_start_y + 20)
        self._img_draw.text(pos, week_str, font=num_font, fill=BLACK)
        
        # Trimester below week
        trim_font = create_font(12)
        w, h = self._calculate_text_size(trimester, trim_font)
        pos = (left_column_x - w/2, content_start_y + 65)
        self._img_draw.text(pos, trimester, font=trim_font, fill=BLACK)
        
        # Draw vertical divider
        divider_x = self.width / 2
        self._img_draw.line(
            [(divider_x, content_start_y), (divider_x, content_start_y + 85)],
            fill=BLACK, 
            width=2
        )
        
        # RIGHT COLUMN
        # Days left label
        days_label = "DAYS LEFT"
        w, h = self._calculate_text_size(days_label, label_font)
        pos = (right_column_x - w/2, content_start_y)
        self._img_draw.text(pos, days_label, font=label_font, fill=DARK_GRAY)
        
        # Days number
        days_str = str(days_left)
        w, h = self._calculate_text_size(days_str, num_font)
        pos = (right_column_x - w/2, content_start_y + 20)
        self._img_draw.text(pos, days_str, font=num_font, fill=BLACK)
        
        # Progress below days
        w, h = self._calculate_text_size(progress, trim_font)
        pos = (right_column_x - w/2, content_start_y + 65)
        self._img_draw.text(pos, progress, font=trim_font, fill=BLACK)

    def _draw_page_indicators(self, current_page):
        """Draw page indicator dots at the bottom - DISABLED"""
        # Page indicators removed since we're using buttons now
        pass

    def draw(self):
        # Clear the image to ensure no overlap
        self._img = Image.new('L', (self.width, self.height), 255)
        self._img_draw = ImageDraw.Draw(self._img)
        
        self._draw_title()
        
        # Draw decorative line under title for all pages
        title_font = create_font(20)
        _, title_h = self._calculate_text_size("New Foley Progress", title_font)
        line_y = self.TITLE_MARGIN_TOP + title_h + 6
        self._img_draw.line([(20, line_y), (self.width - 20, line_y)], fill=BLACK, width=2)
        
        if self.current_page == 0:
            # Progress screen
            self._draw_percent()
            self._draw_weekday()
            self._draw_progress_bar()
        elif self.current_page == 1:
            # Size comparison screen
            self._draw_size_comparison()
        elif self.current_page == 2:
            # Appointments screen
            self._draw_appointments_page()
        elif self.current_page == 3:
            # Baby info screen
            self._draw_baby_info_page()
        
        self._draw_page_indicators(self.current_page)
        return self._img

    def _draw_progress_done(self):
        y1 = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT/2)
        y2 = y1 + self.PROGRESS_BAR_HEIGHT
        x1 = self.ICON_X_MARGIN + self.ICON_CIRCLE_SIZE
        x2 = self._get_progress_bar_mid_x_point()
        self._img_draw.rectangle((x1, y1, x2, y2), fill=LIGHT_GRAY)

    def _draw_progress_remaining(self):
        y1 = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT/2)
        y2 = y1 + self.PROGRESS_BAR_HEIGHT
        x1 = self._get_progress_bar_mid_x_point()
        x2 = self.width - self.ICON_X_MARGIN - self.ICON_CIRCLE_SIZE
        self._img_draw.rectangle((x1, y1, x2, y2), fill=DARK_GRAY)

    def _draw_progress_circle(self):
        mid_x = self._get_progress_bar_mid_x_point()
        mid_y = self.PROGRESS_BAR_Y_CENTER
        size = self.PROGRESS_BAR_HEIGHT
        pos = (mid_x-size/2, mid_y-size/2, mid_x+size/2, mid_y+size/2)
        self._img_draw.ellipse(pos, fill=LIGHT_GRAY)

    def _get_progress_bar_length(self):
        return self.width - 2*self.ICON_X_MARGIN - 2*self.ICON_CIRCLE_SIZE

    def _get_progress_bar_mid_x_point(self):
        offset = self.ICON_X_MARGIN + self.ICON_CIRCLE_SIZE
        return offset + self._get_progress_bar_length()*self.pregnancy.get_progress()