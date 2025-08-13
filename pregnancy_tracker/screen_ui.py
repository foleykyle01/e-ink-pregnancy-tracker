import time
import json
import os
from datetime import datetime
from PIL import Image, ImageDraw

from .icons import carriage_icon_path, moon_icon_path
from .fonts import create_font
from .gray_scale import WHITE, DARK_GRAY, BLACK, LIGHT_GRAY
from .size_data import get_size_for_week
from .developmental_milestones import get_milestone_for_week


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
        self.current_page = current_page  # 0=progress, 1=size, 2=appointments, 3=milestones
        self._img = Image.new('L', (self.width, self.height), 255)  # 255: clear the frame
        self._img_draw = ImageDraw.Draw(self._img)
        self._load_appointments()

    def _calculate_text_size(self, message, font):
        _, _, w, h = self._img_draw.textbbox((0, 0), message, font=font)
        return w, h

    def _draw_title(self):
        font = create_font(20)
        # For milestones page, show week-specific title
        if self.current_page == 3:
            week = self.pregnancy.get_pregnancy_week()
            title_str = f"Week {week} Milestones"
        else:
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
        # Draw "Coming Up" as the title instead of "New Foley Tracker"
        title_font = create_font(20)
        title_str = "Coming Up"
        w, h = self._calculate_text_size(title_str, title_font)
        pos = ((self.width-w)/2, self.TITLE_MARGIN_TOP)
        self._img_draw.text(pos, title_str, font=title_font, fill=BLACK)
        
        # Draw the decorative line
        _, title_h = self._calculate_text_size(title_str, title_font)
        line_y = self.TITLE_MARGIN_TOP + title_h + 6
        self._img_draw.line([(20, line_y), (self.width - 20, line_y)], fill=BLACK, width=2)
        
        # Get next appointment
        next_appointment = self._get_next_appointment()
        
        if next_appointment:
            # Parse and format date
            appt_date = datetime.strptime(next_appointment['date'], '%Y-%m-%d')
            date_str = appt_date.strftime('%b %d').upper()  # Shortened format like "AUG 15"
            
            # Draw date and time in larger font on same line (moved up for more room)
            datetime_font = create_font(24)
            datetime_str = f"{date_str} • {next_appointment['time']}"
            w, h = self._calculate_text_size(datetime_str, datetime_font)
            pos = ((self.width - w) / 2, line_y + 20)  # Moved up from +30
            self._img_draw.text(pos, datetime_str, font=datetime_font, fill=BLACK)
            
            # Draw appointment type with text wrapping if needed
            type_font = create_font(16)  # Slightly smaller for better fit
            type_text = next_appointment['type'].upper()
            
            # Check if text needs wrapping
            max_width = self.width - 30  # Reduced margins for more text space
            w, h = self._calculate_text_size(type_text, type_font)
            
            type_y = line_y + 50  # Moved up from +65 for more room
            
            if w > max_width:
                # Text too long, wrap it
                words = type_text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    test_w, _ = self._calculate_text_size(test_line, type_font)
                    if test_w <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                # Draw each line centered
                for i, line in enumerate(lines[:3]):  # Increased to max 3 lines
                    line_w, line_h = self._calculate_text_size(line, type_font)
                    pos = ((self.width - line_w) / 2, type_y + i * 22)
                    self._img_draw.text(pos, line, font=type_font, fill=BLACK)
            else:
                # Text fits, draw normally
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
    
    def _draw_milestones_page(self):
        """Draw developmental milestones page"""
        title_font = create_font(20)
        _, title_h = self._calculate_text_size("New Foley Progress", title_font)
        
        # Line is already drawn in main draw() method
        line_y = self.TITLE_MARGIN_TOP + title_h + 6
        
        # Get milestone info for current week
        week = self.pregnancy.get_pregnancy_week()
        milestone = get_milestone_for_week(week)
        
        # Draw weight
        weight_label_font = create_font(11)
        weight_label = "WEIGHT"
        w, h = self._calculate_text_size(weight_label, weight_label_font)
        pos = ((self.width - w) / 2, line_y + 20)
        self._img_draw.text(pos, weight_label, font=weight_label_font, fill=LIGHT_GRAY)
        
        weight_font = create_font(16)
        weight_text = milestone['weight']
        w, h = self._calculate_text_size(weight_text, weight_font)
        pos = ((self.width - w) / 2, line_y + 38)
        self._img_draw.text(pos, weight_text, font=weight_font, fill=BLACK)
        
        # Draw development info with text wrapping
        dev_label_font = create_font(11)
        dev_label = "DEVELOPMENT"
        w, h = self._calculate_text_size(dev_label, dev_label_font)
        pos = ((self.width - w) / 2, line_y + 70)
        self._img_draw.text(pos, dev_label, font=dev_label_font, fill=LIGHT_GRAY)
        
        # Wrap development text if needed - smaller font for better fit
        dev_font = create_font(13)
        dev_text = milestone["development"]
        max_width = self.width - 16  # 8px margin on each side
        
        # Split text into lines that fit
        words = dev_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_w, _ = self._calculate_text_size(test_line, dev_font)
            if test_w <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw development text lines (max 4 lines to fit screen)
        dev_y = line_y + 88
        line_spacing = 16  # Reduced spacing between lines
        for i, line in enumerate(lines[:4]):  # Increased to 4 lines
            line_w, line_h = self._calculate_text_size(line, dev_font)
            pos = ((self.width - line_w) / 2, dev_y + i * line_spacing)
            self._img_draw.text(pos, line, font=dev_font, fill=BLACK)

    def _draw_page_indicators(self, current_page):
        """Draw page indicator dots at the bottom - DISABLED"""
        # Page indicators removed since we're using buttons now
        pass

    def draw(self):
        # Clear the image to ensure no overlap
        self._img = Image.new('L', (self.width, self.height), 255)
        self._img_draw = ImageDraw.Draw(self._img)
        
        # Draw title and decorative line for pages except appointments
        if self.current_page != 2:
            self._draw_title()
            
            # Draw decorative line under title
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
            # Appointments screen (has its own title)
            self._draw_appointments_page()
        elif self.current_page == 3:
            # Milestones screen
            self._draw_milestones_page()
        
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